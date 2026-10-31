# Original success path and patch minimality

## Result

**The supplied R03 cannot currently be certified as the minimal, original-functionality-preserving patch set.** This is not a recommendation to remove every unexplained change. Two bounded native comparisons reproduce original behavior that R03 does not preserve. The whole-image ledger also shows that the incremental R03 manifest is not a description of all changes from the supplied original.

The current question is **the original success path and the smallest justified changes needed to preserve intended functionality**, not FPS or crash diagnosis. No GitHub action, new capture/build, binary modification or patch application occurred.

## Provenance and question

- Date: 2026-10-31. Agent: Notion AI; local Python/Capstone/Unicorn analysis.
- Starting state: unpublished local continuation-m, following historical published revision `120f87f3cb7341dfcc0afddd01b9646f16727864`. This copy has no Git metadata; it is not a new published revision.
- Original SHA256: `b685c0f98b15597fb9eabb6d09758a2637246198a1af24a044c2010953fb80ab`.
- R03 SHA256: `d1a05ff2d8164ec326898d3d2d9709fb638f85d8550436f8e5d9c845be54b292`.
- R03 archive SHA256: `dc887be38e6753c3a5316149e2a0b74463a850a4929df7f9cc59a93c962ed583`.
- Archive JSON is an untrusted declaration checked against supplied bytes. No archive script was imported or executed. Inputs remain read-only.

## Whole-image accounting: not just seven initialization calls

[Read-only scanner](../../tools/audit-success-path-delta.py) and [complete structural ledger](../../results/success-path-audit/original-r03-delta-ledger.json):

| Item | Finding |
| --- | --- |
| Declared incremental baseline | V58 SHA256 `eb87d6e69a031b6f2fbd4845d904dc9dc132468d1c24852b8384e0e12522e8d4`, not the supplied original |
| Incremental declared sites | 10; all match supplied R03 output bytes |
| Original-site comparison | Nine old-site declarations match supplied original locally; the appended-area storage-separation site does not. This is not whole-baseline identity. |
| Original function-start ranges changed | 63, comprising 23,444 changed bytes in original text |
| Manifest overlap | Only five changed original ranges contain incremental sites; 58 ranges are not individually explained by this incremental manifest |
| Loader prefix | 1,617 changed bytes in the 4,984-byte compared prefix; original command end 4,680, R03 end 4,984 |
| File growth / appended sections | 49,152 bytes; appended code 32,768 bytes and data 16,384 bytes |
| LINKEDIT | Equal between supplied inputs |
| Original initializer roots | All 13 pointers and root function ranges unchanged; downstream behavior is not thereby proved |

The ten incremental obligations are the callback guard, late-lifecycle frame guard, separation of journal/class-cache storage, and seven local initialization calls. Successful byte matching establishes application identity, not necessity or harmlessness. The V58 executable is unavailable locally. Historical segment names do not establish the active feature set. No missing baseline was fetched.

The [63-row necessity ledger](../../results/success-path-audit/PATCH-NECESSITY-LEDGER.md) and [machine-readable obligations](../../results/success-path-audit/patch-necessity-ledger.json) classify each changed original range. **Necessity and safe removal remain unproved**, including rows with bounded matching behavior. Unknown does not mean removable.

## Original success path: what is recovered and what remains open

[Sixteen-node evidence graph](../../results/success-path-audit/original-success-obligations.json) distinguishes structural, native/provider-backed and unresolved edges:

1. Original initializer roots → main-queue startup registration → application/scene observers and readiness reevaluation.
2. **OPEN:** genuine work/readiness producer, worker and indirect results. Manually seeded eligibility is not evidence that this transition succeeds.
3. Generation-capturing construction request → original admission checks → shared Draw/Float/Menu/Field/Overlay factories and shared control.
4. Native initialization/configuration/resource callers → original Field-child hierarchy, layout and input policy, with runtime/resource providers where documented.
5. Admitted native frame → Float GUI/control update → Draw processing and conditional Menu in the same frame → native render state/cache/commands → endEncoding → presentDrawable → commit.
6. Native completion helpers/cache behavior are bounded; actual callback delivery remains a runtime boundary.

This is **not one validated startup-to-presentation trace**. In particular, original Draw processing at `0x4a130` (F014, directly called by original Draw at `0x111bc`) is not fully recovered. F059 at `0x6db424` contains 20,723 changed bytes and remains semantically unresolved; its size or candidate callees are not enough to name its purpose. No security/backend result is replaced with a successful stub and promoted to genuine success.

## Preservation witness 1: original Float click → same-frame Menu

[16 complete records](../../results/continuations/continuation-n/original-success-contract-tests.json), [test](../../tests/continuation-n/test_original_success_contract.py), related [native writer findings](CONTROL-WRITERS-NONEMPTY-RENDER.md).

