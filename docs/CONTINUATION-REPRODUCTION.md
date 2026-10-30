# Reproduce the two new continuation groups

Use Python 3 and the existing root `requirements.txt`: Capstone 5.0.7 and Unicorn 2.1.4. The original session runs used Capstone 5.0.9; all nine repository editions were freshly rerun against 5.0.7 and retained their expected case counts.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
export AU_ORIGINAL="/absolute/path/to/authorized/original/AccessibilityUtilities"
export AU_R03="/absolute/path/to/authorized/r03/AccessibilityUtilities"
for group in continuation-a continuation-b; do
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
