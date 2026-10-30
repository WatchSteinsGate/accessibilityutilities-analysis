# Overlay lifecycle and layout continuation

## Scope and result

This is a read-only continuation of the whole-system trace, focused on ordinary overlay lifecycle, gesture coexistence, resize scheduling and callback behavior. It does not extend validation, trust, anti-cheat or access-control bypasses and produces no modified binary.

Original and R03 input hashes were rechecked against the handoff. 144 additional scoped native-instruction cases passed: 118 view/gesture cases and 26 size-sync cases. The count includes build pairs and repeated invocations; it does not mean 144 independent end-to-end paths. These tests use native ARM64 instructions with modeled Objective-C/collection/ownership/dispatch boundaries. They do not run iOS/UIKit or genuine asynchronous work.

## 1. Window attachment: cached recognizers, not unconditional recreation

The original `-[OverlayView didMoveToWindow]` at 0x6867c8 calls super, obtains the current window and examines `menuTapRecognizers`. When a nonnil window exists and that property is nil, it creates an array and populates one recognizer from the 16-byte native configuration pair at 0xd60350: five touches required and five taps required. Its target is the overlay and action is `menuShortcutTapped:`. The method sets cancelsTouchesInView, delaysTouchesBegan and delaysTouchesEnded to false, assigns the overlay as delegate, and caches a copy of the array.

It then enumerates cached recognizers. If a recognizer's current view equals the current window, no remove/add is issued. Otherwise, it messages the old view to remove the recognizer and the new window to add it. In the modeled Objective-C semantics, nil receivers are no-ops. A nil window therefore detaches previously attached cached recognizers without discarding the cache; returning to a window reuses them. If no window and no cache exist initially, the static branch skips allocation; that initial condition is not covered by the sequenced cases below.

Tests: 60 executions across original/R03, absent/present initial cache, three prior-view states, and the sequence W1 → W1 → W2 → nil → W2. Each initially absent-cache sequence allocates one recognizer on its first nonnil attachment. Subsequent invocations allocate none in these tests. No repeated attach occurs for the same window. This does not prove allocation behavior of the overlay factory or secondary overlay setup elsewhere.

The two R03 changed instructions in this method enter an observation prologue and an observation branch trampoline. Static disassembly shows the original prologue instruction and both original branch destinations are replayed. These tests execute those trampolines but model the shared journal sink at 0x6e0990, so they do not prove that sink is harmless or register-preserving under all conditions.

## 2. Gesture coexistence and shortcut request semantics

The native simultaneous-recognition delegate returns true when the first recognizer belongs to the cached shortcut array and the second does not. Both members, neither member, or only the second member return false. Eight build-paired membership cases passed. This local return contract is not a claim about every UIKit delegate invocation or system gesture policy.

`menuShortcutTapped:` at 0x686f8c checks recognizer state against numeric value 3 and checks a stored pointer for nonnil. Only then does it write byte 1 through that pointer. It does not locally invert an existing value. Forty-eight state/pointer/initial-byte cases passed across both builds. Treat this as a signal write, not proof of the downstream visible menu outcome; the consumer chain remains outside this pass.

Across the 58 corresponding original/R03 pairs in the three normal-path view/gesture suites, semantic records match after excluding journal-boundary events. The original/R03 delegate and shortcut method bytes are unchanged.

## 3. Layout: original resize dispatch remains, R03 appends another helper

Original `layoutSubviews` calls super and then sends `syncOverlaySize` to self. R03 replaces the second call with a helper that first sends the original message, reloads the saved receiver, then calls its native-button layout helper at 0x1016820. Two native call-boundary cases confirm that ordering. The appended helper's internals, layout reentrancy, work cost and FPS effect are not covered by these tests.

The original `syncOverlaySize` method at 0x6855c0 is byte-identical between the supplied original and R03. This does not make R03's full layout path equivalent because its caller adds work.

## 4. Size-sync scheduling and recursion boundary

`syncOverlaySize` checks `isMainThread` first. Off-main, it constructs a block retaining/capturing self, submits it through the queue-dispatch wrapper and returns. The native block invoke at 0x685b98 reads its captured receiver and sends `syncOverlaySize` again. Static import-wrapper inspection identifies dispatch_async; the queue operand is obtained via the imported main-queue reference. The tests record the constructed block/capture at the dispatch boundary, not actual queue execution.

On-main, the method checks `overlaySizeSyncing`; true returns early, false enters the geometry body. The off-main branch happens before that guard. In the local test, three off-main invocations produce three enqueue requests even when the modeled syncing flag is true. Therefore this method's guard is not an off-main request-coalescing mechanism. This is a local scheduling property, not proof that real callers invoke it frequently or that queued work accumulates on a device.

Twenty-six cases cover both builds, main/off-main and busy/not-busy guard combinations, three invocations, and direct execution of the block invoke. The geometry path is deliberately stopped before its body. Captured-self ownership uses modeled retain/strong operations, not real ARC lifetime or dispatch block copying.

## 5. What remains open

- Execute and validate resize geometry, content-scale/drawable-size updates and zero/invalid bounds handling.
- Trace the R03 native-button layout helper's normal/failure paths and reentrancy without changing input-routing policy.
- Connect the shortcut signal's consumer to presentation under legitimate app state.
- Model lifecycle cancellation interleavings, then distinguish model guarantees from real runtime races.
- Complete render resource-acquisition and cleanup exits; actual Metal/GPU timing remains unavailable locally.
- Full worker fan-out, runtime indirect calls and original validation/backend transitions remain unresolved; this pass does not close them.

No diagnostic build, backend login, signing, installation or new performance claim is produced.

## Reproduction notes (repository edition)

See ../README.md. The two lifecycle scripts now share the portable read-only native environment in tests/. Provide the exact authorized local inputs through AU_ORIGINAL and AU_R03. No input binaries, raw disassembly, historical patch builder, or original path-dependent harness are distributed. This packaging change does not broaden the modeled test scope.

The resize follow-up resolves the first two items in section 5 only within its stated local model; all other limits remain.
