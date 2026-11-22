# P2W Baseline - Run Report

**22 Nov 2026 · 21:55 IST**

> 153 of 212 documents are fixed to 99%. The corpus is 39.7% closer to the 15 Nov baseline than it started.

This run began on an empty pod: it fetched the corpus, built the engine, converted every PDF and then measured in successive sandbox passes until nothing was left unmeasured. The ranking, the state and the census are all published from that one run, the ratchet is clean, and the phase has moved on to classify. The document exempt by size keeps its row in the table with no score, labelled exempt, because dropping the row makes the measurement gate read the corpus as short and blanking it used to make the regression gate read an exemption as a deletion.

## Corpus

| | |
|:--|--:|
| Documents | **212** |
| .docx fixed to 99% | **153** |
| .docx still open | **59** |
| .txt clean | **197** |
| .txt failing | **16** |
| Google measured | **192** of 212 |
| Google clean | **23** |

## Against the 15 Nov baseline

| | baseline | now | |
|:--|--:|--:|:--|
| mean share@5 | 6.15 | **3.71** | -39.70% |
| documents improved | | **65** | |
| regressions | | **0** | none |

