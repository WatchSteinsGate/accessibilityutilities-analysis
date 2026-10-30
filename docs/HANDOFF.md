# Continuation handoff

## Goal and constraints

Investigate the original general startup-to-presentation path beyond the UI-only trace, compare supplied original and R03, and retain enough evidence and context for continuation. The user reports overlay/menu FPS and touch response degrade even when game FPS remains high; degradation can persist with the menu closed. Gyro was historically reported smooth. These are user reports, not measurements established by these tests.

The user prefers concrete local tracing and verification over reassurance and does not want another diagnostic-build/capture cycle. Continue from existing material. Do not describe a scoped emulator pass as an end-to-end device result.

## Historical sequence

1. Earlier patch-integrity work identified multiple revisions and changes beyond an isolated UI edit. R01 did not resolve the reported issue; no R02/R03 device performance fix was established.
2. UI tracing examined ownership/attachment, event queuing, collection, and presentation boundaries. One historical ownership candidate addressed a modeled local mismatch, not restoration of the original whole-system success path. No candidate or installer is distributed here.
3. Whole-system expansion indexed startup roots, lifecycle/epoch handling, coalesced background requests, result/state processing, activation/callbacks, UI/data collection, rendering, queued input, and recovery. It produced scoped tests and an explicit unresolved-coverage ledger; it did not finish all paths.
4. Lifecycle continuation added 144 cases for attachment, recognizer reuse/coexistence, shortcut signaling, layout ordering, and size-sync scheduling.
5. Resize continuation added 150 cases for geometry, numerical edge behavior, button cache/failure/clamp behavior, and one-level staged reentry.
6. Repository packaging removed historical path dependencies from the five benign continuation scripts. Fresh local results are retained separately from historical records. No binary was edited or installed during these continuation/packaging passes.

## Conclusions to carry forward

- Lifecycle readiness depends on application state and notifications; do not equate it with a license/server success flag.
- Startup/presentation is a graph, not one universal success branch. Backend success and complete runtime behavior remain unverified.
- Overlay construction and later attachment do not necessarily select the same parent across revisions. A modeled ownership/attachment mismatch is evidence of a local discrepancy, not measured continuous reparenting or an FPS cause.
- Input events are queued rather than represented solely by one overwritten byte. Collection occurs before later visual decisions; a closed menu does not prove no overlay work.
- Cached window recognizers are reused on ordinary attachment changes. Same-window calls avoid remove/add in the modeled lifecycle cases.
- The original size-sync body is unchanged in R03, but R03's caller appends another layout helper, so the whole layout path is not equivalent.
- Off-main size-sync scheduling precedes its main-thread busy guard. Multiple modeled calls enqueue separately; real queue accumulation has not been established.
- Same-owner button reuse avoids allocation but still performs center/front work. Synthetic owner changes and allocation failures reveal cache boundaries, not actual device occurrence.
- The original resize guard suppresses nested original setters in staged tests. It does not cover the appended button helper. Real UIKit-triggered recursion, exceptions, races, and cost remain unknown.
- Local synthetic zero/NaN/infinite geometry reveals setter/publication differences; it is not evidence that such values caused the user's slowdown.

## Next work, in order

1. **Lifecycle cancellation and stale queued callbacks:** compose queued work with detach/background/epoch changes under legitimate state. Separate native checks from modeled scheduling assumptions; do not infer real races from a chosen sequence alone.
2. **Render resource failure and cleanup:** enumerate ordinary acquisition/early-return/cleanup exits and object lifetime boundaries. No GPU or device timing claim without real evidence.
3. **Shortcut request consumer:** trace the existing signal through legitimate presentation state. Do not alter input policy or force access-gated paths.
4. **Broader graph:** unresolved worker fan-out, indirect callbacks/runtime targets, and producer of a secondary setup request remain. Keep these marked open.
5. **Genuine backend-to-state transitions:** unresolved and outside the bounded local tests. Do not substitute a stand-in result for authenticated backend behavior or extend authentication/trust/anti-cheat circumvention.

Before any new work, confirm the two input hashes. Retain per-case assumptions and failures. Do not build or distribute a modified release, claim complete original equivalence, or claim a fixed FPS/touch problem.

## Existing private workspace record

The fuller historical session context remains in the user's Notion workspace, titled “AccessibilityUtilities — Session context, patch audit & whole-system trace.” This repository is a curated continuation, not a complete export of that page or its private attachments. Deliberate omissions are listed separately. No automatic two-way sync is configured.
