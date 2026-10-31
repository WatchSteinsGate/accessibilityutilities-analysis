# Control-byte writers, R03 Float early return and nonempty native rendering

## Provenance and question

- Date: 2026-10-31. Agent: Notion AI, local Python/Capstone/Unicorn; no subagents or GitHub actions.
- Starting state: separate local continuation-l snapshot, derived from previously checked revision `120f87f3cb7341dfcc0afddd01b9646f16727864`. Prior local snapshot preserved. This follow-up is **local and unpublished**; “keep going” does not override the user's explicit GitHub permission rule.
- Question: move beyond global-slot references and empty draw-command lists into actual pointee writers, actual render-state setup and pipeline-cache composition. No diagnostic build, modified input, installer or access-control work.
- Read-only original: 17,213,264 bytes; SHA-256 `b685c0f98b15597fb9eabb6d09758a2637246198a1af24a044c2010953fb80ab`.
- Read-only R03: 17,262,416 bytes; SHA-256 `d1a05ff2d8164ec326898d3d2d9709fb638f85d8550436f8e5d9c845be54b292`.
- Both input hashes checked before/after. All execution is bounded emulation; external providers, synthetic state and manually invoked functions are identified below.

## Outcome

**236 new labels passed. Full local regression: 32 suites / 1565 labels, all 1329 previous retained record values equal.** Counts include build pairs and overlapping/synthetic cases, not independent end-to-end paths.

The key build-specific finding is concrete: **the supplied R03 `FloatView drawFloatWindow` entry at `0x1230e4` returns immediately**. Normal emulated invocation executes only that entry and returns, with no GUI calls, control-byte write or reset-flag clearing. Original executes the full native method under explicit GUI providers. The downstream writer bytes that static scans still find are therefore not evidence of normal R03 execution through this entry. This does not establish runtime loader/code mutation behavior or an FPS cause.

## 1. Pointer-derived writer candidates and native writer tests

Evidence: [bounded mapper](../../tests/continuation-m/map_control_pointee.py), [static metadata](../../results/continuations/continuation-m/control-pointee-map.json), [native/model suite](../../tests/continuation-m/test_control_writers.py), [156 complete records](../../results/continuations/continuation-m/control-writer-tests.json).

### Bounded static map

Starting from the previous retained canonical control-slot loads, follow at most 39 subsequent instructions in the same straight-line block. Track simple register copies/adds; invalidate overwritten registers and stop at calls/branches. Record only accesses to offset zero and argument escapes. This is not full alias/spill/interprocedural/lifetime analysis.

Each build yields four offset-zero access candidates, three writes and three call-argument escapes. Candidate writes:

| Site | Method | Native/model finding |
| --- | --- | --- |
| `0x1230d4` | Float `resetFloatWindowPosition` | Nonnull control receives whole byte 0; reset-position flag is set even with nil control |
| `0x123464` | Float `drawFloatWindow` | Original admitted click writes whole byte 1; normal R03 entry returns before reaching it |
| `0x68702c` | Overlay `menuShortcutTapped:` | Gesture state provider 3 and nonnull control cause whole byte 1 |

Function-entry RET metadata explicitly marks the R03 residual Float writer candidate. Absence of additional mapped writers does not prove no aliases, no other writers, valid lifetime or no free/replacement. The prior owner-allocation/free question remains unresolved.

### Complete native writer bodies — 156 records

- 12 Float reset records: three synthetic input bytes and nil/non-nil control, paired builds. Native reset sets reset-position flag `0x1010c30` to 1 and clears the whole control byte only when nonnull.
- 64 Float draw records: reset flag, Begin result, click result, control nil/non-nil and styles 1/3. Original clears the reset flag after successful modeled Begin, checks the modeled click and sets whole byte 1 for a nonnull pointer. It calls modeled End even after Begin false. R03's ordinary entry performs none of these actions; reset flag and control stay unchanged.
- 72 Overlay shortcut records: gesture state providers 0–5, three input bytes, pointer nil/non-nil, paired builds. State 3 writes 1; other tested states leave the byte unchanged. Exact gesture meaning is not assumed from the number alone.
- Eight manual same-pointer sequential compositions: reset→draw, draw→reset, reset→shortcut, shortcut→reset. In original, reset→admitted draw yields 1; in R03, reset→ordinary draw leaves 0 because draw returns immediately. Other sequences obey native last-writer order in the explicitly staged calls.

