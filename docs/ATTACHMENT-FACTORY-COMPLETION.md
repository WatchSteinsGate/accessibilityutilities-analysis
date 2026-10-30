<!-- Repository edition: curated from this session continuation; see OMISSIONS.md. -->

# Accepted callback attachment, singleton reuse and render completion

## Outcome and evidence scope

This continuation advances beyond the earlier constructor eligibility prefix into native attachment, the native shared-overlay factory and once block, then native render-completion capture helpers and buffer-cache admission guards.

**210 additional labeled scoped cases passed.** Counts include original/R03 pairs, synthetic faults, repeated calls and staged compositions; they are not independent end-to-end paths or iOS runs.

No framework input was changed. No game executable was downloaded or executed, and no patch, signing, installation, backend login or diagnostic build was produced. The two framework hashes remain:

| Input | SHA-256 |
| --- | --- |
| Supplied original workpack reference | `b685c0f98b15597fb9eabb6d09758a2637246198a1af24a044c2010953fb80ab` |
| R03 | `d1a05ff2d8164ec326898d3d2d9709fb638f85d8550436f8e5d9c845be54b292` |

## 1. What happens after a callback is admitted

**110 cases** in [attachment-tests.json](../results/continuations/continuation-b/attachment-tests.json).

Executed native constructor callback `0x76944` through normal return, with modeled factories, geometry methods, hierarchy effects, ARC counters and synchronization boundaries. The callback selects the original FieldView child or the R03 raw game parent, configures an overlay, queries its superview and conditionally removes/adds it.

Tests start in explicitly seeded eligible state. For staged cases, the native callback is paused at a selected boundary, its register context saved, native suspend/resume mutators executed against the same emulated memory on a separate stack, and callback registers restored before native execution continues. No lifecycle flag or generation is merely faked as a substitute for these mutator instructions.

### Findings

- Once admitted, the tested constructor path does not recheck generation/readiness/active state immediately before attachment.
- Staged suspend or suspend/resume after admission does not prevent completion of the tested configuration/attachment sequence in either image.
- This includes tests after factory return, after the superview query, and between removal and addition.
- If the modeled overlay is already attached to the selected parent, the callback still issues geometry/autoresizing configuration but skips remove/add.
- If detached or attached elsewhere, it issues removal followed by addition to the selected parent. Reaching those messages does not prove UIKit allocations or actual visible behavior.
- The already known original/R03 parent-policy difference persists. With distinct FieldView and raw game objects, the modeled R03 temporary-ownership delta is still FieldView +1 / raw parent −1; original balances in these tests. A test passing here means the expected behavior/delta was reproduced, not that R03 ownership is correct. P01 was not supplied or recreated for this pass.

### Important scheduling limit

A paused native callback with a separate-stack mutation is a **staged composition**, not proof that the real callback can be interrupted at that point. If actual lifecycle work is serialized on the main queue with no relevant reentry, it may not interleave that way. Reachable reentrant routes, scheduler constraints and runtime callback ownership still require evidence before calling this an observed race or defect.

### Synthetic factory-return failures

- Original nil FieldView/last-child sequences exit before overlay attachment.
- R03's raw-parent policy does not depend on those original child lookups.
- A nil overlay factory result is not checked before the later add-to-parent message: the tested path can issue `addSubview:` with a nil child.
- Tests record that attempted call without emulating a UIKit exception. This is not an observed allocation failure, crash or exception diagnosis.

## 2. Native shared-overlay factory: reuse versus allocation

**12 cases** in [factory-tests.json](../results/continuations/continuation-b/factory-tests.json).

Executed the native factory `0x68401c`, native once block `0x684380`, and the initializer prefix through the control-pointer store. The remainder of initialization and Objective-C property implementations are modeled. `dispatch_once` is explicitly staged with modeled completion/token state; real libdispatch and its concurrency are not executed.

The factory/once-block bytes are identical between original and R03.

### Successful first initialization followed by reuse

For three sequential calls with changed geometry, draw/menu/float references and control-pointer arguments:

- One allocation attempt and one initializer-publication-prefix execution occur in the modeled once sequence.
- All three calls return the same overlay identity.
- Every call still sends frame/bounds configuration and draw/menu/float property updates.
- The raw shortcut control pointer remains the first initialized pointer even when later factory calls pass different pointer values.

This strengthens the earlier caution: repeated factory calls do **not** by themselves imply repeated fresh overlay allocation. Reuse also does not imply suppression of repeated configuration work.

The pointer result is conditional on changed inputs. It does not establish that actual callers change that pointer, that the first pointee expires, or that any use-after-free occurs.

### Synthetic first allocation failure

When allocation is forced to return nil and the modeled once execution completes normally, the singleton remains nil. Restoring the allocation provider on later calls does not retry while the once token stays completed.

This is a local synthetic failure contract under the tested normal-completion semantics. Actual allocation-failure behavior, exceptions and libdispatch behavior were not measured. No runtime retry patch was implemented.

## 3. Native factory composed with callback attachment

**12 cases** in [factory-attachment-tests.json](../results/continuations/continuation-b/factory-attachment-tests.json).

