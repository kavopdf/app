# P2W Google Verify - Run Report

**23 Nov 2026 · 17:13 IST · stage classify**

> 190 of 213 measured in Google, 23 refused on page count. Google passes all 42 on 30; LibreOffice on 122.

This run staged the next batch of documents, converted each through Google Docs, exported the result as a PDF and scored it, then rendered the same .docx with soffice and scored that too, so both halves of every document in the batch carry the current engine stamp. None of them was refused on page count. The Google results and the LibreOffice results went in together, and the capability table was regenerated from them. Documents whose older results predate the current engine still have to be re-measured before the pair is fully consistent.

## Measured

| | |
|:--|--:|
| scored | **190** |
| refused on page count | **23** |
| clean in Google | **30** |
| clean in LibreOffice | **122** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `18\_displacement` | **100** | 20 |
| `04\_chars\_missing` | **65** | 2 |
| `25\_invisible\_text` | **48** | 0 |
| `32\_stroke\_lines` | **48** | 1 |
| `05\_chars\_extra` | **44** | 3 |
| `60\_text\_column\_right\_edge` | **56** | 18 |
| `59\_shape\_anchor` | **45** | 9 |
| `45\_char\_accuracy` | **37** | 2 |

The first row is the class to take: `18\_displacement`, 100 documents in Google against 20 in LibreOffice.

