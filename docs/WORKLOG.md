# Agent worklog

Append a new entry for each meaningful session. Keep older entries intact; correct them through explicit follow-up notes. Technical report structure is in [REPORT-TEMPLATE.md](REPORT-TEMPLATE.md), and the standing workflow is in [../AGENTS.md](../AGENTS.md).

## 2026-10-30 — Published success-path continuation evidence

- Agent: Notion AI, using the connected GitHub tools.
- Starting revision: `d578232168ebff4d00c4e62bd54eae485b7e1540`.
- Published revision: [`9737945145128aa459b265d5deca08357545d165`](https://github.com/WatchSteinsGate/accessibilityutilities-analysis/commit/9737945145128aa459b265d5deca08357545d165), via PR #1 / squash merge.
- Work: added two continuation reports, nine portable suites, 442 scoped case records, indexed JSON parts, provenance/reproduction documentation, an integrity validator, and updated handoff/roadmap/inventory/checksums.
- Evidence: `CANCELLATION-RENDER-SHORTCUT.md`, `ATTACHMENT-FACTORY-COMPLETION.md`, `../tests/continuation-a/`, `../tests/continuation-b/`, `../results/continuations/`.
- Validation: nine new suites passed with Python 3.13, Capstone 5.0.7 and Unicorn 2.1.4; indexed reconstruction checked all 442 records. Existing 294-case suites were preserved, not rerun. The remote checksum-manifest blob matched the staged manifest; only present staged-file hashes were checked locally, not a freshly downloaded whole checkout.
- Publication note: connector request-size limits required staged upload batches on a branch; PR #1 was squashed into one commit on `main`.
- Limits: modeled runtime effects, synthetic inputs, staged mutation and bounded prefix/cleanup tests are not real iOS/Metal/GPU runs, race proof, all-path recovery or an FPS fix. Excluded artifacts remain documented in `OMISSIONS.md`.
- Next: establish reachable post-admission lifecycle interleavings before interpreting staged attachment behavior as a real race.

## 2026-10-30 — Standing agent reporting and artifact workflow

- Agent: Notion AI, using the connected GitHub tools.
- Starting revision: `9737945145128aa459b265d5deca08357545d165`.
- Work: added root `AGENTS.md`, a technical report template and this worklog; linked the agent workflow from README and the next-steps page; updated inventory and checksum entries.
- Required future behavior: report work directly in this repo, commit reviewed permitted scripts/results and supporting files, record omissions/blockers, validate actual changes, maintain next steps and evidence boundaries, and link the published revision.
- Validation: documentation links and changed-file checksums checked locally against the loaded repository state. This is a documentation-only change; no research suites rerun and no new trace cases claimed.
- Limits: `AGENTS.md` is repository guidance, not automatic enforcement or synchronization; external agents must read and follow it.
- Next: the technical priority is unchanged—trace actual queue/notification/reentrant routes between eligibility and attachment; then investigate control-pointer lifetime and backend/cache internals.

## 2026-10-30 — Lifecycle scheduling and notification routing

- Agent: Notion AI, local read-only analysis plus connected GitHub tools. Starting revision: `ba6c9ff8340be1a766996f06ea63caa2d48f9a03`.
- Question: establish queue provenance before treating staged post-admission cancellation as a reachable race.
- Work/evidence: `reports/LIFECYCLE-SCHEDULING.md`, `../tests/continuation-c/`, `../results/continuations/continuation-c/`. Native initialization requests main operation queue for four/eight registrations; constructor/coalesced blocks use imported main dispatch queue. Added 64 cases and a bounded direct-reference/code-equality map. Updated handoff, roadmap, README, reproduction/provenance/omissions, validator, inventory and checksums.
- Validation: Python 3.13 / Capstone 5.0.7 / Unicorn 2.1.4; `python tests/continuation-c/test_scheduling.py` passed 64 cases; `python tests/continuation-c/map_scheduling.py` passed six equal ranges plus one expected changed resume-mutator range; `python tools/validate-continuation-results.py` validated all 506 continuation records. Earlier 442 continuation cases and 294 lifecycle/resize cases were not rerun. Input hashes unchanged; source syntax, local links and staged-file hashes checked, not a full-checkout checksum run.
- Corrections: raw unresolved-class dereference failed in preliminary exploration; final harness uses symbolic class bindings and indirect-symbol import metadata. Broad equality assertion initially included R03-changed resume instructions; narrowed comparisons preserve the expected inequality explicitly. No binary edit.
- Limits: modeled ObjC/ARC/enumeration/dispatch, recorded transition/suspend boundaries, skipped backend producer body and seeded generation. Main-queue operands constrain ordinary delivery; they do not prove runtime reentry absent, a real race present, genuine success, full coverage or a device-performance fix.
- Next: trace synchronous admission-to-attachment callees and remaining lifecycle wrapper/initializer caller contexts for a concrete reentry/off-main writer route; then resolve actual control-pointer owner/lifetime. Publication is grouped on a review branch and squashed when allowed; final revision is available through Git history/PR rather than a self-referential commit hash in this entry.
