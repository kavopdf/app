# The scipy guard installs correctly and then reports that it failed

The 12:13 run found the real cause of the screen.py stall and moved the guard to where it belongs:
_ensure_scipy() now sits at the top of edt() instead of only at the top of main(), because screen.py
imports p2w as a module and never runs main(). That fix is right and it is in HEAD.

What it does after installing is not.

## Measured on a pod with no scipy

    before:  scipy importable? no
    _ensure_scipy() -> WARNING: pip exit 0
                    -> WARNING: ~48x slower per page; a 23-document class will not finish in one call
    after:   import scipy -> ModuleNotFoundError

    pip show scipy -> Name: scipy  Version: 1.18.1
    fresh process  -> scipy 1.18.1

So the package was installed. The same-process import cannot see it because sys.path was fixed when the
interpreter started, and a user-site directory created afterwards is not on it. The guard then treats its
own blind spot as a failed install and prints the 48x warning.

## Why that matters

The warning is the one a run reads to decide the class cannot finish in a call. Two runs already blamed
soffice for this stall and lost three 280 s calls each. A guard that installs the fix and then says the
fix is not there reproduces exactly that: the run stops, blames the renderer, and the next run starts from
the same wrong diagnosis.

## The fix

Verify out of process. The guard already knows how to run pip; it should confirm the way a fresh run
will see it:

    python3 -c "import scipy"   # subprocess, not import

If that fails, warn. If it passes, say nothing - the install worked.

## Verified, not changed

The install path is correct and scipy 1.18.1 is on this pod now, so the next run is fast whether or not
this is fixed. Recorded because the warning, not the install, is what a run acts on.
