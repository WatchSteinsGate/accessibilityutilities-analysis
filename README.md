# AccessibilityUtilities investigation

Private, curated research handoff for a read-only integrity and overlay lifecycle investigation. **This is not a restored original, a performance fix, a patch distribution, or a complete all-path trace.**

## Start here

**Agents: read [AGENTS.md](AGENTS.md) before working.** Report work and add reviewed supporting files directly to this repository; maintain the [agent worklog](docs/WORKLOG.md), reports, next steps and integrity manifests.

- [What changed and what is next](docs/NEXT-STEPS.md): latest success-path tracing checkpoint.
- [Cancellation, render cleanup and shortcut consumer](docs/CANCELLATION-RENDER-SHORTCUT.md): 232 additional scoped cases.
- [Accepted attachment, singleton reuse and render completion](docs/ATTACHMENT-FACTORY-COMPLETION.md): 210 additional scoped cases.
- [Lifecycle queue constraints and routing](docs/reports/LIFECYCLE-SCHEDULING.md): 64 further scoped cases; main-queue routes narrow, but do not settle, the reentry question.
- [Startup registration and reentry boundaries](docs/reports/STARTUP-REENTRY-BOUNDARIES.md): 58 further scoped cases; recovered registration startup provenance, not a proven race.
- [All nine supplied attachments accounted for](docs/ATTACHMENT-INTAKE.md).
- [New-suite reproduction](docs/CONTINUATION-REPRODUCTION.md) and [artifact provenance](docs/CONTINUATION-ARTIFACTS.md).

- [Continuation handoff](docs/HANDOFF.md): current conclusions, user-reported symptoms, decisions, and next steps.
- [Integrity and whole-system summary](docs/INTEGRITY-AND-TRACE.md): input identities, structural coverage, evidence boundaries, and unresolved branches.
- [Overlay lifecycle report](docs/LIFECYCLE-CONTINUATION.md): 144 scoped native-instruction cases.
- [Resize/layout report](docs/RESIZE-LAYOUT-CONTINUATION.md): 150 scoped cases.
- [Omissions and provenance](docs/OMISSIONS.md): what was deliberately not uploaded.
- [Inventory](docs/INVENTORY.md) and [SHA256SUMS](SHA256SUMS): included files and integrity checks.

## What is verified locally

The repository now retains nine investigation groups:

| Group | Labeled scoped cases | Validation |
| --- | ---: | --- |
| Existing lifecycle + resize suites (5 scripts) | 294 | Previously validated; preserved unchanged |
| Cancellation/render/shortcut continuation (4 scripts) | 232 | Fresh portable rerun passed |
| Attachment/factory/completion continuation (5 scripts) | 210 | Fresh portable rerun passed |
| Lifecycle scheduling continuation (1 test + static mapper) | 64 | Passed; rerun in startup pass |
| Startup/reentry boundary continuation (1 test + static mapper) | 58 | Passed in prior publication |
| Factory/control-state continuation | 54 | Passed; rerun after main-guard refactor |
| Complete Draw/Menu initializer effects | 46 | Passed in prior publication |
| Overlay resource guards / failed singleton reuse | 34 | Passed; byte-identical regression rerun |
| Overlay configuration / font guards / backend wrappers | 36 | New scoped run passed |

The configuration/font/backend pass adds **36 records**, bringing the stored total to **1028 labeled cases** (294 earlier + 734 continuation), not unique end-to-end paths. The new 36-case suite and prior 34-case guard regression passed; other native suites were not rerun. The continuation validator now expects 734 records across groups a–h; only group h was integrity-validated in this partial checkout. Native path/IO setup, font guards and standalone backend wrapper returns are covered with explicit provider boundaries. This does not establish a complete successful Overlay initializer or genuine GPU/backend success. [Latest findings and limits](docs/reports/OVERLAY-CONFIG-FONTS-BACKEND.md).

In the prior publication, the **nine scripts / 442 records** were rerun using the repository's pinned Capstone 5.0.7 and Unicorn 2.1.4. The then-resulting **736 stored labeled cases across those three groups** are not 736 unique or independent end-to-end paths. Counts include paired builds, synthetic inputs, repetitions, staged mutations and directly seeded cleanup states. Original session runs of the two new groups used Capstone 5.0.9; the portable rerun used 5.0.7.

Objective-C/UIKit, ARC, dispatch/once semantics, weak-reference results, journal and selected backend boundaries remain modeled. No real backend, iOS loader, Metal/GPU timing, asynchronous race, device FPS or physical touch latency is verified.

The original is the **supplied reference workpack**, not independently publisher-authenticated code. Neither input binary is included. The investigation remains incomplete; see the handoff for the next unresolved work.

## Reproduce the bounded tests

Use Python 3 with the pinned dependencies. The earlier five-suite packaging run used Python 3.13, Capstone 5.0.7, and Unicorn 2.1.4; its 294 records are preserved. The nine new suites passed a fresh portable rerun with those same pinned dependencies; see [new-suite reproduction](docs/CONTINUATION-REPRODUCTION.md). Provide only inputs you are authorized to analyze. The harness rejects files whose SHA-256 differs from the two recorded identities.

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

Generated records go to ignored `results/generated/`; set `AU_RESULTS` to select another directory. Checked-in historical records are in `results/lifecycle/` and `results/resize/`; the earlier packaging-run records are in `results/portable-run/`. New portable results and per-suite scope/validation summaries are in `results/continuations/continuation-a/` and `results/continuations/continuation-b/`; scheduling records/metadata are in `results/continuations/continuation-c/`. Geometry/button records contain explicitly synthetic NaN/Infinity values using Python JSON numeric extensions; strict JSON consumers may need to normalize these.

Tests execute native instructions in **emulated memory** with stubbed runtime boundaries. They do not patch disk inputs, build a framework, contact a server, install an app, or exercise actual touch/action routing. The selector cache is declarative data, not a patch builder.

## Project boundaries

No credentials, proprietary framework/game binaries, installable bundles, bypass patchers, anti-cheat tooling, or binary download links are included. Earlier bypass-related artifacts and unreviewed historical archives were intentionally omitted, not silently lost. See [the omissions manifest](docs/OMISSIONS.md).

No blanket license is granted to third-party material. This repository does not assert ownership or redistribution rights over any proprietary inputs. Private visibility is not a substitute for authorization.
