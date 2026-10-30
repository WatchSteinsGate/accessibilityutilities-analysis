# Current success-path tracing checkpoint

For every agent: follow [AGENTS.md](../AGENTS.md), append [WORKLOG.md](WORKLOG.md), and publish reviewed reports and supporting files here rather than leaving the only record in chat.

## What changed

The work is still recovering the **original success-path graph**, comparing original/R03 behavior and checking its cancellation, failure and recovery dependencies. It is not a patch-development or release milestone.

Two new repository editions preserve the latest findings:

- [Cancellation, render cleanup and shortcut consumer](CANCELLATION-RENDER-SHORTCUT.md): 232 labeled cases.
- [Accepted attachment, singleton reuse and render completion](ATTACHMENT-FACTORY-COMPLETION.md): 210 labeled cases.

All nine new repository-adapted suites passed a fresh rerun with the pinned dependencies. Existing lifecycle/resize reports and their five suites were preserved. Counts are model records, not independent end-to-end paths, and the scopes overlap.

## Latest scheduling pass

[Queue constraints and callback routing](reports/LIFECYCLE-SCHEDULING.md) adds 64 scoped cases. Recovered lifecycle registrations request `mainQueue`; constructor and coalesced reevaluation blocks use the imported main dispatch queue. Ordinary queued notification delivery does not establish post-admission interruption. Runtime reentry/off-main state writers remain unproven. Six selected ranges match; the separately recorded R03 resume-mutator range differs as expected. Earlier suites were not rerun.

## What is next

| Priority | Remaining question | Evidence needed / completion boundary |
| --- | --- | --- |
| 1 | Can lifecycle changes actually occur between callback admission and attachment? | Main-queue operands are now recovered. Next trace synchronous constructor callees, lifecycle wrapper/initializer caller contexts, and other state writers for concrete reentry/off-main routes. Staged mutation alone remains insufficient; do not assume ordinary queued callbacks interrupt the constructor. |
| 2 | Who owns the shortcut control pointer and how long is its pointee valid? | Trace actual producer, callers, changes and remaining writers; establish lifetime rather than assuming changed-pointer inputs occur. |
| 3 | What happens inside backend allocation/draw/completion registration failures? | Extend native draw-loop and resource contracts beyond modeled providers; distinguish block registration/copying from actual GPU callback delivery. |
| 4 | How does the accepted reusable-buffer cache body behave? | Trace insertion, enumeration, eviction, synchronization and selection/reuse; entry guards are not the full policy. |
| 5 | What drives secondary setup and the remaining workers/indirect calls? | Recover the producer and intended trigger frequency; continue explicit unresolved-coverage accounting. |

## What must not be claimed

- No literal every-function/every-branch recovery.
- No complete original-success equivalence or minimal patch set.
- No observed device race/crash cause from synthetic cases.
- No proven device FPS or physical touch-latency improvement.
- No genuine backend success inferred from seeded state.

Use existing captures, authorized inputs and read-only local analysis. No new diagnostic build or modified release binary is requested. Keep authentication, trust, anti-cheat and access-control circumvention outside this repository's scope.

## Navigation

- [Handoff](HANDOFF.md)
- [Reproduction](CONTINUATION-REPRODUCTION.md)
- [Artifact/provenance manifest](CONTINUATION-ARTIFACTS.md)
- [Omissions](OMISSIONS.md)

## Startup/reentry continuation — 2026-10-30

[New report](reports/STARTUP-REENTRY-BOUNDARIES.md): recovered image initializer → main-queue block → registration producer → once block → observer initialization. The remaining direct lifecycle forwarding chains fold into the known transition/background graph; no independent thread hop or reachable interruption is established. Added 58 scoped cases; reran the existing 64 scheduling and 110 attachment cases.

**Next concrete priority:** trace the actual custom synchronous factory/initializer implementations reached by the admitted constructor, not just the now-resolved veneers. Preserve ordinary main-queue serialization and require positive reentry/state-writer evidence. The constructor's control value comes from `0x1011b68`; its actual producer, pointee lifetime and writers remain unresolved. No new diagnostic build is needed. [All supplied attachment occurrences](ATTACHMENT-INTAKE.md) are accounted for; omitted binaries/archives are not in Git.

## Factory/control-state continuation

[54 new cases](reports/FACTORY-CONTROL-PROVENANCE.md) compose four native singleton factories/once blocks, full FloatView/FieldView initializer bodies and the DrawWindow publication prefix. Slot `0x1011b68` has a recovered 256-byte allocation/publication excerpt; existing-slot reuse skips allocation. Whole-owner lifetime is not established. The producer excerpt differs between builds despite the selected shared contracts passing.

Next: trace deallocation/replacement and pointee writers; continue actual MenuWindow/OverlayView initialization and the DrawWindow remainder for concrete reentry/state-writer evidence. No real race or performance fix is established. Older native suites were not rerun in this pass.

## Complete Draw/Menu initializer follow-up

[46 new cases](reports/INITIALIZER-EFFECTS.md) now execute both complete native initializer normal/false/nil-return bodies with external runtime/filesystem/INI boundaries modeled. Draw still performs setup and size reset after modeled inherited nil. Menu ignores file-creation Boolean failure and performs configuration work before inherited init. Native once composition prevents repeating that work in the tested later factory calls, not universally.

Next remains actual OverlayView initialization and control-state deallocation/replacement/pointee writers. No real runtime reentry, lifetime or device-performance diagnosis is established. Existing 54-case factory suite rerun unchanged; other older native suites not rerun.
