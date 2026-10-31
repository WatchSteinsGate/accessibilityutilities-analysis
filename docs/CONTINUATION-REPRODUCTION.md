# Reproduce the continuation groups

Use Python 3 and the existing root `requirements.txt`: Capstone 5.0.7 and Unicorn 2.1.4. The original session runs used Capstone 5.0.9; all nine repository editions were freshly rerun against 5.0.7 and retained their expected case counts.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
export AU_ORIGINAL="/absolute/path/to/authorized/original/AccessibilityUtilities"
export AU_R03="/absolute/path/to/authorized/r03/AccessibilityUtilities"
for group in continuation-a continuation-b continuation-c; do
  for suite in tests/"$group"/test_*.py; do
    python "$suite" || exit 1
  done
done
```

Both input hashes are checked before emulation. Neither disk input is written. Generated results default to ignored `results/generated/continuation-a/` and `results/generated/continuation-b/`. Set `AU_RESULTS` to an alternate directory; use distinct directories per group when retaining a complete run.

Checked-in fresh portable records are under `results/continuations/continuation-a/` and `results/continuations/continuation-b/`, each with a scope and dependency/provenance summary. Formatting was compacted without removing records/values. They represent 232 and 210 labeled cases respectively.

The modules are deliberately isolated per continuation group so earlier five-suite packaging remains untouched. Helper source is loaded from sibling files where needed; no historical workpack, patcher, selector builder or framework-download URL is needed.

## Native versus modeled execution

Read each JSON `scope` and both reports before interpreting green results. The emulator uses unslid native instructions, modeled Objective-C/ARC/weak operations, dispatch/once completion, property effects, mutex/journal boundaries and selected backend providers. Stageable native mutators run on disjoint emulated stacks with saved/restored register contexts. This is sequential composition, not a scheduler or proof that the interleaving is reachable.

Unknown imported calls raise errors; unexpected low-page data reads are rejected. A symbolic external canary binding and modeled UIKit class reference avoid treating unresolved raw-image imports as runtime objects. No real iOS loader/rebasing, UIKit, GPU/Metal execution, race proof, device timing, signing or install occurs.

Raw proprietary disassembly and binary evidence archives remain excluded. The repository editions preserve the reviewed test source, case records, code-equality/reference metadata and findings rather than opaque ZIPs.

## Indexed record parts

Large `*-tests.json` files are `partitioned-v1` indexes. Each lists relative part paths, record counts and SHA-256 values; every original record is retained in the adjacent text JSON parts. Runnable tests still emit ordinary complete JSON into generated results. The checked-in validator verifies both formats. Partitioning addresses connector request limits without publishing opaque archives.

## Scheduling continuation (64 records)

`tests/continuation-c/test_scheduling.py` reuses the existing continuation-b native/parser/emulator modules without modifying them. It sets its own default output directory to `results/generated/continuation-c/`; an explicit `AU_RESULTS` overrides this. Use a distinct output directory for each group. Also run:

```bash
python tests/continuation-c/map_scheduling.py
python tools/validate-continuation-results.py
```

The scheduling pass ran only its new 64-case suite and static mapper with Python 3.13 / Capstone 5.0.7 / Unicorn 2.1.4. It did not rerun the older suites. Its complete records and metadata are under `results/continuations/continuation-c/`. The validator now checks 506 indexed continuation records (442 earlier + 64 scheduling); this is record integrity, not a runtime rerun. Read [the report](reports/LIFECYCLE-SCHEDULING.md) for the explicitly skipped producer body, modeled transition boundary and unresolved runtime scheduling.

## Startup/reentry boundary continuation (58 records)

`tests/continuation-d/` reuses continuation-b helpers and the now-importable `test_attachment.Model`. Running the existing attachment script still executes all 110 original cases; importing its model no longer executes its suite. Set authorized input paths as above, then:

```bash
python tests/continuation-d/test_reentry_boundaries.py
python tests/continuation-d/map_reentry_boundaries.py
python tools/validate-continuation-results.py --group continuation-d
python tools/validate-attachment-intake.py
```

Default generated output is `results/generated/continuation-d/`; `AU_RESULTS` overrides it. New published records live in `results/continuations/continuation-d/`. The 58-case suite and mapper passed with Python 3.13.15 / Capstone 5.0.7 / Unicorn 2.1.4; existing scheduling (64) and attachment (110) suites were rerun. Other suites were not. The new record index retains every record in hashed JSON parts.

Default validator scope now requires 564 continuation records across groups a–d. `--group` explicitly validates one group's expected total in a partial checkout; it is not a full validation claim. Only group d was integrity-validated this pass. See [report](reports/STARTUP-REENTRY-BOUNDARIES.md) for modeled once completion, non-executed observer body at the routing boundary and unresolved actual reentry. The exact [source resize report](source-reports/Resize-layout-continuation.md) is historical, not a replacement for portable reproduction.

## Factory/control-state continuation (54 records)

With authorized input paths configured, run `python tests/continuation-e/test_factories.py`, then `python tools/validate-continuation-results.py --group continuation-e`. Defaults to `results/generated/continuation-e/`; published complete records are under `results/continuations/continuation-e/`. Python 3.13.15 / Capstone 5.0.7 / Unicorn 2.1.4; 54 cases passed, twelve equal windows and one expected producer-window discrepancy retained. Older native suites were not rerun. Full default integrity validation now requires 618 continuation records; only group e was checked this pass. Read [scope and modeled boundaries](reports/FACTORY-CONTROL-PROVENANCE.md).

## Complete Draw/Menu initializer effects (46 records)

Run `python tests/continuation-f/test_initializer_effects.py`, then `python tools/validate-continuation-results.py --group continuation-f`, with authorized inputs configured. Defaults to `results/generated/continuation-f/`; `AU_RESULTS` overrides it. Existing group-e model is now importable without executing its suite; its 54-case regression passed with byte-identical records. New 46 cases and four equality windows passed with pinned dependencies. Only group f was integrity-validated; full default now requires 664 records. See [modeled providers and corrections](reports/INITIALIZER-EFFECTS.md).

## Overlay resource guards (34 records)

Run `python tests/continuation-g/test_overlay_resources.py` with authorized inputs, then `python tools/validate-continuation-results.py --group continuation-g`. Default generated directory `results/generated/continuation-g/`, overridden by `AU_RESULTS`. New 34/34 passed; older native suites not rerun. The default validator now requires 698 records; only group g was integrity-validated. [Scope and preserved return-tail inequality](reports/OVERLAY-RESOURCE-GUARDS.md). Successful prefix stops before `0x6849f8`, not at a complete Overlay/backend success.

## Configuration/font/backend contracts (36 records)

Run `python tests/continuation-h/test_overlay_config.py` and `python tools/validate-continuation-results.py --group continuation-h` with authorized inputs. Default `results/generated/continuation-h/`, overridden by `AU_RESULTS`. Native/model 36/36 passed; resource-guard 34/34 regression rerun byte-identical after import-safe refactor. Older native suites not rerun. Default validator expects 734 records; only group h integrity-validated this pass. [Explicit GUI/font/backend provider boundaries](reports/OVERLAY-CONFIG-FONTS-BACKEND.md). Ready font paths stop before size synchronization; backend-wrapper tests are standalone, not full Overlay/backend success.

## Size/backend/attachment composition (30 records)

Run `python tests/continuation-i/test_overlay_attachment.py`, then `python tools/validate-continuation-results.py --group continuation-i`, with authorized inputs. Default generated output `results/generated/continuation-i/`, overridden by `AU_RESULTS`. New 30/30 and prior 34/36-case regressions passed; historical regression records byte-identical. Other older native suites not rerun. Default validator now expects 764 labels; only group i integrity-validated this pass. [Conditional threading, pre-return stop and modeled providers](reports/OVERLAY-SIZE-ATTACHMENT-COMPOSITION.md).

## Native normal return and Menu INI (31 records)

Run `python tests/continuation-j/test_overlay_return_menu.py`, then `python tools/validate-continuation-results.py --group continuation-j`, with authorized inputs. Default output `results/generated/continuation-j/`, overridden by `AU_RESULTS`. New 31/31 passed; prior 30-case composition rerun byte-identical. Other older native suites not rerun. Default validator expects 795 labels; only group j artifact-integrity validated. [Existing R03 wrapper, modeled class/scheduler operations and Menu state prerequisites](reports/OVERLAY-NORMAL-RETURN-MENU-INI.md). Native normal return is not complete functional initialization or real GPU/device success.

## Bubble callback composition and full regression (22 new records)

Run `python tests/continuation-k/test_bubble_callbacks.py` with authorized inputs. Default output is `results/generated/continuation-k/`, overridden by `AU_RESULTS`. The suite imports earlier models without changing their behavior, starts with cold emulated UI caches, and manually invokes the callback IMPs recorded from native registration. All method additions/UI allocation/class/thread answers and runtime delivery are modeled; no real runtime installation occurs. [Scope and findings](reports/BUBBLE-CALLBACK-COMPOSITION.md).

`python tools/run-native-regression.py` runs all 23 native/model suites with per-group output under `results/generated/regression/`, overridden by `AU_REGRESSION_RESULTS`, and writes `summary.json`. It compares generated record values to retained complete/partitioned records (key-order normalization, preserving synthetic NaN/Infinity spelling); it does not overwrite historical files. Python 3.13.15, Capstone 5.0.7, Unicorn 2.1.4: all 1111 labels passed; the 1089 prior record values matched. New 22-case output was deterministic on repeated runs. [Reviewed summary](../results/continuations/continuation-k/regression-summary.json).

`python tools/validate-continuation-results.py` now checks 817 retained continuation labels across a–k; `--group continuation-k` checks only the new 22. The full checkout and full 817-record validation were checked this pass, unlike previous partial-checkout checkpoints. Both existing static mappers also passed. Native/model execution is still not actual UIKit/main-queue/GPU/device execution or a performance fix.
