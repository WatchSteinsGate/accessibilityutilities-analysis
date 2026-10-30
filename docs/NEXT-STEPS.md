# Current success-path tracing checkpoint

For every agent: follow [AGENTS.md](../AGENTS.md), append [WORKLOG.md](WORKLOG.md), and publish reviewed reports and supporting files here rather than leaving the only record in chat.

## What changed

The work is still recovering the **original success-path graph**, comparing original/R03 behavior and checking its cancellation, failure and recovery dependencies. It is not a patch-development or release milestone.

Two new repository editions preserve the latest findings:

- [Cancellation, render cleanup and shortcut consumer](CANCELLATION-RENDER-SHORTCUT.md): 232 labeled cases.
- [Accepted attachment, singleton reuse and render completion](ATTACHMENT-FACTORY-COMPLETION.md): 210 labeled cases.

All nine new repository-adapted suites passed a fresh rerun with the pinned dependencies. Existing lifecycle/resize reports and their five suites were preserved. Counts are model records, not independent end-to-end paths, and the scopes overlap.

## What is next

| Priority | Remaining question | Evidence needed / completion boundary |
| --- | --- | --- |
| 1 | Can lifecycle changes actually occur between callback admission and attachment? | Recover runtime/reentrant routes and main-queue constraints; staged mutation alone is insufficient. |
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
