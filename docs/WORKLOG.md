# Agent worklog

Append a new entry for each meaningful session. Keep older entries intact; correct them through explicit follow-up notes. Technical report structure is in [REPORT-TEMPLATE.md](REPORT-TEMPLATE.md), and the standing workflow is in [../AGENTS.md](../AGENTS.md).

## 2026-10-30 — Published success-path continuation evidence

- Agent: Notion AI, using the connected GitHub tools.
- Starting revision: `d578232168ebff4d00c4e62bd54eae485b7e1540`.
- Published revision: [`9737945145128aa459b265d5deca08357545d165`](https://github.com/WatchSteinsGate/accessibilityutilities-analysis/commit/9737945145128aa459b265d5deca08357545d165), via PR #1 / squash merge.
- Work: added two continuation reports, nine portable suites, 442 scoped case records, indexed JSON parts, provenance/reproduction documentation, an integrity validator, and updated handoff/roadmap/inventory/checksums.
- Evidence: `CANCELLATION-RENDER-SHORTCUT.md`, `ATTACHMENT-FACTORY-COMPLETION.md`, `../tests/continuation-a/`, `../tests/continuation-b/`, `../results/continuations/`.
- Validation: nine new suites passed with Python 3.13, Capstone 5.0.7 and Unicorn 2.1.4; indexed reconstruction checked all 442 records. Existing 294-case suites were preserved, not rerun. The remote checksum-manifest blob matched the staged manifest; only present staged-file hashes were checked locally, not a freshly downloaded whole checkout.
- Publication note: connector request-size limits required staged upload batches on a branch; PR #1 was squashed into one commit on `main`.
- Limits: modeled runtime effects, synthetic inputs, staged mutation and bounded prefix/cleanup tests are not real iOS/Metal/GPU runs, race proof, all-path recovery or an FPS fix. Excluded artifacts remain documented in `OMISSIONS.md`.
- Next: establish reachable post-admission lifecycle interleavings before interpreting staged attachment behavior as a real race.

## 2026-10-30 — Standing agent reporting and artifact workflow

- Agent: Notion AI, using the connected GitHub tools.
- Starting revision: `9737945145128aa459b265d5deca08357545d165`.
- Work: added root `AGENTS.md`, a technical report template and this worklog; linked the agent workflow from README and the next-steps page; updated inventory and checksum entries.
- Required future behavior: report work directly in this repo, commit reviewed permitted scripts/results and supporting files, record omissions/blockers, validate actual changes, maintain next steps and evidence boundaries, and link the published revision.
- Validation: documentation links and changed-file checksums checked locally against the loaded repository state. This is a documentation-only change; no research suites rerun and no new trace cases claimed.
- Limits: `AGENTS.md` is repository guidance, not automatic enforcement or synchronization; external agents must read and follow it.
- Next: the technical priority is unchanged—trace actual queue/notification/reentrant routes between eligibility and attachment; then investigate control-pointer lifetime and backend/cache internals.

## 2026-10-30 — Lifecycle scheduling and notification routing

- Agent: Notion AI, local read-only analysis plus connected GitHub tools. Starting revision: `ba6c9ff8340be1a766996f06ea63caa2d48f9a03`.
- Question: establish queue provenance before treating staged post-admission cancellation as a reachable race.
- Work/evidence: `reports/LIFECYCLE-SCHEDULING.md`, `../tests/continuation-c/`, `../results/continuations/continuation-c/`. Native initialization requests main operation queue for four/eight registrations; constructor/coalesced blocks use imported main dispatch queue. Added 64 cases and a bounded direct-reference/code-equality map. Updated handoff, roadmap, README, reproduction/provenance/omissions, validator, inventory and checksums.
- Validation: Python 3.13 / Capstone 5.0.7 / Unicorn 2.1.4; `python tests/continuation-c/test_scheduling.py` passed 64 cases; `python tests/continuation-c/map_scheduling.py` passed six equal ranges plus one expected changed resume-mutator range; `python tools/validate-continuation-results.py` validated all 506 continuation records. Earlier 442 continuation cases and 294 lifecycle/resize cases were not rerun. Input hashes unchanged; source syntax, local links and staged-file hashes checked, not a full-checkout checksum run.
- Corrections: raw unresolved-class dereference failed in preliminary exploration; final harness uses symbolic class bindings and indirect-symbol import metadata. Broad equality assertion initially included R03-changed resume instructions; narrowed comparisons preserve the expected inequality explicitly. No binary edit.
- Limits: modeled ObjC/ARC/enumeration/dispatch, recorded transition/suspend boundaries, skipped backend producer body and seeded generation. Main-queue operands constrain ordinary delivery; they do not prove runtime reentry absent, a real race present, genuine success, full coverage or a device-performance fix.
- Next: trace synchronous admission-to-attachment callees and remaining lifecycle wrapper/initializer caller contexts for a concrete reentry/off-main writer route; then resolve actual control-pointer owner/lifetime. Publication is grouped on a review branch and squashed when allowed; final revision is available through Git history/PR rather than a self-referential commit hash in this entry.

## 2026-10-30 — Startup registration, direct veneers and source attachment intake

- Agent: Notion AI, local read-only ARM64 analysis and connected GitHub tools. Starting revision: `62d05c2eb1615baef92d0446e5e70c92a3c72805`.
- Question: resolve observer-registration startup provenance and remaining direct lifecycle caller veneers before treating staged cancellation as a real race.
- Work: recovered `0x43850` main enqueue → `0x4388c` callback → `0x438b8` registration producer → once block invoking `0x7aa4c`; followed suspend/transition wrapper chains into the known graph. Native ObjC veneers and rectangle helper add no queue hop; actual custom methods remain modeled. Verified constructor control argument loads from `0x1011b68`, without claiming real input changes or pointee lifetime.
- Evidence: `reports/STARTUP-REENTRY-BOUNDARIES.md`, `../tests/continuation-d/`, `../results/continuations/continuation-d/`. Added 58 new cases, ten equal code/data windows and nine selected direct edges per build.
- Inputs: original/R03 hashes match prior identities before and after analysis. All nine attachments accounted for by seven unique hashes; three original workpacks are identical. Exact supplied resize report preserved, unsafe/mixed archives and framework binaries omitted explicitly. See `ATTACHMENT-INTAKE.md`.
- Validation: Python 3.13.15 / Capstone 5.0.7 / Unicorn 2.1.4. New suite 58/58; scheduling rerun 64/64 and mapper passed; refactored attachment suite 110/110. Group-d record reconstruction, intake/report hashes, Python syntax, changed-document links and all present staged hashes checked. Other suites and full 564-record/full-repository checksum validation not run. `test_attachment.py` only gains an executable main guard for reusable model imports; behavior/regression result contents preserved.
- Corrections: a direct initializer-caller search missed the block invoke route; following the global block recovered it. An exploratory broad data scan stopped at a zero-fill section and is not used as exhaustive evidence.
- Limits: dispatch/once completion, ObjC/ARC/hierarchy and secondary setup modeled; no actual scheduler, UIKit reentry, backend success, GPU/device execution, race proof or FPS/touch fix. Native input files unchanged. Historical source copies/reruns do not add new case counts.
- Next: trace actual synchronous custom factories/initializers and other state writers; then resolve real control-pointer producer/owner lifetime. Publish reviewed artifacts on the analysis branch with a PR; verify the published revision before handing off.

## 2026-10-30 — Native factories and control-state allocation/publication

- Agent: Notion AI, local read-only ARM64 analysis. Starting revision `cb50b04337c2174f01bd4a3faabfcb4f6e755cc1`. GitHub work kept to a single compact publication, without a staging-branch/PR cycle.
- Advanced actual DrawWindow/FloatView/FieldView/MenuWindow factory + once-block composition; full FloatView/FieldView init normal/nil-return bodies, DrawWindow prefix only, MenuWindow initializer modeled. Found control-slot producer allocating 256 bytes through `__Znwm`, initializing selected fields and publishing `0x1011b68`; existing-slot/repeated excerpt reuses it. Enclosing producer/backend not executed.
- Evidence: `reports/FACTORY-CONTROL-PROVENANCE.md`, `../tests/continuation-e/test_factories.py`, `../results/continuations/continuation-e/factory-tests.json`.
- Validation: Python 3.13.15 / Capstone 5.0.7 / Unicorn 2.1.4, new 54/54 native/model cases, thirteen window comparisons (twelve equal, one expected unequal producer excerpt), new-group record integrity, Python syntax, changed links and present-file checksums. Original/R03 hashes unchanged. Older native suites and full 618-record/full-repository integrity not rerun.
- Corrections: nesting emulation inside active import hooks exhausted an instruction bound; replaced with explicit pause/run/restore/resume between emulator calls. Blanket producer equality failed; retained and asserted its revision discrepancy explicitly. No binary changed.
- Limits/next: modeled ObjC/ARC/once/allocation/UI/subobject boundaries; producer is a bounded local excerpt, not genuine backend success. No lifetime/race/device-FPS proof. Next trace deallocation/replacement and pointee writers, then actual MenuWindow/OverlayView initializers and DrawWindow remainder. Raw instruction/reference scratch files remain unpublished.

## 2026-10-30 — Complete Draw/Menu initializer effects

- Agent: Notion AI; starting `29e4e16cc5f99b7f4c89fcfcc78025b322202088`. Local read-only native work; compact direct publication, no PR cycle.
- Extended DrawWindow past its old control-store stop through native setup/local state writes and size reset. Executed full MenuWindow normal/false/nil-return body with path/filesystem/INI providers modeled. Native file-creation false is ignored; configuration effects precede inherited init, including late nil. Composed both native factories/once blocks with these complete initializer bodies, bounding repeated work in the modeled sequential sequence.
- Evidence: `reports/INITIALIZER-EFFECTS.md`, `../tests/continuation-f/test_initializer_effects.py`, `../results/continuations/continuation-f/initializer-tests.json`.
- Validation: Python 3.13.15 / Capstone 5.0.7 / Unicorn 2.1.4; new 46/46 cases, four equal ranges. Existing factory suite 54/54 rerun; record output byte-identical after main-guard refactor. New-group integrity, Python syntax, changed links, present hashes and input identities checked. Other native suites, full 664-record validation and whole-repository checksums not rerun.
- Correction: initial test assumed file creation false aborts. Unbound raw class references also suppressed modeled provider calls; explicit symbolic selector-provider bindings plus the native branch trace established continued INI/inherited-init execution. Preserve false/nil behavior as scoped evidence, not actual runtime failures or an FPS cause.
- Limits/next: real ObjC/ARC/once/Foundation/INI/inherited callbacks, exceptions, Overlay initialization and heap lifetime/writers remain unresolved. No actual filesystem writes, binary modifications, backend/device runs, race proof or performance fix. Continue Overlay initializer and deallocation/replacement/pointee writer tracing.

## 2026-10-30 — Overlay resource guards and failed singleton reuse

- Agent: Notion AI; starting `1ebb1a77bc7e3cf7817b8a2666dd8a95318a27c5`. Local read-only analysis with compact direct publication; no PR cycle.
- Executed native Overlay resource-failure paths and ten property methods, then actual factory/once failure-recovery sequences. Completed-once nil does not retry despite modeled provider recovery. Raw control/property stores precede inherited init; delegate assignment precedes queue/loader failures. Ready prefix deliberately stops before `0x6849f8`.
- Evidence: [report](reports/OVERLAY-RESOURCE-GUARDS.md), `../tests/continuation-g/test_overlay_resources.py`, `../results/continuations/continuation-g/overlay-resource-tests.json`.
- New 34/34 passed with Python 3.13.15 / Capstone 5.0.7 / Unicorn 2.1.4. Older native suites not rerun. Group-g record integrity, changed links/syntax/JSON, present hashes and input identities checked; no full 698-record or whole-repository run.
- Corrections: initial blanket byte-equality assertion failed on the real return-tail call difference. Retained both hashes and coverage evidence: inherited-nil visits the existing R03 trampoline with nil. Twelve windows equal, one unequal; no whole-binary equivalence claim.
- Runtime/ARC/Metal/once boundaries modeled. No device failure, dangling pointer/delegate, lifetime/race proof, genuine backend success or FPS/touch improvement established. Next: remaining font/GUI/backend/size setup, nontrivial Menu backreference setter and state writers/deallocation.

## 2026-10-30 — Configuration/font/backend continuation

- Agent: Notion AI; starting `fa1acfb4f7641e48dbcb7a109e37748127b977b9`. Local read-only work, compact direct publication.
- Extended native Overlay setup past the resource stop through Documents/imgui.ini path, IO flag/filename stores and native font-config constructors/required-result guards. Explicitly modeled GUI compatibility/context creation and font-add boundaries. Native backend initializer/helper executed separately with registration/device-object boundaries modeled.
- New 36/36 passed, six equal code windows. Prior 34/34 resource-guard regression byte-identical after import-safe entry point/optional stop refactor. Other native suites not rerun. Group-h integrity, changed links/syntax/JSON, present hashes and input identities checked; no full 734-record or whole-repository run.
- Findings: failed creation and nil UTF8/duplicate do not return early here; first/third fonts are required while intermediate merge result is not checked. Backend wrappers publish flags/name and return true even under zero modeled subordinate results; not genuine backend-success evidence.
- Evidence: [report](reports/OVERLAY-CONFIG-FONTS-BACKEND.md), `../tests/continuation-h/test_overlay_config.py`, `../results/continuations/continuation-h/overlay-config-tests.json`.
- Initial unmodeled retainAutorelease import failed closed; added explicit identity ARC boundary without lifetime claims. No binary edits, actual filesystem/GUI/GPU/device run, race/lifetime proof or FPS/touch fix. Next: actual size synchronization, attachment checks, late nontrivial Menu backreference and control-state writers/deallocation.

## 2026-10-30 — Size/backend/attachment composition

- Agent: Notion AI; starting `8889c84899a5dafb5f1addc94d466fad8eda540d`. Local read-only composition, compact direct publication.
- Native ready initializer, native size sync and display writes, backend wrappers, optional child routing and actual Menu setter guard paths composed to pre-return stop 0x6854a8. Forced off-main enqueues size work while subsequent setup continues; actual captured block manually drained under modeled main-thread state. This is not proven reachable startup or a race. Native Menu publishes global reference before device/cache/decode guards and reaches modeled readIniConfig.
- New 30/30 passed, three equal selected windows; prior 34/34 and 36/36 rerun with byte-identical records after adding optional child arguments to shared model. Other older native suites not rerun. New-group integrity, changed links/syntax/JSON, present hashes and input identities checked; no full 764-record or whole-repository run.
- Corrections: rejected scale provider corrected to actual nativeScale selector; regression caught accidental factory-call substitution during parameterization and restored default arguments. No native input edited.
- Evidence: [report](reports/OVERLAY-SIZE-ATTACHMENT-COMPOSITION.md), `../tests/continuation-i/test_overlay_attachment.py`, `../results/continuations/continuation-i/overlay-attachment-tests.json`.
- Limits/next: ready caller not run through final return; nonnil R03 instrumentation, successful Menu texture/non-null INI, actual child callbacks, runtime lifetime/scheduling and control writers remain open. No actual GPU/device run, ownership/race proof or FPS/touch fix.

## 2026-10-30 — Native normal return and Menu INI application

- Agent: Notion AI; starting `3c48d6b68e5631bea93b49e1e57733eaf6979403`. Read-only local analysis, compact direct publication.
- Executed final native Overlay cleanup/normal return including existing R03 wrapper/helpers, preserving unequal return window. Actual factory/once/normal-return reuse retains singleton and first control. R03 runtime method-add/lookup/main-thread request boundaries modeled; no methods actually installed and requested bubble callback not executed.
- Executed native Menu nonnil-INI guard, defaults and state-apply helper chain with modeled integer reads/preinitialized state/no-op readIniConfig. Native applied flag prevents repeat reads in tested sequences, not arbitrary callback mutation.
- New 31/31 passed; two equal and one unequal compared windows. Prior 30/30 composition regression rerun byte-identical; older native suites not rerun. Pinned dependencies restored. New-group integrity, changed links/syntax/JSON, present hashes and input identities checked; no full 795-record or whole-repository run.
- Initial newly reached factory frame/autoresizing messages failed closed; added explicit modeled callbacks to new suite only. No shared harness or binary modifications.
- Evidence: [report](reports/OVERLAY-NORMAL-RETURN-MENU-INI.md), `../tests/continuation-j/test_overlay_return_menu.py`, `../results/continuations/continuation-j/overlay-return-menu-tests.json`.
- Next: requested bubble callback and successful Menu/child texture routes, actual control writers/lifetime, real GUI/GPU/scheduling and performance. Normal native caller return is not genuine backend/device success; no race/ownership proof, root cause or FPS/touch fix.

## 2026-10-31 — Reattached source intake and reviewed historical context

- Agent: Notion AI, local read-only attachment inspection and connected GitHub tools. Starting revision: `ab2f2a7f3c00152ae88cf41e5c631d69eb868369` on `main`.
- Request: organize newly supplied files and update the repository in its existing curated format; no new native research/build/capture requested.
- Work: accounted for all 11 occurrences / 10 unique identities; eight occurrences match seven earlier source identities; T01, T02 and the context TXT are new to the manifest. Original workpack copies match each other. Rechecked original/R03/R01 framework identities and T01/T02 members against package output declarations. Preserved prior intake/report history without duplicate uploads.
- Added: `source-reports/SESSION-CONTEXT-THROUGH-R03-REVIEWED.md`, `source-reports/TIMING-DIAGNOSTICS-PROVENANCE.md`, `../results/source-attachments/2026-10-31-intake.json`. Extended the intake validator; updated intake/navigation, handoff/next steps, omissions, inventory and checksums.
- Validation: all nine ZIP member CRC checks passed; attached standalone resize report matches the existing recorded source hash; T01/T02 baseline declarations kept distinct from supplied original/R03 inputs. Both intake manifests and retained narrative hashes checked with `python tools/validate-attachment-intake.py`; Python syntax, changed-document link targets against the repository manifest, inventory coverage and all present staged-file hashes checked. Inventory validation caught and excluded a generated bytecode cache before final staging. This is a partial staged-file integrity check, not a full-checkout checksum run.
- Limits: no attachment code executed, no native/replay suites rerun, no new trace records, no device/GPU/performance result. Diagnostic validation claims remain attributed to their source metadata. Opaque archives, proprietary frameworks, raw mixed session/capture exports and patch/build/apply/security material are omitted, not silently claimed uploaded.
- Next: retain authorized source attachments separately and continue the existing bounded native callback/texture/control-lifetime questions. The historical context does not supersede the later technical checkpoint. A single-payload publish was rejected by the connector confirmation limit of 65,536 bytes before any repository write. Publication uses a staging branch and upload batches for one reviewed final change; its exact revision is available through Git history rather than a self-referential hash here.
