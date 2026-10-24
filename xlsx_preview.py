"""Read-only preview of the consolidation template for /free/consolidation-excel-template/.
openpyxl does not calculate formulas, so this evaluates the handful of functions the template
uses (IF, AND, N, SUM, SUMIF, ROUND, SUMPRODUCT) to show the same values Excel would.
Used by generate_joiin_leadmagnet.py; run that with the base Python (it has openpyxl)."""
import html
import re

import openpyxl
from openpyxl.utils import get_column_letter, range_boundaries


class _Arr(list):
    def _op(self, o, f):
        o = o if isinstance(o, list) else [o] * len(self)
        return _Arr(f(a, b) for a, b in zip(self, o))

    def __eq__(self, o): return self._op(o, lambda a, b: a == b)
    def __ne__(self, o): return self._op(o, lambda a, b: a != b)
    def __mul__(self, o): return self._op(o, lambda a, b: _num(a) * _num(b))


def _num(v):
    if isinstance(v, bool):
        return int(v)
    return v if isinstance(v, (int, float)) else 0


def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


FUNCS = {
    "IF": lambda c, a, b=False: a if c else b,
    "AND": lambda *a: all(a),
    "N": lambda v: v if _is_num(v) else 0,
    "SUM": lambda *a: sum(y for x in a for y in (x if isinstance(x, list) else [x]) if _is_num(y)),
    "SUMIF": lambda r, crit, s: sum(_num(b) for a, b in zip(r, s) if a == crit and a != ""),
    "ROUND": lambda v, d: round(_num(v), d),
    "SUMPRODUCT": lambda a: sum(_num(x) for x in a),
}
REF = re.compile(r"(?:'([^']+)'|([A-Za-z][A-Za-z ]*?))!(\$?[A-Z]+\$?\d+(?::\$?[A-Z]+\$?\d+)?)"
                 r"|(\$?[A-Z]+\$?\d+(?::\$?[A-Z]+\$?\d+)?)(?![A-Za-z(])")


class Book:
    def __init__(self, path):
        self.wb = openpyxl.load_workbook(path)
        self.cache = {}

    def val(self, sh, ref):
        key = (sh, ref.replace("$", ""))
        if key not in self.cache:
            v = self.wb[sh][key[1]].value
            if v is None:
                v = ""
            elif isinstance(v, str) and v.startswith("="):
                v = self._eval(sh, v[1:])
            self.cache[key] = v
        return self.cache[key]

    def rng(self, sh, r):
        c1, r1, c2, r2 = range_boundaries(r.replace("$", ""))
        return _Arr(self.val(sh, f"{get_column_letter(c)}{rr}") for rr in range(r1, r2 + 1) for c in range(c1, c2 + 1))

    def _eval(self, sh, f):
        out = []
        for part in re.split(r'("[^"]*")', f):
            if not part.startswith('"'):
                def sub(m):
                    s, r = m.group(1) or m.group(2) or sh, m.group(3) or m.group(4)
                    return f"_b.rng({s!r},{r!r})" if ":" in r else f"_b.val({s!r},{r!r})"
                part = REF.sub(sub, part).replace("<>", "!=")
                part = re.sub(r"(?<![<>!=])=(?!=)", "==", part)
            out.append(part)
        return eval("".join(out), {"_b": self, **FUNCS})

    def table(self, sh, header_row, cols, first, last):
        """Header + non-empty rows of a sheet as lists of display values."""
        head = [self.val(sh, f"{c}{header_row}") for c in cols]
        rows = []
        for r in range(first, last + 1):
            row = [self.val(sh, f"{c}{r}") for c in cols]
            if row[0] != "":
                rows.append(row)
        return head, rows


def fmt(v):
    if _is_num(v):
        return f"({abs(v):,.0f})" if v < 0 else f"{v:,.0f}"
    return html.escape(str(v))


def render(head, rows, check_rows=()):
    """HTML table; check_rows = labels whose OK cells get the green style."""
    th = "".join(f"<th>{html.escape(str(h))}</th>" for h in head)
    body = []
    for row in rows:
        cells = []
        for i, v in enumerate(row):
            cls = ' class="ok"' if v == "OK" else (' class="num"' if _is_num(v) else "")
            cells.append(f"<td{cls}>{fmt(v)}</td>")
        strong = ' class="total"' if row[0] in check_rows else ""
        body.append(f"<tr{strong}>{''.join(cells)}</tr>")
    return f'<div class="xp-scroll"><table class="xp-table"><thead><tr>{th}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'
