# P2W Google Verify - Run Report

**21 Nov 2026 · 13:24 IST · stage classify**

> 192 of 213 measured in Google, 21 refused on page count. Google passes all 42 on 6; LibreOffice on 122.

This run measured nothing new and touched no engine code. It regenerated the capability table from the committed results in both renderer directories, committed it, and pushed; that table is this stage's last deliverable.

## Measured

| | |
|:--|--:|
| scored | **192** |
| refused on page count | **21** |
| clean in Google | **6** |
| clean in LibreOffice | **122** |

## Checks Google fails and LibreOffice does not

| check | Google | LibreOffice |
|:--|--:|--:|
| `32\_stroke\_lines` | **145** | 1 |
| `05\_chars\_extra` | **141** | 3 |
| `18\_displacement` | **124** | 20 |
| `04\_chars\_missing` | **66** | 2 |
| `25\_invisible\_text` | **49** | 0 |
| `59\_shape\_anchor` | **58** | 11 |
| `60\_text\_column\_right\_edge` | **58** | 18 |
| `45\_char\_accuracy` | **37** | 2 |

The first row is the class to take: `32\_stroke\_lines`, 145 documents in Google against 1 in LibreOffice.

