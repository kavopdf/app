# P2W Google Verify - Run Report

**23 Nov 2026 · stage classify (from stage.py)**

> 86 of 213 documents have a Google result on the current engine, and the rest still carry results from older engines. Of those 86, 13 pass all 42 and 50 fail at least one; 23 are refused on page count.

This run re-measured a fresh batch through Google and re-rendered the LibreOffice half of the same documents, so the pair for each one now comes from the current engine rather than from an older build. Both result sets are committed. The stage label above is what stage.py prints; its measured count reads every result file without asking which engine wrote it, so the measurement itself is tracked by the plan line, which still lists documents to go.

## Checks the current-engine set fails in Google

| check | documents |
|:--|--:|
| `18\_displacement` | 28 |
| `04\_chars\_missing` | 24 |
| `60\_text\_column\_right\_edge` | 21 |
| `25\_invisible\_text` | 19 |
| `59\_shape\_anchor` | 19 |
| `13\_text\_colours` | 18 |
| `45\_char\_accuracy` | 14 |
| `35\_rotation` | 10 |

## Both renderers, all committed results

Across every committed result, mixed engines included: LibreOffice passes all 42 on 122 of 190, Google on 30 of 190. The disagreement is unchanged in shape - `18\_displacement` 20 against 101, `04\_chars\_missing` 2 against 65, `25\_invisible\_text` 0 against 48, `32\_stroke\_lines` 1 against 47.

## Next

Continue the Google measurement: most of the corpus still carries no result from the current engine. One document scored worse than its committed result (`08\_two\_overlapping\_stamps`, recorded in BLOCKERS.md with the gate refusal), and nothing else in the re-measured set moved.
