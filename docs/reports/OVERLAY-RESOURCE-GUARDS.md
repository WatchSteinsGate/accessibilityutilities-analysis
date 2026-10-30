# Overlay initializer resource guards and failed singleton reuse

## Scope and provenance

2026-10-30, Notion AI. Starting revision: `1ebb1a77bc7e3cf7817b8a2666dd8a95318a27c5`. Continues the [initializer effects pass](INITIALIZER-EFFECTS.md). Both authorized input hashes remain unchanged.

Actual native OverlayView factory, once block, initializer resource-guard paths and ten property accessors execute in emulated memory. Inherited MTK initialization, ObjC messages/ARC, allocation, device/queue/loader providers and once completion remain modeled. Successful-resource cases stop at `0x6849f8`, before font/GUI setup: **not a completed successful Overlay initializer or backend run**. Native early failures execute through normal return.

## Findings

### Control publication and properties precede inherited initialization

Initializer `0x684454` publishes the supplied raw control pointer to `0x1011e20`, then assigns Draw/Menu/Float properties before inherited `initWithFrame:`. Their ten selected getter/setter bodies, including commandQueue and loader, execute natively; strong stores and ownership remain modeled. Both zero and nonzero control arguments are covered. This establishes ordering and selected memory effects, not pointee validity, ownership, leak or use-after-free.

### Resource failures return nil at distinct boundaries

The suite forces inherited-init nil, device nil, command-queue nil, loader allocation nil and loader initialization nil. Device failure precedes delegate assignment. Queue/loader failures occur after `setDelegate:self`. The ready prefix sets the command queue and loader properties before the stop. No actual Metal device or GPU work runs.

No explicit delegate-reset message occurs on the tested early-failure routes, but runtime weak-reference behavior, ARC deallocation and UIKit cleanup are not modeled faithfully enough to infer a dangling delegate. Stored synthetic properties after modeled inherited nil likewise do not prove a leak.

### Completed-once nil does not retry after provider recovery

Actual factory `0x68401c` and once block `0x684380` are composed with each of the five native failure routes. Across three sequential factory calls, only the first allocates/initializes Overlay. After the modeled once completes, singleton `0x1011620` remains nil; recovering the providers and changing subsequent control arguments does not retry. Raw control publication remains the first argument. This is a conditional contract under completed-once semantics, not evidence that initialization fails on a device or explains reported FPS/touch symptoms.

### A real original/R03 return-tail difference is preserved

Twelve of thirteen compared windows are equal. The wider return-tail window `0x6854e4..0x68557c` is **not** equal: at `0x6854ec`, original calls `_objc_retain` at `0x876648`, while R03 calls its existing trampoline at `0x1017600`. Both hashes are recorded. The inherited-nil cases traverse this tail, including the R03 trampoline with a nil object; other resource-failure cases do not visit that call. Runtime messages to nil return zero in the model. These selected nil-return results do not establish nonnil trampoline behavior, lifetime equivalence or whole-binary equivalence.

The first test draft incorrectly asserted equality for all thirteen windows and failed after the functional records passed. The assertion was corrected to preserve exactly this observed difference, not to suppress it. A follow-up visited-address assertion also disproved the assumption that every early failure skips this tail; final records explicitly distinguish inherited-nil traversal.

## Reproduction and validation

- [Portable native/model suite](../../tests/continuation-g/test_overlay_resources.py)
- [All 34 labeled records and code-window hashes](../../results/continuations/continuation-g/overlay-resource-tests.json)
- 24 direct initializer cases: two builds, six modes and two control inputs.
- 10 native factory/once failure-then-recovery sequences: two builds and five initial failures, three calls per sequence.

With authorized `AU_ORIGINAL` and `AU_R03` configured:

```bash
python tests/continuation-g/test_overlay_resources.py
python tools/validate-continuation-results.py --group continuation-g
```

Python 3.13.15, Capstone 5.0.7, Unicorn 2.1.4: **34/34 passed**, 12 equal windows and one unequal window. Generated output defaults to `results/generated/continuation-g/`; override with `AU_RESULTS`. Only this new group was executed/integrity-validated; older native suites were not rerun. Present-file checksums, changed-document links, Python syntax, JSON and unchanged input identities were checked. This partial checkout is not a full-repository checksum run or a full 698-record continuation validation.

Stored totals become 698 continuation + 294 earlier = **992 labeled records**, including paired builds, synthetic conditions and repeated calls, not 992 independent end-to-end paths. No binary changes, installer, actual device run, GPU/backend success, race/lifetime proof or performance fix.

## Next boundary

Continue beyond `0x6849f8` through actual font/GUI/backend and size synchronization setup, keeping runtime providers explicit. The late MenuWindow `setOverlayView:` method is not a trivial setter: native global strong storage at `0x1011c88` is followed by additional setup and must be traced as such. Establish control-state replacement/deallocation and pointee writer provenance before claiming a reachable interruption or ownership defect. No actual scheduling or synchronous reentry is established here.
