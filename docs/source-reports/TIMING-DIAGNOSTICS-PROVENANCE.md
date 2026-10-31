# T01/T02 historical diagnostic provenance

## Scope of this review

The two archives were supplied on 2026-10-31. This review reads archive contents, README/manifest declarations and selected validation metadata; it verifies file hashes and archive CRCs. It does **not** run package code, decode a new capture, build/apply a patch, install a framework or independently reproduce the packaged tests. Full identities and dispositions are in the [intake manifest](../../results/source-attachments/2026-10-31-intake.json).

| Archive | Files | Included framework bytes | Disposition |
| --- | ---: | ---: | --- |
| `AccessibilityUtilities-V58-T01-timing-diagnostic.zip` | 17 | 17,262,416 | Historical experimental diagnostic; binary/archive/build/apply material not published |
| `AccessibilityUtilities-V58-T02-collector-timing.zip` | 20 | 17,262,416 | Later historical diagnostic; binary/archive/build/apply material not published |

## Identities must remain separate

Both package manifests declare baseline SHA-256 `eb87d6e69a031b6f2fbd4845d904dc9dc132468d1c24852b8384e0e12522e8d4`. That is the repository's historical V58 identity, **not** the supplied reference workpack identity used by its bounded original/R03 tests. Neither diagnostic is substituted for `AU_ORIGINAL` or `AU_R03`.

Directly hashed framework members agree with their package manifest output hashes:

- T01: `a79b03662abf61ad49b92d9cbd770ac05bca9f41a78fe6e0b745424e6940b8d5`.
- T02: `792db0772e6cf6db488075d4495439ed9deb27698d955425d0c996865c4a7246`.

A matching hash identifies supplied bytes; it is not publisher authentication, a redistribution authorization or a safety guarantee.

## Historical corrections recorded by the sources

T02's README documents two diagnostic defects in T01: overlapping journal/class-cache storage and zero being used as an unset-minimum sentinel. It describes separate journal storage and sample-count-based minimum initialization as corrections. Those are source-reported diagnostic corrections, not proof that the original FPS problem was fixed. T01 minimum fields are not reliable evidence on that account. The existence of this later package does not make its historical test instructions the current project plan.

Both packages include declarations of bounded ARM64 replay validations with clock/runtime boundaries modeled. Their validation metadata marks device validation false. The accompanying historical context discusses an already supplied capture; this intake does not authenticate, re-decode or reproduce it, and does not confuse it with the package authors' local replay validations.

## Measurement limits retained

- Callback spacing is not game/display FPS or GPU completion/presentation timing.
- Observed forwarding-site intervals are not hardware touch timestamps, operating-system queue delay or physical touch-to-photon latency.
- Instrumentation has unmeasured device overhead and can perturb the symptom under study.
- Overlapping stage windows and different sample populations cannot simply be summed into an end-to-end latency.
- Packaged local replay assertions do not establish actual concurrency, loader/signing behavior, unwind safety, a root cause or a device repair.

No proprietary framework, binary delta, builder/apply tool, instrumentation assembly, raw operational disassembly or private capture/export path is copied into this curated narrative. The actual original ZIPs are now separately available as [repository release assets](../../archives/2026-10-31/README.md); the disposition column above records the earlier summaries-only stage, not current absence from GitHub. Existing read-only tracing priorities remain unchanged; no fresh diagnostic-build/capture cycle is requested.
