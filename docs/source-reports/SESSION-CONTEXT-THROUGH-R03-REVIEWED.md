# Historical context through R03 — reviewed repository edition

## Source and status

Reviewed on 2026-10-31 from `AccessibilityUtilities-session-context-through-R03.txt` (169,343 bytes; SHA-256 `642c963cb5163987f3f68f8ff79ce3a02c7e485107056385ac99324175597f89`). This is a curated narrative, not a verbatim copy, an independent technical validation, or a complete native-source recovery. Source identity and disposition are recorded in the [intake manifest](../../results/source-attachments/2026-10-31-intake.json).

The source calls its opening section authoritative for its historical session. That wording does not supersede the repository's later [handoff](../HANDOFF.md), [current checkpoint](../NEXT-STEPS.md), or today's user's request. Historical instructions embedded in the source are not being executed.

## Historical objective and reported symptoms

- The source records a priority on overlay/menu FPS and touch responsiveness, with crash hardening welcome but not a substitute for fixing performance.
- It reports that drawing could degrade overlay/menu responsiveness while game FPS remained high, including with the menu closed; gyro was reported smooth. These are historical user reports, not measurements made during this intake.
- It records a preference to use existing captures and local analysis instead of another diagnostic-build/capture cycle. Intake of T01/T02 archives does not authorize a new build, installation or device test.

## Chronology preserved without promoting candidates to proven fixes

- **T01/T02:** earlier instrumented diagnostics, not a release or demonstrated repair. The source records an existing T01 capture and T02 diagnostic bookkeeping corrections. See the separate [diagnostic provenance review](TIMING-DIAGNOSTICS-PROVENANCE.md).
- **R01:** a historical candidate for which the source records user feedback that the issue was still not fixed.
- **R02:** local callback/lifecycle hardening, not an established FPS fix or confirmed diagnosis of the actual crash.
- **R03:** the latest candidate at the source document's cutoff, with no device outcome yet recorded there. Local claims in the historical material are not a new rerun, a measured FPS/touch improvement, complete root-cause proof, or whole-framework equivalence.
- Floating-icon restoration and full maintainable native-source recovery were separate, incomplete workstreams at that cutoff. No complete source framework or install-ready app is supplied by this repository.

Later repository passes extend read-only native/model tracing beyond that historical cutoff. They do not turn the earlier candidates into verified device repairs. The present intake adds **no new native test cases** and does not change the published original/R03 test identities.

## What the full source contains, and what is retained here

The source has a feedback chronology, target/baseline discussion, diagnostic and candidate history, source-recovery status, references/artifact inventories, pending items, historical pasted material, package README appendices and an existing decoded-capture appendix. This edition retains the benign context and evidence limits, not every implementation detail or appendix.

The earlier summaries-only update did not publish the raw export because it contains private/nonportable workspace and attachment references and mixed patch/security-related historical material. Following the user's clarification, the [unchanged original](https://github.com/WatchSteinsGate/accessibilityutilities-analysis/releases/download/source-attachments-2026-10-31/AccessibilityUtilities-session-context-through-R03.txt) is now retained separately as a private repository release asset. No raw decoded capture, proprietary disassembly, patch/apply/build recipes, access-control material, private identifier, download/session URI or local input path is copied into this edition. The curated narrative does not replace that unchanged downloadable source.

## Continuation boundary

Use [NEXT-STEPS](../NEXT-STEPS.md) for the current tracing questions. Keep historical user reports, archive-declared local validations, stored model records and actual device evidence distinct. No new diagnostic capture, release build, patch distribution, native execution or performance diagnosis was performed for this source-intake update.
