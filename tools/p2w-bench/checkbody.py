#!/usr/bin/env python3
"""
checkbody.py - what a check ASKS, as a digest. Not what it is called.

THE BLIND SPOT THIS CLOSES
  instrument.py names the universe by the list of check ids, and record.py stamps
  that name on every row and mark. Five checks on 13 Nov changed their PREDICATE
  while keeping their id:

    7b6ed92  32_stroke_lines   counted drawing objects -> counts segments
    cc8644e  22_reading_order  LCS over two extractors' sequences -> torn lines
    6692271  08_image_count    get_images() (the /Resources dictionary) -> get_image_info() (drawn)
    11517dc  18_displacement   absorbed 19_worst_dy's tail clause (TAIL_FACTOR)
    57f521d  08_image_count    (the half of it that was never written)

  The id list is identical before and after each of those. So `universe_sha`, which
  is a digest of the ID LIST, is identical too - and a mark taken under the old
  `22_reading_order` (agreement between two extractors, 88 documents failing) is
  silently compared against the new one (torn lines, 4 failing). The ratchet reads
  that as 84 documents getting better, or worse, depending on which direction the
  redefinition went. It is neither: it is two different questions scored as one.

  This is the denominator guard's own failure one level deeper. That guard said
  "a count means nothing without the set it was counted out of". This says the set
  is not the whole story: the set of QUESTIONS is the ids PLUS what each id asks.

WHAT A BODY IS
  Not the assignment line. `checks["22_reading_order"] = (0, len(torn), not torn)`
  is one line and it is the same line before and after the redefinition - `torn`
  is what changed. So a body is the transitive closure, inside the verifier's own
  AST, of:

    * the statement that assigns the id,
    * every statement in the same scope that defines a name the body reads, and
      every statement that MUTATES one (`bad_pages.append(pg)`, `flat.add(...)`,
      `x[k] = v`, `del x`) - a value built by mutation has no defining statement
      to find, and missing those was how 18_displacement's whole page loop, the
      loop TAIL_FACTOR lives in, first read as unchanged,
    * every module-level function or constant the body names, and what THOSE name,
      to the same rule.

  A function's docstring is dropped and comments never reach the AST, so prose is
  not part of the question. Re-indenting or re-wrapping is not either: bodies are
  hashed as `ast.unparse` output, not as bytes. Editing the sentence that explains
  a check does not invalidate a mark; editing the arithmetic that decides it does.

WHAT IT DELIBERATELY DOES NOT COVER
  * Parameters. `extra_checks(src, gd, s_runs, g_runs, pairs)` receives its inputs;
    the code that BUILT `s_runs` is the run matcher, not this check. A change to
    the matcher changes every check's number without changing any check's
    question, and a mark that must be re-taken because the matcher moved is a cost
    the id-set guard already pays.
  * Imports. `import collections` cannot change what a check asks.
  * Output sinks. `checks = {}` and `c = {}` are the dicts the answers are written
    INTO; treating a write to them as a mutation would make every check's body the
    whole file. A name initialised from an empty dict literal is a sink.

USAGE
  python3 tools/p2w-bench/checkbody.py verify_google.py          # id -> body sha
  python3 tools/p2w-bench/checkbody.py verify_google.py --diff OLD.py
                                                                 # which ids moved
"""
import ast
import copy
import hashlib
import re
import sys

CHECK_RE = re.compile(r"^(?:\d{2}[a-c]?|t\d{2})_[a-z0-9_]+$")

# Methods that change their receiver. A statement that calls one of these on a name
# is part of that name's value, so it belongs in the closure of anything that reads it.
MUTATORS = frozenset("""
append extend insert add update setdefault pop popitem remove discard clear sort
reverse __setitem__ __delitem__ __iadd__ write writelines
""".split())


class Scope:
    """One lexical scope: a module, a function body, a class body."""

    __slots__ = ("parent", "defs", "muts", "binds", "owner")

    def __init__(self, parent, owner=None):
        self.parent = parent
        self.defs = {}           # name -> [statement that assigns it, ...]
        self.muts = {}           # name -> [statement that mutates it in place, ...]
        self.binds = {}          # the two merged, sinks excluded - what closure reads
        self.owner = owner


