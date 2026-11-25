# A .docx can never be byte-identical to itself; unzip before comparing

Found independently twice on 25 Nov, by the 07:02 run and by corpus-changed.py.

## The measurement

Two runs of one engine, twelve documents:

    file bytes differ      12 of 12
    word/document.xml      12 of 12 identical

The engine is deterministic at word/document.xml and not at the .docx byte. A .docx is a zip, and a zip
carries a local-header timestamp per member, so two archives written a second apart differ in bytes while
holding identical parts. The 07:02 report puts it plainly: "The patch's own reviewer checklist asks for
byte identity; that check can only ever fail. Unzip before comparing."

## Where this is already right

corpus-changed.py hashes word/document.xml and says so in its docstring. That fix landed today after the
same defect made a record-to-record comparison report 213 changed documents out of 213 - every document
"changed" because every zip timestamp had moved.

No other tool compares .docx bytes for identity. The remaining getsize() calls in code_test.py and
reduce-repro.py report a size, which is a different question and is fine.

## What still asks for it

The requirement survives in prose - in patch reviewer checklists and in handoffs that say "identical at
the byte" when they mean "identical at word/document.xml". A future run reading one of those will measure
a difference that is not there and conclude its patch changed something it did not.

The rule, for anything that writes it down: compare word/document.xml, or unzip both and compare parts.
Never compare the archive.

## Not changed

No tool edited. The one that needed it was fixed today for its own reason. This records the rule so the
next checklist does not re-introduce the impossible check.
