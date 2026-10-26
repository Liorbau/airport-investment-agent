"""Runs the brief's sample questions against the real agent and checks each answer with code."""

import json

from app.modules.chat.agent import run
from app.modules.chat.schemas import Answer, ChatMessage
from app.modules.rankings.service import KPI_SORTS

RANK, DETAILS = "rank_airports", "airport_details"
CASES = [
    ("Which airports in New England are strong candidates for terminal expansion?", RANK, ["BGR"]),
    ("Compare LA and Santa Ana airport congestion levels.", DETAILS, ["LAX", "SNA"]),
    ("What is the percentage of long haul flights out of Anchorage airport?", DETAILS, ["12.3"]),
    ("What is the unmet flight demand in SFO airport and why?", DETAILS, ["36.0"]),
    ("What is the best airport to invest in across the whole US?", RANK, ["ORD"]),
    ("Which East Coast airports are the best opportunities?", RANK, []),
    ("Tell me about PWM.", DETAILS, ["PWM"]),
    ("What is the airport with the most long haul flights across the US?", RANK, ["JFK"]),
    ("Which airports grew the most in passengers?", RANK, ["ORD"]),
    ("Which US airport has the lowest load factor?", RANK, []),
]
KPI_COLUMN = "Score"
FOLLOW_UP = "Which one is more congested?"


def _answer(question: str, history: list[ChatMessage]) -> Answer:
    events = list(run(history, question))
    return events[-1]


def _check(answer: Answer, tool: str, facts: list[str]) -> list[str]:
    problems = [f"missing '{fact}'" for fact in facts if fact not in answer.text]
    if tool not in [call.name for call in answer.tool_calls]:
        problems.append(f"{tool} not called")
    has_kpi = any(
        call.name == DETAILS or json.loads(call.arguments).get("sort_by", "score") in KPI_SORTS
        for call in answer.tool_calls
    )
    if KPI_COLUMN in answer.text and not has_kpi:
        problems.append("a score column without any score in the data")
    if answer.number_check.unverified_numbers:
        problems.append(f"numbers not in the data: {answer.number_check.unverified_numbers}")
    return problems


def _report(question: str, problems: list[str]) -> int:
    print(f"{'PASS' if not problems else 'FAIL'}  {question}  {'; '.join(problems)}")
    return int(bool(problems))


def main() -> int:
    failures = 0
    for question, tool, facts in CASES:
        answer = _answer(question, [])
        failures += _report(question, _check(answer, tool, facts))
        if "Santa Ana" in question:
            history = [
                ChatMessage(role="user", content=question),
                ChatMessage(role="assistant", content=answer.text),
            ]
            follow_up = _answer(FOLLOW_UP, history)
            failures += _report(f"(follow-up) {FOLLOW_UP}", _check(follow_up, DETAILS, []))
    print(f"{len(CASES) + 1 - failures}/{len(CASES) + 1} passed")
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
