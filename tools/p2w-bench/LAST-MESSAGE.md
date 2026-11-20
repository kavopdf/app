# Google verification pass - 20 Nov

Stage is **classify**. Every document now has both numbers: 213 measured through Google, 213 with a LibreOffice partner. Measuring is finished, so this run's deliverable is the capability table - regenerated from the committed JSON and pushed as `benchmarks/GOOGLE-VS-LIBREOFFICE.md`. Next: the classifier cron groups the 185 failing documents into classes; this cron does not classify and does not touch engine code.

| what | count |
|---|---:|
| documents measured through Google | 213 |
| scored against all 42 checks | 192 |
| pass all 42 in Google Docs | 7 |
| fail at least one check | 185 |
| refused (page count) | 21 |

The 21 refusals are not passes. `--collect` recorded them as `page_count_refused` because Google returned a render that was not that document, and they are counted apart from the 192 scored documents.

## Where the two renderers disagree

LibreOffice passes 108 of 192; Google passes 7 of 192. Same source, same .docx, same instrument - only the renderer differs.

| check | Google fails | LibreOffice fails |
|---|---:|---:|
| 32\_stroke\_lines | 145 | 1 |
| 05\_chars\_extra | 141 | 7 |
| 18\_displacement | 125 | 19 |
| 04\_chars\_missing | 67 | 7 |
| 59\_shape\_anchor | 58 | 10 |
| 60\_text\_column\_right\_edge | 57 | 28 |
| 25\_invisible\_text | 49 | 1 |
| 45\_char\_accuracy | 38 | 7 |
| 13\_text\_colours | 32 | 1 |
| 44\_header\_footer | 32 | 4 |
| 17\_matched\_runs | 30 | 9 |
| 47\_margins | 26 | 14 |

Full 42-row table in `benchmarks/GOOGLE-VS-LIBREOFFICE.md`.

Two of these are already explained and must not be re-derived: 32\_stroke\_lines is a rule emitted as a floating `w:drawing` that Google drops while keeping the anchor, and 05\_chars\_extra is that same anchor counted as a character. Everything Google fails and LibreOffice passes is a construct LibreOffice honours and Google does not - the limitation is Google's, and it is a limitation of absolute placement in a flowing-text format.