The constructor prepares its native factory arguments; the native shared factory/once block/publication prefix runs on a separate stack; native suspend then advances lifecycle state before the native callback resumes after factory return.

- With successful first initialization, three seeded-admitted callbacks reuse one overlay. The first attaches it; later same-parent calls do not remove/add it again.
- The first control pointer remains published while later calls pass other symbolic pointers.
- With synthetic first allocation failure, the completed once sequence remains nil on subsequent calls and the constructor can again attempt a nil-child addition.

This composes more of the route than the earlier fixed-return factory model, but the initializer remainder, hierarchy effects and dispatch runtime remain modeled. Each invocation begins from explicitly seeded eligible state, not an executed genuine activation pipeline.

## 4. Render completion: strong buffers, weak context

**60 cases** in [completion-tests.json](../results/continuations/continuation-b/completion-tests.json).

Static tracing of native `MetalContext renderDrawData:commandBuffer:commandEncoder:` shows registration of a completed-handler block capturing two buffers strongly and the context weakly. This pass executes native helper bodies:

- Copy helper `0x12eea8`.
- Completion invocation `0x12edb8`.
- Dispose helper `0x12ef14`.

The tests manually prepare a source block, execute native capture copy, dispose the source, invoke the copied callback, then dispose the copy. ARC counts and weak-runtime operations are modeled.

### Findings within the model

- The copy helper establishes two strong capture slots and copies the weak context slot.
- Disposing the source does not release the copied capture ownership.
- Invocation loads the weak context separately for the two `enqueueReusableBuffer:` messages.
- Invocation balances temporary command-buffer ownership and temporary weak-load retains; it does not clear the copied strong captures.
- Disposal clears the weak slot and releases both strong capture slots.
- Distinct, aliased and synthetic nil-buffer captures were included.
- Live/live, nil/nil, and forced live/nil weak-resolution sequences were included. The forced live/nil sequence bounds behavior but does not prove the real owner can disappear between those loads under actual lifetimes.

An absent weak context suppresses effective messaging to that receiver, but captured buffer ownership still survives until block disposal in the model. No claim of a leak follows solely from missed cache reuse.

### Still not executed

The native draw loop and real completion-handler registration/copying are not executed end-to-end in these tests. Nor are GPU completion delivery, actual Blocks/ARC/zeroing-weak runtime behavior, command-buffer error status, timing, or concurrent buffer-cache mutation. Reaching a completed-handler registration instruction statically does not prove it is delivered.

## 5. Buffer-cache admission guards

**16 cases** in [cache-guard-tests.json](../results/continuations/continuation-b/cache-guard-tests.json).

Executed native `enqueueReusableBuffer:` entry guards and rejecting normal exits. Accepted cases stop at the cache-body boundary before locking/enumeration/insertion.

- A nil wrapper or nil underlying Metal buffer is rejected before entering the cache body.
- Lengths greater than `0x1000000` (16 MiB) are rejected by the tested unsigned comparison.
- Exactly 16 MiB is admitted, as are the tested smaller values, including zero. Admitted here means only reaching the next cache-body boundary, not successful insertion or reuse.
- Rejecting exits balance the modeled temporary ownership. Accepted-prefix cases intentionally still own their frame-local wrapper because execution stops before its later cleanup.

Underlying buffer/length getters and ARC operations remain modeled. Cache capacity, eviction, locking, insertion, reuse suitability and allocator behavior are not established by these prefix tests.

## 6. Case inventory

| Evidence | Labeled cases |
| --- | ---: |
| Accepted callback attachment and synthetic factory failures | 110 |
| Native factory once/reuse | 12 |
| Factory-to-attachment composition | 12 |
| Completion capture copy/invoke/dispose | 60 |
| Buffer-cache admission/rejection | 16 |
| Total | 210 |

Source scripts, JSON records, final-run metadata and a code-equality inventory are included; raw disassembly and source archives are deliberately omitted. All import boundaries must be modeled explicitly; unknown imports raise errors. Unexpected low-page data reads are rejected. Initializer-prefix ownership is not scored as complete initializer ownership; its unexecuted remainder is explicitly modeled.

## 7. Remaining benign work

1. Establish whether post-admission lifecycle interleavings are actually reachable through relevant runtime callbacks or reentry; do not infer that from staged mutations alone.
2. Trace the shortcut control pointer's actual producer, all consumers/writers and owner lifetime. Native singleton reuse alone does not prove a dangling pointer.
3. Execute/document the backend draw loop and resource-allocation failure routes, plus actual completion registration/copy contracts, without substituting seeded state for runtime evidence.
4. Extend accepted cache-body tracing through enumeration, insertion, eviction and reuse. The prefix limit is not the full cache policy.
5. Resolve the secondary setup-word producer and additional workers/indirect-call coverage.
6. Preserve unresolved genuine backend/security transitions without implementing or extending authentication, trust, anti-cheat or access-control circumvention.

The expanded trace still does not establish literal all-path recovery, patch minimality, actual crash causation, or device FPS/touch-latency improvement. No new install binary was produced.
