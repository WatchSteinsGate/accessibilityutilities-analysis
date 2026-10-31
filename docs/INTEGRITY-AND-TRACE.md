# Integrity and whole-system trace summary

## Publication checkpoint — explicitly authorized 2026-10-31

The user explicitly requested “report to github now” after the local audit. This publication includes the original-success/minimality report and its reviewed supporting code, ledgers and records, including previously local continuations l–n required for reproduction. The local-pass statements below describe the earlier execution history, not this publication's status. No new binary, diagnostic build or source-archive modification is included. Future GitHub work still requires a new explicit user request.

Current result: two bounded original-behavior differences; original genuine producer/processing and patch necessity remain unresolved. Full local validation: 34 suites /1605 labels, previous 1565 values equal. Expected-difference assertions are not preservation or minimality proof.


## Current objective — original success and minimality (local, unpublished)

The user explicitly redirected work away from FPS/crashes: recover the **original success path**, then establish whether the patches are the **smallest justified set preserving intended functionality**. [Current report](reports/ORIGINAL-SUCCESS-PATH-AND-MINIMALITY.md) and [complete 63-range ledger](../results/success-path-audit/PATCH-NECESSITY-LEDGER.md). Two bounded native witnesses show original Float→same-frame Menu behavior omitted in R03 and original self-hit pass-through changed. Neither is silently accepted as an intended exception. The original genuine producer/processing path remains open; no minimality/no-breakage certification is claimed.

Full rerun: **34 suites / 1605 labels**, all previous 1565 record values equal, 40 new original-contract records. Passing expected differences is not preservation. The R03 incremental manifest targets V58, not the supplied original. No GitHub action or binary modification. Older FPS/crash-oriented paragraphs below are historical, not the current work queue.


## Input identities

SHA-256 identifies the supplied artifacts; it does not authenticate their publisher or establish safety.

| Artifact | SHA-256 | Bytes, where recorded |
| --- | --- | ---: |
| Supplied original reference | `b685c0f98b15597fb9eabb6d09758a2637246198a1af24a044c2010953fb80ab` | 17,213,264 |
| R03 | `d1a05ff2d8164ec326898d3d2d9709fb638f85d8550436f8e5d9c845be54b292` | 17,262,416 |
| V58 historical identity | `eb87d6e69a031b6f2fbd4845d904dc9dc132468d1c24852b8384e0e12522e8d4` | — |
| R01 historical identity | `fd81099a1fb7b1a5e9a2c2fc22ba55edf408e8b6267412ea5698e1b6bfcefda5` | — |
| P01 historical identity, not a restoration | `42235fabcc45041029730407901fca32c37709edca59af8fbcc5c43f5b0ff80c` | — |
| Supplied game executable identity | `beb866fd0272889b829931df0e50d891c14503cd5b81d85a9ca73ce52f5a032c` | 178,901,616 |

Only original and R03 are required by the included bounded tests. No binaries or download locations are distributed.

## Structural coverage versus semantic coverage

The earlier indexing pass recorded:

| Item | Count |
| --- | ---: |
| Function boundaries | 69,613 |
| Direct call sites | 131,229 |
| Cross-function tail branches | 345 |
| Indirect branch/call sites | 3,459 |
| Conditional branches | 23,337 |
| Initializer roots | 13 |
| Changed original function ranges compared against R03 | 63 |

These are structural indexing counts, **not** complete semantic traces or proof every runtime target is known. Changed original text bytes were counted as 23,444; header changes as 1,617 bytes; added file bytes as 49,152. Relocated LINKEDIT content compared identical in that pass. Byte accounting/reversibility does not prove each change necessary, minimal, behaviorally equivalent, or beneficial.

## Scope of the original route

The recovered outline includes initialization, lifecycle readiness and epoch/generation invalidation, coalesced worker requests, result/state handling, activation, main-thread callbacks, UI/data collection, rendering/presentation, queued input, and failure/recovery. The route has multiple readiness checks, callbacks, and failure exits, not one universal success branch.

Earlier local tests were reported as 3,718 scoped cases: 1,536 state-mutator comparisons, 2,074 classifier/adapter cases with modeled backend status, six once-start/thread-creation cases with modeled pthread operations, and 102 UI cases. Those older tests are not republished here, and their counts do not establish authenticated validation, successful iOS launches, or full behavior. Operational bypass/trust material is intentionally excluded.

The repository includes only the two most recent benign continuation passes: 144 lifecycle/scheduling cases and 150 geometry/layout/reentry cases. The 294 local cases were rerun after portable packaging. Do not combine historical and current counts into a claim of independently covered end-to-end paths.

## Unresolved boundaries

- Genuine validation-to-state transitions and real backend behavior.
- Complete worker/engine/data graph and indirect/runtime callbacks.
- Producer of a secondary setup request word.
- Lifecycle cancellation, stale callbacks, and actual asynchronous interleavings.
- Render resource acquisition/failure/cleanup across all exits.
- Actual UIKit/ARC/block lifetime, exceptions, gesture arbitration, Metal/GPU behavior, device timing, FPS, and physical touch latency.

No full-framework all-path completion or performance repair has been established.
