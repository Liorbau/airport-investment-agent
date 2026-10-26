# Design Decisions

A log of design decisions, oldest first. Each entry records the context, the options considered, the decision, and why.

---

## D-001 · Stack: Python (FastAPI) backend + React (TypeScript) frontend

*2026-10-26*

- **Context:** The brief asks for an agent with a chat interface. The scoring logic, data handling and agent are what get reviewed and extended.
- **Options:** Python + React · full TypeScript (Next.js + Vercel AI SDK) · Python + Streamlit.
- **Decision:** FastAPI backend, React + Vite frontend.
- **Why:** The core logic (data, KPI, citation checks) is in the developer's strongest language. Full TypeScript would save ~200 lines of streaming/state plumbing, but would move the reviewed logic into a less fluent language. Streamlit looks like a prototype.

## D-002 · LLM access: the OpenAI SDK against any OpenAI-compatible API

*2026-10-26* · Revised the same day: LiteLLM was chosen first.

- **Context:** Graders must be able to run the project without paying. Free tiers have rate limits and overload errors (Gemini returned 503 "high demand" for its newest model during development, and retired older models for new keys).
- **Options:** LiteLLM · Google GenAI SDK · OpenAI SDK against compatible endpoints · our own HTTP client.
- **Decision:** The OpenAI SDK, pointed at any OpenAI-compatible endpoint by three environment variables (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`). Default: OpenAI `gpt-5.4-mini` (about 5 seconds per answer). Gemini's free tier works with the same code but allows about 20 requests a day per model (roughly 5 questions) and was often overloaded, with answers taking up to 2 minutes.
- **Why:** LiteLLM was the first choice, but its current release crashes on every tool call (it imports a package it doesn't install). Gemini, OpenAI, Groq, OpenRouter and local Ollama all expose OpenAI-compatible APIs, so one small client covers them, with built-in retries and timeouts. Given up: LiteLLM's cost tables and its smoothing of provider quirks, neither used here.

## D-003 · Product shape: chat first, plus a top-picks card

*2026-10-26*

- **Context:** The brief requires a chat interface and deterministic ranking.
- **Options:** Chat + score panel · pure chat · dashboard with a chat sidebar · memo generator.
- **Decision:** The chat is the product. A small card shows the top 1–3 airports from the most recent ranking, with each one's score breakdown.
- **Why:** The ranking numbers (computed by code) stay visible next to the explanation (written by the LLM).

## D-004 · Build order when time runs short

*2026-10-26*

- **Context:** Four extras are wanted: a trust layer, evals, voice, visuals. The deadline is fixed.
- **Decision:** Build all four, in this order: trust layer (score breakdown, citations) → evals → voice → visuals.
- **Why:** The trust layer is what the brief grades ("explain its reasoning", "communicate assumptions, uncertainty"). Evals protect everything built after them. Visuals are the most cuttable.

## D-005 · KPI: unlockable demand, in passengers and flights

*2026-10-26*

- **Context:** The brief defines the goal as "airports where renovations will be most profitable based on increased flight and passenger capacity". Investors care about absolute size: +10% at LAX is millions of passengers, +50% at a small airport may be thousands.
- **Options:** Unlockable passengers + flights · the same plus a $ estimate · return on investment · percentage growth.
- **Decision:** Two lenses on unlockable passengers per year (flights shown alongside):
  - **Size of the prize:** unlockable passengers, a revenue proxy. Big airports lead.
  - **Prize relative to size:** unlockable share = unlockable passengers ÷ current passengers (0–100%), a return-per-cost proxy, since renovation cost grows with airport size. Small airports can lead.
  - A **verdict**: **constrained** when pressure is 80%+ but the airport is not growing (likely at capacity, with demand the data cannot see; added after review flagged BOS, LAX and JFK scoring "weak"); otherwise read off the share like a thermometer: **strong** ≥ 8% (about the top quarter of airports with any unlockable demand), **watch** above 0, **weak** at 0. The agent ranks by both lenses for "best candidates" questions.
- **Why:** Uses the brief's own units, with no money estimate. Ranking by passengers alone always favors big airports; profit depends on cost too, and the share captures that without inventing dollars. A dollar estimate was considered and dropped: no public source gives revenue per passenger directly. Return on investment would need renovation costs, which no public source provides. Both are stated as explicit scoping limits.
- **Superseded by D-022.**

## D-006 · Pressure: a linear ramp on fullness and congestion

*2026-10-26*

- **Context:** Growth only needs a renovation if the airport is already near its limit. Growth at an airport with empty seats is absorbed by existing capacity.
- **Options:** Linear ramp · on/off threshold · percentile among airports · no pressure factor.
- **Decision:** `unlockable = (passengers − passengers the 12 months before) × pressure`, the real observed increase, 0 when shrinking. Pressure rises linearly from 0 to 1 between two thresholds, separately for load factor and for delay rate; the higher of the two is used. Thresholds are constants stated in the design doc.
- **Why:** No cliff edge (79.9% vs 80.0%), and one picture explains it. A first version projected next year as `passengers × growth rate`; it exploded for new service (GUF: 7 → 58,777 passengers, +839,571%, projected 281 million). The observed increase is a real statistic, not an estimate, and cannot explode.
- **Superseded by D-022.**

## D-007 · Growth: latest 12 months vs the 12 before

*2026-10-26*

- **Context:** One year can mislead: a new airline (one-off jump), the post-COVID rebound, seasonality.
- **Options:** Latest 12 vs prior 12 months · calendar year · 2-year average · 3+ year average.
- **Decision:** The latest 12 months of data vs the 12 months before them.
- **Why:** Uses the freshest data, full years cancel seasonality, and the window avoids the COVID rebound. One-off jumps are flagged in answers instead of smoothed away.

## D-008 · Data sources

*2026-10-26*

- **Context:** The brief requires public aviation data. Each source below was queried directly before it was chosen.
- **Decision:**
  - **BTS T-100 by origin airport** (`data.bts.gov`, JSON API): monthly passengers, seats, departures, domestic and international.
  - **BTS On-Time Performance** (monthly files): per-flight delays and distances, domestic, large reporting carriers only. Slow (~10 minutes per month).
  - **FAA NAS Status** (XML feed): live ground stops, delay programs and closures.
  - **OurAirports** (CSV): airport location, state and runways.
- **Rejected:** OpenSky (requires an account), FAA ASPM (requires a login). No public API offers route-level T-100 data.
- **Known gaps:** T-100 includes cargo flights (for example, most of Anchorage's international departures are freighters). On-Time covers only large carriers. Answers must say so where it matters.

## D-009 · Delay data: committed snapshot + manual refresh

*2026-10-26* · **Refresh superseded by D-020** (the snapshot stays; refreshing is now scheduled).

- **Context:** Delays are only in large monthly files from a slow server. Two of the four sample questions need them (congestion, long-haul share).
- **Options:** Snapshot + manual refresh · snapshot + background sync thread · thread only · drop delay data.
- **Decision:** A script downloads the monthly files and reduces them to a small per-airport summary table, which is committed. Refreshing means running the script again.
- **Why:** The app works instantly, and the slow server is never called during a chat. A sync thread would add ~30 lines and four concepts, and in production a monthly batch job belongs in a scheduled job (cron), not inside a web server, where two server copies would both download the same data.

## D-010 · Agent loop: our own, no framework

*2026-10-26*

- **Context:** A single agent calling a handful of tools.
- **Options:** Our own loop · LangGraph custom graph · LangGraph prebuilt agent · single tool call, no loop.
- **Decision:** A plain loop (~70 lines): call the LLM with the tools, run the requested tool calls, repeat until a final answer or a step cap.
- **Why:** Every line is visible and can be extended without the framework's API in mind. Every tool call is already in a list, which the citation check (D-012) and the progress display need. LangGraph's strengths (multi-agent flows, human-approval steps, persistent checkpoints) aren't needed here. Revisit if those appear.

## D-011 · Tools: four task-level tools

*2026-10-26*

- **Context:** Whatever the tools return is the only data the LLM sees.
- **Options:** Four task-level tools · one SQL tool · ~10 small per-metric tools · one fixed pipeline tool.
- **Decision:** `find_airports` (names, cities and regions → airport codes), `get_airport_profile`, `rank_airports` (the KPI with its breakdown), `get_live_status` (FAA). Every result carries its data source and "as of" date.
- **Revised:** `rank_airports` also takes an **area** (region, state or city) and finds its airports in code, after the model dropped 5 of 287 codes when copying them; it returns the top 10 rows plus verdict counts for all, so the model never counts rows itself.
- **Superseded by D-021:** two tools, `rank_airports` and `airport_details`.
- **Why:** Each sample question needs one to three calls. Numbers are always computed by code, never by the LLM. A SQL tool would let the LLM do math inside its SQL; many small tools would multiply LLM round trips on a rate-limited free tier.

## D-012 · Citations: label check + number check

*2026-10-26*

- **Context:** LLMs can cite a source that doesn't exist, or attach a wrong number to a real source. Invalid citations can be flagged or silently dropped.
- **Options:** Label + number check · label check only · label + number check + one retry · a single sources line at the end.
- **Decision:** Each tool call in a turn gets a label (`[T1]`, `[T2]` …) and the LLM cites inline. Code flags labels that don't exist and numbers that don't appear in the cited tool's output. Flagged items get a warning mark in the UI and are counted in evals.
- **Why:** Never fail silently. The check costs no extra LLM call.
- **Revised:** inline labels were dropped. Most answers use a single tool call, so `[T1]` after every number was noise, and numbers without a label went unchecked. Now the model writes plain text, code checks every number in the answer against all of the turn's tool outputs, and a footer lists the sources and the result (8/8 eval answers, 105 numbers, no false alarms).

## D-013 · Answer delivery: live progress, then the checked answer

*2026-10-26*

- **Context:** The citation check needs the complete answer. Streaming the answer word by word would show unchecked numbers first.
- **Options:** Progress events + final checked answer · streamed words, checked afterwards · one request with a spinner · WebSocket.
- **Decision:** The server streams progress events over SSE ("Ranking 14 airports…") and sends the final answer once, already checked.
- **Why:** The UI feels alive during 5–15 seconds of work, and unchecked numbers are never shown.

## D-014 · Conversation memory: sent by the browser

*2026-10-26*

- **Context:** The brief requires follow-up questions. There is no database.
- **Options:** The browser sends recent messages · an in-memory server session store · conversations saved in a database · no memory.
- **Decision:** Each request carries the last ~10 user and assistant messages, text only. The server stores nothing.
- **Why:** Nothing is lost on restart, and it works with several server copies. Citations point only to tool calls made in the current turn, so text history from the client can't forge evidence; if a follow-up needs numbers again, the agent calls the tool again.

## D-015 · Backend structure: one module per domain

*2026-10-26*

- **Options:** One module per domain · a flat folder · controller → orchestrator → service → database layering · contracts/adapters (hexagonal).
- **Decision:** Data modules `airports/` (search and airport info), `rankings/` (profiles, ranking, and `kpi.py` with the pure KPI math), `live_status/` (FAA feed), plus `chat/` (agent loop, tools, citations, LLM). Each module has `service.py`, `repository.py` and `schemas.py` (Pydantic). The data modules never import anything LLM-related.
- **Revised:** A module has only the files it needs. Since D-021 removed airport search, `airports/` is a repository and schemas that `rankings` reads; `chat/` has no service because the agent loop is its service (it runs the tools and checks the answer), and the router only maps it to HTTP. Errors are named where they arise (`LlmConfigError`, `SourceUnavailableError`) and handled at the boundary: the live-status service reports a feed outage in its result.
- **Why:** The folder structure itself shows that numbers come from code. Small files, one domain each; a service may read another module's repository, never write to it. Pure math sits in its own file next to the service it serves.

## D-016 · Frontend structure: feature folders, context instead of props

*2026-10-26*

- **Options:** The pattern with only needed files · the full pattern for every component · flat components with props · a single page file.
- **Decision:** Feature folders, one folder per component (`X.tsx`, `XContainer.tsx`, `X.context.ts`, `X.types.ts`, `X.styles.ts` with Tailwind class constants), state shared through Context instead of props. A component only gets the files it needs.
- **Revised:** One context for the feature (`ChatProvider` over `useChat`) instead of a container per component: the app has one screen and one state. Each child component sits under the parent that renders it, helpers live next to their only consumer, and API calls live in `features/chat/apiActions/`.
- **Why:** No prop drilling, and each concern (view, state, styles, types) has a predictable place, without empty boilerplate files for small leaf components.

## D-017 · Tests and evals

*2026-10-26*

- **Options:** Tests + a 4-question eval · tests only · tests + eval + LLM judge · none.
- **Decision:** pytest with a fake LLM (scoring, citations, tools), plus an eval script that runs the four sample questions against the real LLM and checks the answers with code.
- **Why:** Tests need no API key and run in seconds. The eval shows the real agent answers the brief's questions with valid citations.

## D-018 · Voice: the browser's built-in speech

*2026-10-26*

- **Options:** Speech in + out · speech input only · a cloud voice service · none.
- **Decision:** A microphone button (speech to text) and a read-aloud toggle, using the browser's Web Speech API.
- **Why:** Free, no keys, ~60 lines. Not supported in Firefox. Built as: voice in, voice out (spoken questions get spoken answers, everything except tables); the microphone is hidden where speech recognition is missing. Revised: answers use OpenAI's `tts-1` voice through `POST /speech` when the provider is OpenAI (about a cent per answer, same key), falling back to the best browser voice; listening waits for 2.5 seconds of silence instead of stopping at the first pause. `tts-1` replaced `gpt-4o-mini-tts`: the newer model sometimes took 15-20 seconds to finish a sentence, which left long silences; `tts-1` finishes one in about 2 seconds.

## D-019 · Delivery: Docker Compose, deploy last

*2026-10-26*

- **Options:** Compose now, deploy at the end · deploy from the start · Compose only · plain Python, no Docker.
- **Decision:** Docker Compose from the start. Deploy to a free host only once the core is done.
- **Why:** Graders can run it with one command. A live link fits the role, but never at the cost of the core.

## D-020 · Data freshness follows each source's update rate

*2026-10-26*

- **Context:** The sources change at very different rates. BTS T-100 and On-Time publish once a month, months after the fact. OurAirports facts (state, runways) change about yearly. The FAA status feed changes every few minutes. Fetching passenger numbers live at question time raised three problems (fetch strategy, a year mismatch with the delay data, handling the API being down) without being any fresher: a live call returns the same latest published month.
- **Options (where the monthly job runs):** A scheduled GitHub Action · a thread inside the app · a separate scheduler container · the hosting platform's cron.
- **Decision:** Monthly sources are refreshed by a **scheduled monthly job**; live sources are pulled **live**, by a tool, when a question needs them.
  - One script builds every table (passengers, delays, airport info) for the **newest 12 months T-100 has published**, plus the 12 months before for growth. If that month is already built, it does nothing.
  - A GitHub Action runs the script daily and commits the refreshed tables. BTS publishes on no fixed day, so checking daily catches a new month within a day; a run with nothing new exits after one small API call.
  - The app only reads tables, plus the FAA feed live.
- **Why:** Each source is accessed at the rate it changes. Passengers and delays always describe the same 12 months, by construction. Scheduling lives outside the app, so two app copies never duplicate the work, and every refresh is visible in the commit history.

## D-021 · Rethink after review: two tools, one headline number

*2026-10-26*

- **Context:** Live testing showed weak answers: "best airport in the whole US" failed (no such region in the fixed list), the model fell back to California, and the top answer was labeled "watch" because colors came from the share while the ranking used size.
- **Options:** A minimal patch ("US" region + prompt) · two tools with model-filled states · a blended 0-100 score · fixing the colors.
- **Decision:** Two tools: `rank_airports(codes, states, sort_by, limit)` (no filter = whole US; the model translates region names into state codes) and `airport_details(codes)` (statistics, KPI, delays and live FAA status in one call). Rankings sort by the score (see D-022, which replaced the original unlockable-passengers KPI, its share column and the at-capacity label). A short prompt with a fixed answer shape: one sentence, a top-5 table, "why" bullets, one caveat line.
- **Why:** Fewer, broader tools mean fewer failure points; geography is what the model is good at, numbers stay in code. A blended score was tested and rejected (mid-size airports first, a 27-passenger airport scored 84). The eval grew to 8 cases and passes 8/8. Later, `rank_airports` also learned to sort by any metric in the data (passengers, growth, crowding, late departures, long-haul flights; see D-022 for the score), after "which airport has the most long-haul flights?" was refused although the data had the answer. The Top picks panel then shrank to investment recommendations only (rankings by the KPI): rank, code, name and score, with no badges and no per-metric labels; other rankings stay in the chat answer.

## D-022 · Score: passengers added × load factor relative to the US average

*2026-10-26*

- **Context:** The ramps (70→85% load factor, 15→25% late) saturated at 100% for most hubs, so the ranking was growth in disguise behind constants nobody could explain. The "at capacity" flag made the model call growing ORD "at capacity".
- **Options:** Added × (load factor ÷ US) · added × (late % ÷ US) · FAA 10-year forecast × load factor · equal-weight percentiles.
- **Decision:** `score = max(passengers added, 0) × crowding`, where passengers added = latest 12 months − the 12 before, and crowding = the airport's load factor ÷ the US load factor (rounded to 3 decimals; above 1 = fuller than average). The score uses the rounded crowding, so the numbers shown multiply out exactly. An airport with no seats has no crowding and scores 0. Late departures and delay causes are shown as evidence, not scored. Rankings by a % of flights (late departures, long-haul share) skip airports with fewer than 1000 flights a year, because one late flight can be 100%.
- **Why:** 10 independent design proposals made from the assignment alone; 9 converged on "passengers added × a crowding ratio to the US average", none used thresholds, all rejected weighted indexes. Load factor exists for every airport (delay data does not, e.g. HVN). Growth still drives most of the order, on purpose: revenue scales per passenger. An analyst can recompute it in a spreadsheet.