def _target_names(target):
    """Names a target binds. A Subscript or Attribute target binds NO new name:
    `checks["x"] = y` writes into a dict that already exists, and counting it as a
    binding of `checks` made every check's body the entire file (measured: 54 checks,
    3 distinct bodies)."""
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        out = []
        for e in target.elts:
            out.extend(_target_names(e))
        return out
    if isinstance(target, ast.Starred):
        return _target_names(target.value)
    return []


def _base_name(node):
    """`bad_pages` for `bad_pages.append`, `flat` for `flat[x]`, else None."""
    while isinstance(node, (ast.Subscript, ast.Attribute)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def _cached(node, key, fn):
    """Memoise a pure function of an AST node ON the node (see canon())."""
    hit = getattr(node, key, None)
    if hit is None:
        hit = fn(node)
        try:
            setattr(node, key, hit)
        except Exception:                   # pragma: no cover
            pass
    return hit


def local_binders(node):
    """Names a comprehension or a lambda binds INSIDE the expression.

    `s_imgs = sum(len(p.get_image_info()) for p in src)` binds `p` - but only within
    that sum. Treated as a scope binding it collided with `for i, p in enumerate(src)`
    above it, and every check whose body held a comprehension over `p` pulled the whole
    run-matching loop in with it (measured: 08_image_count, 3 statements of its own,
    read as 142)."""
    return _cached(node, "_binders", _local_binders)


def _local_binders(node):
    out = set()
    for n in ast.walk(node):
        if isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            for g in n.generators:
                out.update(_target_names(g.target))
        elif isinstance(n, ast.Lambda):
            a = n.args
            for arg in list(a.args) + list(a.posonlyargs) + list(a.kwonlyargs):
                out.add(arg.arg)
            if a.vararg:
                out.add(a.vararg.arg)
            if a.kwarg:
                out.add(a.kwarg.arg)
    return out


def writes(stmt):
    """(names this statement defines, names it mutates in place)."""
    defined, mutated = [], []
    inner = local_binders(stmt)

    def scan(n, top=False):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not top:
            return                       # a nested def's internals belong to the def
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            if n.id not in inner:
                defined.append(n.id)
        elif isinstance(n, ast.Subscript) and isinstance(n.ctx, (ast.Store, ast.Del)):
            b = _base_name(n)
            if b:
                mutated.append(b)
        elif isinstance(n, ast.Attribute) and isinstance(n.ctx, (ast.Store, ast.Del)):
            b = _base_name(n)
            if b:
                mutated.append(b)
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            b = _base_name(n.func.value)
            if b and n.func.attr in MUTATORS:
                mutated.append(b)
        for ch in ast.iter_child_nodes(n):
            scan(ch)
    scan(stmt, top=True)
    return defined, mutated


def reads(stmt):
    return _cached(stmt, "_reads", _reads)


def _reads(stmt):
    inner = local_binders(stmt)
    return frozenset(n.id for n in ast.walk(stmt)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
            and n.id not in inner)


def _is_sink(stmt, name):
    """`x = {}` / `x = dict()` is an output dict, not a value the check computes."""
    if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
        return False
    if _target_names(stmt.targets[0]) != [name]:
        return False
    v = stmt.value
    return (isinstance(v, ast.Dict) and not v.keys) or \
           (isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == "dict")


def build(stmts, parent, fn_scopes):
    sc = Scope(parent)

    def visit(ss):
        for s in ss:
            if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                fn_scopes[s] = build(s.body, sc, fn_scopes)
                sc.binds.setdefault(s.name, []).append(s)
                continue
            if isinstance(s, (ast.Import, ast.ImportFrom)):
                continue                  # an import is not a predicate
            defined, mutated = writes(s)
            for nm in defined:
                sc.defs.setdefault(nm, []).append(s)
            for nm in mutated:
                sc.muts.setdefault(nm, []).append(s)
            for f in ("body", "orelse", "finalbody"):
                sub = getattr(s, f, None)
                if isinstance(sub, list) and sub and isinstance(sub[0], ast.stmt):
                    visit(sub)
            if isinstance(s, ast.Try):
                for h in s.handlers:
                    visit(h.body)
            if hasattr(ast, "Match") and isinstance(s, ast.Match):
                for case in s.cases:
                    visit(case.body)
    visit(stmts)
    # A name whose only definition is an empty dict literal is where answers are WRITTEN,
    # not a value a check computes. `checks["01_page_count"] = ...` is a write to `checks`,
    # and counting writes to a sink as part of a body made every one of the 54 checks
    # include every other one (measured: 5 distinct bodies of 54, 980 statements each).
    for nm, muts in sc.muts.items():
        if any(_is_sink(d, nm) for d in sc.defs.get(nm, [])):
            continue
        sc.binds.setdefault(nm, []).extend(muts)
    for nm, ds in sc.defs.items():
        sc.binds.setdefault(nm, []).extend(ds)
    return sc


def canon(node):
    """Normalised source of one statement: comments gone, whitespace normalised,
    a def's docstring gone. Two edits that mean the same thing hash the same.

    Memoised per parse by node identity: the 54 closures overlap heavily (they all
    contain the run loop), so the same big `for` is unparsed fifty times without
    this, and checkbody took 1.4 s on the 150 kB verifier. The guard calls it twice
    per commit and cannot afford that."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        body = node.body
        if body and isinstance(body[0], ast.Expr) \
                and isinstance(body[0].value, ast.Constant) \
                and isinstance(body[0].value.value, str):
            node = copy.copy(node)
            node.body = body[1:] or [ast.Pass()]
    # Stored ON the node, not in a dict keyed by id(node): the docstring-stripped
    # shallow copies canon() makes are freed immediately, so their ids are handed
    # out again to later nodes and an id-keyed cache returns another statement's
    # text. That corruption is silent - it only makes the digest wrong.
    hit = getattr(node, "_canon", None)
    if hit is not None:
        return hit
    try:
        out = ast.unparse(node)
    except Exception:                       # pragma: no cover - unparse is total on 3.9+
        out = ast.dump(node)
    try:
        node._canon = out
    except Exception:                       # pragma: no cover - ast nodes accept it
        pass
    return out


def _eligible(binding, node):
    """Is this binding one the reading statement can actually see?

    Python executes a block top to bottom, so a value read at line N was built by a
    statement at line < N - or by a loop/if that CONTAINS line N, whose header is
    also at a smaller line number. Without this, `i` - a loop counter reused by a
    dozen unrelated loops - welds them together: 04_chars_missing read
    `for i in range(gd.page_count)`, which is 31_pages_lost_their_text's loop 400
    lines below it, and moved whenever 31 moved (measured on 6692271).

    A def is exempt from the ordering, because a function is bound before any call
    to it can run, and because a body's reads happen at call time, not at its def
    line - a module constant defined below the def that uses it is still that
    function's body."""
    if isinstance(binding, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return True
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return True
    return getattr(binding, "lineno", 0) <= getattr(node, "lineno", 0)


def body_of(target, scope, fn_scopes, cap=2000):
    """(canonical text, statements) of the closure rooted at `target`."""
    items, seen, stack = [], set(), [(target, scope)]
    while stack:
        node, sc = stack.pop()
        if id(node) in seen:
            continue
        seen.add(id(node))
        items.append(node)
        inner = fn_scopes.get(node, sc)
        for name in sorted(reads(node)):
            s = inner
            while s is not None:
                cand = [bn for bn in s.binds.get(name, []) if _eligible(bn, node)]
                if cand:
                    for bn in cand:
                        stack.append((bn, s))
                    break
                s = s.parent
        if len(items) > cap:                # a hard stop, so a pathological file cannot
            break                           # make this quadratic
    items.sort(key=lambda n: (getattr(n, "lineno", 0), getattr(n, "col_offset", 0)))
    return "\x1e".join(canon(n) for n in items), items


def _assignments(stmts, sc, fn_scopes, out):
    """Every `X["<check id>"] = ...` in the tree, with the scope it lives in."""
    for s in stmts:
        if isinstance(s, ast.Assign):
            for t in s.targets:
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) \
                        and isinstance(t.slice, ast.Constant) \
                        and isinstance(t.slice.value, str) \
                        and CHECK_RE.match(t.slice.value):
                    out.append((t.slice.value, s, sc))
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            _assignments(s.body, fn_scopes[s], fn_scopes, out)
            continue
        for f in ("body", "orelse", "finalbody"):
            sub = getattr(s, f, None)
            if isinstance(sub, list) and sub and isinstance(sub[0], ast.stmt):
                _assignments(sub, sc, fn_scopes, out)
        if isinstance(s, ast.Try):
            for h in s.handlers:
                _assignments(h.body, sc, fn_scopes, out)
        if hasattr(ast, "Match") and isinstance(s, ast.Match):
            for case in s.cases:
                _assignments(case.body, sc, fn_scopes, out)


def bodies(text):
    """{check id: (body sha12, statement count, chars)} for one verifier source.

    Two assignment sites for the same id (the txt half keeps a couple) are hashed
    together in source order, so an id is never silently narrowed to one of them.
    """
    tree = ast.parse(text)
    fn_scopes = {}
    mod = build(tree.body, None, fn_scopes)
    found = []
    _assignments(tree.body, mod, fn_scopes, found)
    out = {}
    for cid, stmt, sc in found:
        txt, items = body_of(stmt, sc, fn_scopes)
        h = hashlib.sha1(txt.encode()).hexdigest()[:12]
        prev = out.get(cid)
        if prev is None:
            out[cid] = (h, len(items), len(txt))
        else:
            both = "\x1f".join(sorted([prev[0], h]))
            out[cid] = (hashlib.sha1(both.encode()).hexdigest()[:12],
                        prev[1] + len(items), prev[2] + len(txt))
    return out


def bodies_of_file(path):
    return bodies(open(path, encoding="utf-8").read())


def universe_sha(body_map):
    """One name for a whole instrument: every id AND the digest of what it asks."""
    return hashlib.sha1(
        "\n".join("%s:%s" % (k, body_map[k][0] if isinstance(body_map[k], tuple)
                             else body_map[k]) for k in sorted(body_map))
        .encode()).hexdigest()[:12] if body_map else ""


def id_sha(ids):
    """The OLD name: the id list only. Kept for comparison and for the audit trail -
    it is what the marks of 13 Nov were stamped with, and saying so is the point."""
    ids = sorted(ids)
    return hashlib.sha1("\n".join(ids).encode()).hexdigest()[:12] if ids else ""


def moved(old_text, new_text):
    """(redefined, added, dropped) between two verifier sources.

    `redefined` is the case the id-list digest cannot see: same id, different question.
    """
    a, b = bodies(old_text), bodies(new_text)
    redefined = sorted(k for k in a if k in b and a[k][0] != b[k][0])
    return redefined, sorted(set(b) - set(a)), sorted(set(a) - set(b))


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    path = argv[0]
    m = bodies_of_file(path)
    if "--diff" in argv:
        old = bodies_of_file(argv[argv.index("--diff") + 1])
        redefined, added, dropped = moved(open(argv[argv.index("--diff") + 1]).read(),
                                         open(path).read())
        print("redefined (same id, different question): %d" % len(redefined))
        for k in redefined:
            print("  %-30s %s -> %s" % (k, old[k][0], m[k][0]))
        if added:
            print("added:   %s" % ", ".join(added))
        if dropped:
            print("dropped: %s" % ", ".join(dropped))
        print("id-sha  %s -> %s  %s"
              % (id_sha(old), id_sha(m),
                 "SAME - the old guard sees nothing" if id_sha(old) == id_sha(m)
                 else "changed - the old guard sees this one"))
        print("body-sha %s -> %s" % (universe_sha(old), universe_sha(m)))
        return 0
    for k in sorted(m):
        print("%-32s %s  stmts=%-4d chars=%d" % (k, m[k][0], m[k][1], m[k][2]))
    print("")
    print("%d checks; id-sha %s; body-sha %s" % (len(m), id_sha(m), universe_sha(m)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
