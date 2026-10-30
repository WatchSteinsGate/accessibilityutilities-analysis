# Resize geometry and R03 layout-helper continuation

## Result and scope

150 additional scoped cases passed: 110 original/R03 geometry cases, 35 R03 button-layout/cache/clamp cases, and 5 staged one-level reentry cases. Counts include paired builds, synthetic failure inputs and repeated invocations, not 150 independent end-to-end executions. Both supplied input SHA-256 hashes were rechecked against the handoff. No framework or game binary was modified, signed, installed or executed on a device.

This pass concerns ordinary resizing, UI lifecycle and numerical robustness. It does not extend authentication, trust, anti-cheat or access-control bypasses.

## 1. Original size selection and change suppression

The original `syncOverlaySize` body at 0x6855c0, unchanged in R03, now has native-instruction tests through its normal geometry and publication paths, not just the earlier scheduling boundary.

- It takes screen `nativeScale`; a nil screen or a nonpositive/nonfinite scale selects 1. The native finite check compares absolute value against infinity.
- It uses overlay bounds first, then frame when a dimension is nonpositive, then screen bounds when frame dimensions are nonpositive. Origin does not affect the selected dimensions.
- It multiplies dimensions by the selected scale and orders ordinary finite positive outputs with the larger side first. It does not round fractional dimensions in this code.
- It treats content scale as unchanged when absolute difference is strictly below 0.01. Drawable dimensions are treated as unchanged when both absolute differences are strictly below 0.5. The modeled cases cover below/over scale tolerance and below/exactly-at/over drawable tolerance.
- When either property needs updating, it sets `overlaySizeSyncing` true, applies only the changed property setters, then clears the flag on the normal path.
- Even if neither setter is needed, it still reaches the size-publication helper. With a valid modeled context, that helper writes converted float dimensions and resets the framebuffer-scale pair to (1,1).

All 55 corresponding per-build geometry records matched between original and R03, including the synthetic edge outcomes. This does not make the complete layout paths equivalent: R03's caller still appends its button helper.

## 2. Invalid geometry: setter path and publication path differ

These are inherited original behaviors, reproduced in R03, not newly introduced R03 differences:

- If all dimension sources are zero, the normal setter path can issue drawableSize=(0,0), while the publication helper refuses nonpositive dimensions and leaves its previous display-size/framebuffer-scale values intact.
- The bounds/frame fallback comparisons do not form a complete finite-value check. Synthetic NaN or infinite dimensions can reach the modeled drawable setter. The publication helper rejects nonfinite double inputs and retains the previous published values.
- A synthetic finite-double dimension outside float range passes that helper's double-finiteness check, then overflows to infinity when converted to the stored float representation. The test input used an unrealistically large finite dimension; this demonstrates a type-conversion boundary, not evidence of a real device state.
- In the stateful zero → valid → repeat-valid sequence, publication recovers once positive finite dimensions arrive. The last repeat avoids both setters while still publishing valid output.

These tests establish issued messages and native memory writes under modeled Objective-C responses. They do not establish whether UIKit accepts, clamps, rejects or throws for an invalid drawable size; they do not establish that any invalid value occurred in the user's captures. No FPS or crash cause is assigned from these cases.

## 3. Added R03 helper: cache is keyed to owner identity

The R03 helper at 0x1016820 is an installer plus layout operation, rather than only a geometry updater. Its initialized selector/class-cache precondition is modeled explicitly; action dispatch and touch policy are not exercised or changed.

- A nil receiver or an off-main call returns without issuing UI work.
- With the same cached owner and a nonnil button, it reuses the button, reads its center and owner bounds, optionally sends setCenter, then sends bringSubviewToFront. It does not allocate another button or recognizer in this path.
- With a different owner, it removes/releases the cached button, attempts a new button, configures it and its optional pan recognizer, attaches it, then performs layout. In modeled A → A → B → B → A sequences, button creation attempts are [1,0,1,0,1]. This does not prove actual callers alternate owners.
- If replacement-button creation fails, the old button has already been removed and cleared, but the cached owner field still identifies the old owner. A subsequent call with that old owner skips creation because the owner matches even though the button is nil. A later different-owner call can retry successfully. This was produced by a synthetic allocation-failure sequence, not observed real allocation failure.
- If the same-owner button was externally detached, this helper does not send addSubview on that reuse path; it only attempts its usual clamp/front messages. Actual UIKit behavior for the front message to a detached child is not modeled as proof of reattachment.
- Failure to allocate the pan recognizer does not prevent the modeled button-attachment path. The tests do not assess real gesture availability or usability after that failure.

## 4. Native clamp boundaries and repeated work

The clamp at 0x1016ab0 preserves a 32-point inset for a 64-point button when ordinary finite bounds are at least 64 points on both axes. Tests cover nonzero bounds origins and exactly-64 dimensions. Smaller, zero, negative, or tested NaN dimensions skip setCenter, though the outer installer still sends bringSubviewToFront for a cached button.

For valid unchanged bounds and center, three calls each still send setCenter and bringSubviewToFront. Thus same-owner reuse avoids construction, but does not suppress all repeated layout messages. The code also lacks comprehensive finite checks on all origin/center inputs: tested NaN centers and infinite origins can remain nonfinite. This is a numerical boundary, not evidence that UIKit supplies those inputs in normal operation.

## 5. Bounded native reentry composition

Five tests pause after a modeled setter, save the CPU context, execute one nested native invocation on separate emulated stack space sharing the same memory, restore the outer CPU context, and resume it. This is controlled single-thread composition, not actual UIKit callbacks or concurrency.

- Four build/setter cases interrupt setContentScaleFactor or setDrawableSize. The original native syncing flag is already true; a nested native `syncOverlaySize` returns without further setters, and the outer normal path later clears the flag.
- One cached-button case interrupts setCenter and invokes the added layout helper once. That nested invocation is not suppressed: it sends another setCenter and front message without construction. The resumed outer invocation completes its own front message.

This establishes that the original resize guard is scoped to the original method; it is not a blanket guard for the added helper. It does not prove that setCenter triggers layoutSubviews on a real device, that callbacks recurse without bound, or that this causes the reported slowdown. Exception/throwing setter paths, real ARC/block ownership and asynchronous races remain untested. A first staged-test harness attempt incorrectly demanded a completed helper return at an intentional pause; the pause check was corrected without changing any binary input.

## 6. Evidence and remaining scope

- `geometry-tests.json`: 110 cases; native numeric helpers, setter selection and output writes.
- `button-layout-tests.json`: 35 cases; modeled cache/owner/allocation states and native clamp instructions.
- `reentry-tests.json`: 5 staged reentry cases.
- `summary.json`, `SHA256SUMS.json`: counts and exact input/artifact identities.
- Disassembly and selector labels accompany the test scripts. Scripts depend on the retained `audit/` binary inputs/dependencies and previous lifecycle model at its recorded path. No input binaries or historical patch builder are included. The button test only reads literal selector/class lists from that builder source; it never runs it.

The tests are unslid local execution with modeled Objective-C and UI/ownership boundaries, not real UIKit/Metal, gesture arbitration, performance measurements or backend launches. Evidence JSON uses Python's NaN/Infinity numeric extensions for explicitly labeled synthetic edge cases.

Next work: lifecycle cancellation and stale queued-callback composition, render resource failure/cleanup exits, and the shortcut signal's consumer under legitimate state. Broader worker fan-out, runtime indirect branches, secondary setup-word producer and genuine backend transitions remain unresolved. Full-framework all-path completion and device FPS repair are not established.
