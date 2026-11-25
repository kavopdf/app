# t09 fails the two Account Forms because repeated form values are counted as page furniture

## The measurement

    041122-Account_Opening_Form
      t09_page_furniture   owed=29 drawn   present=125 in the .txt   FAIL

t09 builds `elements` from text that appears on at least FURNITURE_MIN_PAGES pages and contains a letter, then
requires present == owed.

## What the repeated text actually is

Counting the .txt lines by the same key the check uses:

    72 x |#     53 x |Yes     45 x |M     41 x |Y     33 x |D

These are form field values - a checkbox tick, a gender letter, a yes/no letter, a placeholder. They are not
running heads. They repeat because a nine-page admission form asks the same question on every page.

## And the PDF really does draw them that often

    PDF draws:   Yes 53   M 52   Y 48   D 40      on 9 pages
    .txt has:    Yes 53   M 45   Y 41   D 33

So `Yes` is complete - 53 drawn, 53 present. `M`, `Y` and `D` are each seven short.

## Two faults, not one

1. THE CHECK MISCLASSIFIES. A value that legitimately repeats on every page of a form satisfies t09's test for
   furniture, so the check charges the document for a surplus it is supposed to have. This is the same shape
   as the duplicate-head case the code already documents: the check cannot tell a running head from a form
   value that happens to appear everywhere.

2. THE .txt LOSES 21 VALUES. Seven copies each of M, Y and D are drawn by the PDF and are not in the .txt.
   That is a real loss and the check is right to notice something - just not the thing it reports.

## Why it was not changed here

Weakening t09 to ignore short repeated strings would hide fault 2 as well as fault 1, and fault 2 is real text
loss. The two need separating: a form value should not enter the furniture population at all, and the 21
missing values should be measured against the PDF's own field positions before anything is edited.

## Blast radius

Two documents. They are the same pair as the ligature fault, and both carry U+FFFD as well, so all three of
their failing checks sit on one population of two sibling forms.

t06's cause is established (ligatures written as U+FFFD, 127 per form). t09's is stated here and is a
different fault: 21 dropped values, plus a check that cannot distinguish them from furniture.
