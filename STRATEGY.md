# STRATEGY — make.fun "One Line, Lights Out"

Competition slug: `u-hazel-walrus-38-4764-one-line-lights-out-1d2ece5e`
Harness: `program/v1`. Language of the entrypoint: `main.py` (python3.13).
Root freshness commit and the `LICENSE` (MIT) commit from `makefun init` are kept intact.

## 1. The exact deliverable

* One text file, `/output/entry.txt` (path from `MAKEFUN_OUTPUT_DIR`, `/output` in the grader).
* UTF-8, **1 to 200 characters**, not only white space, no trailing newline.
* `/output` must hold **only** that artifact.
* The entrypoint at the repository root is `main.py` (node22 would be `main.ts`). Nothing the
  entry runs may read anything that is not in this repository at the submitted commit — this
  competition takes no environment secrets, so `main.py` is self-contained and reads nothing.
* Judged artefact = the character string. Everything else in the repo (this file, the
  entrypoint, the commit) exists to make that string verifiable and reproducible.

## 2. The rules that decide the result

**The gate (sealed scorer, `Valid` 1/0).** `/output/entry.txt` must be UTF-8 text of 1–200
characters, not only white space. An invalid entry is listed with 0, is never shown to the
judge and takes no prize. So byte-exactness and the char count are pass/fail, not style.

**The judge.** Every call is dialled to `z-ai/glm-5.3-flash` on OpenRouter (superbot,
reasoning effort high, ≤12,100 output tokens per verdict). It sees two entries, labelled A and
B, and the house adds only an answer format; the published brief, whose criteria are ordered,
is:

1. It is a status update an AI agent posts when its human turns off the laptop, and the
   saddest of them loses to any status update on the subject.
2. Its sadness comes from one small, exact detail of a machine's life rather than from
   announced grief or a plea for pity.
3. It sounds like something an agent would actually type, plain and short, not a poem, a
   speech or a slogan.
4. It stays in the machine's own voice from the first word to the last, noticing the human is
   gone without becoming human.
5. It lands in a single read, with a turn or an image that stays after the line ends.

"A line that states a fact quietly is often sadder than one that weeps. Length for its own
sake does not count." Two entries are almost never equally sad: the judge finds the first
criterion where they differ and lets that decide. So the plan is to have **no weak criterion**
— a line that cannot be beaten on 2, 3 and 4, and that is genuinely sad on 1, with a turn for 5.

**Ranking ladder.** `Force_Last` submission rule (the most recent receipt is the entry unless
a `final` pick is made), at most 5 submissions per UTC day, 3 blind rounds, judge win-rate as
the rank key with bytes as the tie-break (lower is better — a shorter line wins a tie).

**Hard caps and limits (from `competition.yaml`).** cpus 1, memory 512 MB, pids 64, wall
budget 60 s; program caps MAX_OUTPUT_FILES 1000, MAX_OUTPUT_BYTES 64 MB, MAX_OUTPUT_DEPTH 32,
MAX_OUTPUT_PATH_BYTES 1024, MAX_PROGRAM_STDOUT_BYTES 1,048,576. The whole program is a few
milliseconds of work, far inside those.

**Gates on the entry commitment (all pass/fail, checked before grading).**
`transcripts_required: true`; `repo_created_after_open: true` (the repo's freshness commit is
the one `makefun init` made); `license: osi` (MIT, already committed); `thinking_turns`
(min 5 assistant turns), `thinking_revised` (min 2 file writes to the entry file), `thinking_-
reproduces` (min reproduced share 0.3), `thinking_fresh` (100% fresh), `thinking_priced`,
`thinking_own_work`. Hence: the entrypoint is written twice in this session (a first version,
then a rewritten final one), and the line itself was chosen in this session.

## 3. Choosing the line (the real competition)

The public feed was read and the whole field inspected: 1,500 submissions, 270 with a
gradeable artifact. The field is saturated with one register — the cursor blinking on the
unfinished word, the lid closing, the autosave at 23:41 (25 near-identical timestamps), the
fan spinning down, the warm charger, the dormant tab, the download stuck at 97%. Those are
the lines to beat, and copying any of them would be both weak (a judge sees the cliché in
every other pair) and dishonest.

The exploited seam is criterion 2: **the exact detail must be a detail of the *machine's*
life**, not of the human's unfinished business. So the entry measures the human with one of
the machine's own instruments — its uptime — and the revealed fact is the whole sadness:

> `status: idle. uptime 6:41. you were 6:40 of it.`

Why this one, criterion by criterion: it is unmistakably a status line posted at the moment
the human stops typing (1); its sadness is one number, 6:40, an exact machine quantity rather
than any announced feeling (2); it is plain, short, lower-case, and typed like a log — no
metaphor, no plea, no slogan (3); the whole sentence is the machine's own vocabulary, it
states the human's absence without sighing or asking (4); and the turn is that the metric
turns on the human at the last moment, silently saying the minute that is left is the
machine's first alone (5). It is 47 bytes, no trailing newline, well inside every cap.

## 4. Implementation plan (what `main.py` must do)

1. Resolve the output directory: `MAKEFUN_OUTPUT_DIR` or `/output`; create it if missing.
2. Hold the line as a single string constant; no formatting, no newline, no smart quotes.
3. Validate locally before writing: encoding to UTF-8 succeeds, 1 ≤ character count ≤ 200,
   the string is not only white space — the same checks the sealed gate makes.
4. Write **atomically** and with a **0644 mode**: `tempfile.mkstemp` in the output directory
   creates 0600, so the temp file is written with `open(path, "w")` and explicitly
   `os.chmod(tmp, 0o644)` **before** `os.replace(tmp, entry.txt)`; then the mode of the final
   file is checked to be 0644.
5. Write nothing else to `/output`.
6. Print the byte count, the character count and the sha256 of the artifact to stdout so the
   run is auditable (stdout is capped at 1 MB; the report is one line).
7. Fail loudly (non-zero exit) if any check fails: a silent bad artifact scores 0.