GUI/ImGui calls, Begin/click/style and ObjC gesture/ARC are providers. No actual UI delivery, production ordering, changed-pointer occurrence, valid ownership, race or physical input latency is established. Synthetic multi-bit bytes distinguish whole-byte assignment from R03 bubble tap's previously tested XOR of bit 0; they are not evidence that production stores invalid Boolean values.

Original/R03 reset and Overlay shortcut windows match. The Float draw window differs as expected. **A passing expected-discrepancy assertion is not a correctness/FPS claim.** The previous pass's Float texture initializer/loader work concerns different methods; texture setup being reachable does not imply this draw method executes.

## 2. Nonempty render commands — 32 records

Evidence: [source](../../tests/continuation-m/test_render_commands.py), [complete records](../../results/continuations/continuation-m/render-command-tests.json). Actual native render body `0x12e2d0` executes; the selected full window matches between builds.

The prior empty command-list limitation is advanced: synthetic lists now contain normal indexed commands, custom callbacks and reset sentinel commands. Eight synthetic vertices and indices per list keep normal command offsets/counts within supplied buffer capacity. Provider-backed buffers receive actual native-loop memcpy effects; no GPU consumes them.

- Native clipping subtracts display origin, applies framebuffer scale, clamps lower bounds at zero and upper bounds at framebuffer dimensions, and skips empty/inverted/outside clips in tested cases.
- Positive fractional clip extent can truncate to zero integer scissor width/height after passing the positive floating-point extent test. The caller issues that scissor request. Whether a real encoder accepts it is not tested.
- Zero element count skips normal scissor/binding/draw work.
- Nonnull texture issues fragment binding. Nil texture skips that message; in a nonnull→nil sequence, the caller does **not** explicitly clear/rebind the texture. No claim is made about actual sampled GPU state or a production defect.
- Vertex offset uses 20-byte stride; index offset uses two-byte stride and adds previous-list byte totals. Two-list execution verifies second-list copies at +160 vertex bytes / +16 index bytes and matching draw offsets.
- Custom callback dispatch uses the actual native indirect call with list/command pointers, landing in an explicit provider. Reset sentinel invokes render-state setup instead of an indexed draw. This identifies a callback mechanism, not a proven constructor reentry route.

Metal encoder/state/buffer allocation, custom callback behavior and real submission remain modeled. Index capacity checks are not a claim of valid real shader/pipeline execution.

## 3. Actual native render-state setup — 24 records

Evidence: [source](../../tests/continuation-m/test_render_state.py), [records](../../results/continuations/continuation-m/render-state-tests.json).

Replace the previous entire setup provider with actual native `setupRenderState:commandBuffer:commandEncoder:renderPipelineState:vertexBuffer:vertexBufferOffset:` at `0x12de90`. Compose render→native setup→reset sentinel→native setup→normal indexed command→completion registration.

- Native viewport uses framebuffer-scaled display width/height, origin zero, depth 0–1.
- Native 64-byte orthographic matrix is checked for three origins/scales. It uses logical display coordinates, not framebuffer dimensions, and uploads at vertex argument index 1.
- Native caller requests cull mode 0, modeled cached depth state, passed pipeline state, vertex buffer at slot 0 and subsequent byte-offset update.
- Both nil/non-nil depth and pipeline providers are tested. Caller forwards nil state messaging; modeled encoder acceptance is **not** real Metal validation or success.
- Native setup window matches original/R03. ObjC/ARC, getter values and encoder state effects remain providers; no real GPU/ARC execution or performance claim.

