# Causes, not symptoms

**Coverage: 2 of 72 open documents classified.** The rest are unclassified, and a cause
table built from a sample is not a census - re-run `cause.py --open --limit N` against docx
built by the CURRENT engine before sizing any work from this file.

Grouped from `CAUSES.json`, which `cause.py` writes by matching every line of our render
against the line the PDF drew and classifying the SHAPE of the displacement.

| cause | documents | what one fix would serve |
|---|---:|---|
| `clean` | **4** |  |
| `scattered` | **1** | needs a human to look at one |
| `page-shift` | **1** | margins, page size or an offset applied to the whole sheet |

## Documents

### `clean` — 4

- `electricity-bill` — 0.0 pt
- `mobile-bill` — 0.0 pt
- `salary-slip-factory-wages` — 0.0 pt
- `two-tables-stacked-with-no-gap` — 0.0 pt

### `scattered` — 1

- `form16-part-b` — 8.61 pt

### `page-shift` — 1

- `marksheet-university-consolidated` — 0.53 pt
