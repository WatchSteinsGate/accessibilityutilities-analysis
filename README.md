# AccessibilityUtilities investigation

Private, curated research handoff for a read-only integrity and overlay lifecycle investigation. **This is not a restored original, a performance fix, a patch distribution, or a complete all-path trace.**

## Start here

- [Continuation handoff](docs/HANDOFF.md): current conclusions, user-reported symptoms, decisions, and next steps.
- [Integrity and whole-system summary](docs/INTEGRITY-AND-TRACE.md): input identities, structural coverage, evidence boundaries, and unresolved branches.
- [Overlay lifecycle report](docs/LIFECYCLE-CONTINUATION.md): 144 scoped native-instruction cases.
- [Resize/layout report](docs/RESIZE-LAYOUT-CONTINUATION.md): 150 scoped cases.
- [Omissions and provenance](docs/OMISSIONS.md): what was deliberately not uploaded.
- [Inventory](docs/INVENTORY.md) and [SHA256SUMS](SHA256SUMS): included files and integrity checks.

## What is verified locally

The five included test scripts cover **294 scoped cases** across lifecycle, size-sync scheduling, geometry, added-button layout/cache behavior, and staged reentry. Counts include paired builds, synthetic inputs, and repeated calls, not 294 independent end-to-end launches. Objective-C/UIKit, ownership, journal, and dispatch boundaries are modeled. No real backend, iOS loader, Metal/GPU timing, asynchronous races, device FPS, or physical touch latency is verified.

The original is the **supplied reference workpack**, not independently publisher-authenticated code. Neither input binary is included. The investigation remains incomplete; see the handoff for the next unresolved work.

## Reproduce the bounded tests

Use Python 3 with the pinned dependencies. The repository packaging was rerun locally with Python 3.13, Capstone 5.0.7, and Unicorn 2.1.4; all 294 cases passed. Provide only inputs you are authorized to analyze. The harness rejects files whose SHA-256 differs from the two recorded identities.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
export AU_ORIGINAL="/absolute/path/to/authorized/original/AccessibilityUtilities"
export AU_R03="/absolute/path/to/authorized/r03/AccessibilityUtilities"
for suite in test_view_lifecycle test_size_sync test_geometry test_button_layout test_reentry; do
  python "tests/${suite}.py" || exit 1
done
```

Generated records go to ignored `results/generated/`; set `AU_RESULTS` to select another directory. Checked-in historical records are in `results/lifecycle/` and `results/resize/`; fresh packaging-run records are in `results/portable-run/`. Geometry/button records contain explicitly synthetic NaN/Infinity values using Python JSON numeric extensions; strict JSON consumers may need to normalize these.

Tests execute native instructions in **emulated memory** with stubbed runtime boundaries. They do not patch disk inputs, build a framework, contact a server, install an app, or exercise actual touch/action routing. The selector cache is declarative data, not a patch builder.

## Project boundaries

No credentials, proprietary framework/game binaries, installable bundles, bypass patchers, anti-cheat tooling, or binary download links are included. Earlier bypass-related artifacts and unreviewed historical archives were intentionally omitted, not silently lost. See [the omissions manifest](docs/OMISSIONS.md).

No blanket license is granted to third-party material. This repository does not assert ownership or redistribution rights over any proprietary inputs. Private visibility is not a substitute for authorization.