## 4. Native pipeline-cache lookup, miss, clear and composition — 24 records

Evidence: [source](../../tests/continuation-m/test_pipeline_cache.py), [records](../../results/continuations/continuation-m/pipeline-cache-tests.json).

Execute native cache caller `0x12c798` and clear body `0x12de18`, both equal across builds. Shader/pipeline creation remains an explicit `_renderPipelineStateForFramebufferDescriptor:device:` provider; its body is not executed.

- Cache hit avoids the creation provider. Successful cold miss inserts; next request reuses it.
- Nil creation result reaches keyed-subscript setter. The explicit dictionary provider treats nil as removal, so later requests retry; failure→recovered provider can subsequently cache. This is not a real Foundation/exception test.
- Clearing removes existing entries and allows a later rebuild. Nil cache getter suppresses effective dictionary operations; creation repeats in the model.
- Synthetic descriptor-key change creates another entry. Same synthetic key with changed device argument reuses the cached entry: this caller's lookup does not separately key by the device. No actual multi-device switch or defect is established.
- Full cold/hit/nil-creation/nil-cache cases compose native render→native pipeline cache→native state setup→nonempty native draw→completion registration. An encoder provider accepting nil pipeline does not mean such a command is valid on hardware.

## Validation and corrections

- Python 3.13.15, Capstone 5.0.7, Unicorn 2.1.4.
- Full runner: all 32 suites / 1565 labels pass; all previous 1329 retained record values equal after normalized JSON keys. [Full summary](../../results/continuations/continuation-m/regression-summary.json).
- New suites: writer 156, render commands 32, render state 24, pipeline cache 24 = 236. Expanded continuation validator expects **1271 records across a–m**, plus 294 base labels.
- New bounded mapper passed. Existing prior static-map records remain historical and unchanged; the old scheduling/root mappers were not rerun in this follow-up.
- Offline intake/publication-metadata validation, Python syntax, relative links, complete curated local inventory/checksums and unchanged input identities checked. Metadata validation does not query live releases/GitHub.
- Important failed assumption: the first writer test incorrectly expected the original Float draw behavior in R03. It failed on missing GUI events; entry inspection showed RET. Tests now assert the build discrepancy and R03's exact two-address visit set (entry and harness return sentinel), rather than patching the binary or forcing original behavior.
- Render inputs were strengthened from initial tiny arithmetic-only buffers to eight-element lists so tested normal offsets/counts fit supplied capacities. Initial arithmetic observations were not retained as purported valid real draw geometry.
- No unknown-call blanket fallback, source edit, real worker or security/backend success seed was introduced.

Reproduction with the prior pinned dependencies and authorized inputs:

```bash
export AU_ORIGINAL="/absolute/path/to/authorized/original/AccessibilityUtilities"
export AU_R03="/absolute/path/to/authorized/r03/AccessibilityUtilities"
for suite in tests/continuation-m/test_*.py; do python "$suite" || exit 1; done
python tests/continuation-m/map_control_pointee.py
python tools/run-native-regression.py
python tools/validate-continuation-results.py
python tools/validate-attachment-intake.py
python tools/validate-original-attachments.py
sha256sum -c SHA256SUMS
```

## Retention, limits and next concrete work

Five new reviewed Python files (four suites and mapper), complete results/map/regression/provenance/validation metadata, this report and updated handoff/navigation/integrity files are local. Raw instruction scratch, input binaries/ZIPs, bytecode and unreviewed logs are excluded from the reviewed-text bundle. No new GitHub revision exists.

Remaining concrete questions: actual control-owner alias/free/replacement chain; original GUI providers and genuine entry/callback reachability; actual decoder and shader/pipeline creation internals; synchronous reentry evidence; real ARC/Metal/thread delivery and physical timing. The pointer map and RET result narrow interpretation but do not prove allocation lifetime or an FPS cause. Continue using existing authorized sources/captures only; do not build a diagnostic/modified release or perform any GitHub action without an explicit new request.