The native Overlay frame executes the actual native Float method against the same control pointer. With Float enabled, Menu initially closed and a modeled GUI click, the original invokes its GUI, writes control bit zero to one, and subsequently calls Menu in that same native frame. R03's Float entry returns immediately: no Float GUI event, no control update, and no corresponding Menu call in this state. Menu-open, hide and click combinations are retained separately.

Both builds can reach encoding/presentation/commit under the supplied providers. **Reaching commit does not preserve the omitted UI interaction.** Draw/Menu processing, graphics resources and GUI answers remain modeled; this witness is native caller/Float composition, not a device touch or GPU observation. Expected divergence passes are explicitly distinguished from preservation.

## Preservation witness 2: original self-hit pass-through

[24 complete records](../../results/continuations/continuation-n/original-input-contract-tests.json), [test](../../tests/continuation-n/test_original_input_contract.py).

Original `hitTest:withEvent:` converts a super-result equal to the overlay itself into nil, preserving pass-through; nil and child results remain unchanged. Supplied R03 returns the overlay itself when a control pointer is present and the Menu-open bit is set. The paired matrix finds exactly one differing R03 record: self result + pointer present + Menu open. The original/R03 native bodies and R03 trampolines execute; Super, event/point input and ARC are explicit providers.

This can be an intentional modal policy, but it is **not original-equivalent input behavior**. No user-approved behavioral exception has been assumed.

## Minimality decision rule and other unresolved dependencies

For each proposed retained change, require (a) a named intended behavior or accepted exception; (b) a legitimate original-path precondition; (c) a demonstrated failure without the change and success with it under the same inputs; (d) preservation of relevant ownership, scheduling, input, configuration and rendering contracts; and (e) an argument that a smaller dependency set cannot satisfy the same obligation. These are proof obligations, not instructions to synthesize executable variants.

Existing evidence also leaves these decisions open:

- Constructor admission and parent selection differ; original Field-child versus R03 raw-parent modeled ownership results do not certify real ARC correctness or original equivalence.
- Layout adds a button installation/layout dependency. Added UI is not an original necessity by default.
- A bounded matching `didMoveToWindow` message contract excludes a modeled observation sink; it does not justify all instrumentation.
- Journal/class-cache separation repairs an added dependency; it does not itself justify the journal.
- Equal initialized bytes from local fills do not establish necessity or prove removed resolver side effects irrelevant.
- Menu configuration methods and the largest processing ranges are not covered completely by initializer/INI tests.
- Security-policy changes remain opaque contract differences, not a bypass implementation or a certified acceptable exception.

## Validation and reproduction

Python 3.13.15, Capstone 5.0.7, Unicorn 2.1.4. Set `AU_ORIGINAL` and `AU_R03` to authorized read-only inputs; set `AU_R03_ARCHIVE` to the retained R03 ZIP. From the curated tree:

```bash
python tools/audit-success-path-delta.py --r03-archive "$AU_R03_ARCHIVE"
python tests/continuation-n/test_original_success_contract.py
python tests/continuation-n/test_original_input_contract.py
python tools/run-native-regression.py
python tools/validate-continuation-results.py
python tools/validate-attachment-intake.py
python tools/validate-original-attachments.py
sha256sum -c SHA256SUMS
```

The full runner actually reran **34 suites / 1,605 labels**, including **1,565 previous retained record values equal** and **40 new labels**. Continuations a–n retain 1,311 labels, plus 294 base labels. [Regression summary](../../results/continuations/continuation-n/regression-summary.json), [provenance](../../results/continuations/continuation-n/provenance.json), [final integrity record](../../results/continuations/continuation-n/validation.json).

Green assertions include reproduction of expected mismatches. They are not 1,605 independently validated success paths, no-breakage certification or a minimality proof. Existing historical tests were rerun unchanged; no new FPS/crash investigation was designed. Older static scheduling/root maps were preserved, not rerun in this pass. Intake/publication checks are offline metadata checks, not live GitHub verification.

## Files, omissions and next concrete work

New: the read-only scanner, two continuation-n tests, all 40 records, graph/delta/necessity ledgers, this report, provenance/integrity summaries. Navigation, worklog, inventory and checksums reflect the new goal. Raw disassembly, private binaries, generated scratch, archive builders and operational patch bytes are omitted from the curated handoff.

Next: close the original Draw-processing contract and legitimate readiness/producer edge before calling the graph complete; classify remaining changed ranges by their original contract and dependencies. Keep the two witnessed UI differences explicitly unresolved unless accepted as intended exceptions. Resolving them does not require a new diagnostic build or permission to alter GitHub. Do not infer that all unexplained changes must be removed.
