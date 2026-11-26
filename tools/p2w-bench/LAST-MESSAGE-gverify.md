**Google verify - run report**

**Stage: classify.** The Google half is complete and the capability table already matches it, so this cron had nothing to measure and nothing to rewrite. It changed no engine code.

`gverify.py --report` reads 213 verified, 42 pass every check offered, 166 fail at least one, 5 refused on page count. Both halves sit on the engine in the tree - 208 of 208 pairs through Google and 208 of 208 through LibreOffice - and `gverify.py --matrix` now regenerates `benchmarks/GOOGLE-VS-LIBREOFFICE.md` byte for byte, so the table written by the last LibreOffice pass is still the table the results support. Nothing to commit.

Where the two renderers disagree - the pair that names a construct:

| check | LibreOffice fails | Google fails | who is stricter |
|---|---:|---:|---|
| `18\_displacement` | 21 | 119 | **Google** |
| `60\_text\_column\_right\_edge` | 19 | 62 | **Google** |
| `04\_chars\_missing` | 3 | 55 | **Google** |
| `59\_shape\_anchor` | 12 | 49 | **Google** |
| `45\_char\_accuracy` | 3 | 34 | **Google** |
| `13\_text\_colours` | 1 | 32 | **Google** |
| `17\_matched\_runs` | 6 | 32 | **Google** |
| `47\_margins` | 16 | 28 | **Google** |

Every check offered: LibreOffice 135 of 208 documents pass, Google 42 of 208.

**Next:** stage.py reads classify because the class table is older than the results - 166 failing documents to group. That is the classifier's step, not this cron's stage, so I stopped here.
