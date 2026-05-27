"""
update_readme.py
Scans all .cpp files in the repo root, classifies them by platform,
and rewrites the AUTO-GENERATED sections in README.md.
"""

import os
import re

# ── Difficulty map for known LeetCode problem numbers ──────────────────────────
LEETCODE_DIFFICULTY = {
    1: "🟢 Easy",  2: "🟡 Medium", 3: "🔴 Hard",  4: "🔴 Hard",
    5: "🟡 Medium", 11: "🟡 Medium", 15: "🟡 Medium", 17: "🟡 Medium",
    19: "🟡 Medium", 20: "🟢 Easy", 21: "🟢 Easy", 22: "🟡 Medium",
    23: "🔴 Hard", 26: "🟢 Easy", 33: "🟡 Medium", 46: "🟡 Medium",
    48: "🟡 Medium", 49: "🟡 Medium", 53: "🟡 Medium", 54: "🟡 Medium",
    56: "🟡 Medium", 70: "🟢 Easy", 74: "🟡 Medium", 75: "🟡 Medium",
    78: "🟡 Medium", 84: "🔴 Hard", 88: "🟢 Easy", 94: "🟢 Easy",
    98: "🟡 Medium", 100: "🟢 Easy", 101: "🟢 Easy", 102: "🟡 Medium",
    104: "🟢 Easy", 105: "🟡 Medium", 112: "🟢 Easy", 114: "🟡 Medium",
    118: "🟢 Easy", 119: "🟢 Easy", 121: "🟢 Easy", 125: "🟢 Easy",
    128: "🟡 Medium", 136: "🟢 Easy", 138: "🟡 Medium", 141: "🟢 Easy",
    142: "🟡 Medium", 144: "🟢 Easy", 145: "🟢 Easy", 146: "🟡 Medium",
    152: "🟡 Medium", 153: "🟡 Medium", 160: "🟢 Easy", 169: "🟢 Easy",
    189: "🟡 Medium", 198: "🟡 Medium", 200: "🟡 Medium", 206: "🟢 Easy",
    215: "🟡 Medium", 217: "🟢 Easy", 226: "🟢 Easy", 230: "🟡 Medium",
    234: "🟢 Easy", 235: "🟡 Medium", 236: "🟡 Medium", 237: "🟡 Medium",
    238: "🟡 Medium", 242: "🟢 Easy", 268: "🟢 Easy", 283: "🟢 Easy",
    287: "🟡 Medium", 300: "🟡 Medium", 322: "🟡 Medium", 338: "🟢 Easy",
    344: "🟢 Easy", 347: "🟡 Medium", 394: "🟡 Medium", 416: "🟡 Medium",
    509: "🟢 Easy", 543: "🟢 Easy", 560: "🟡 Medium", 567: "🟡 Medium",
    572: "🟢 Easy", 617: "🟢 Easy", 647: "🟡 Medium", 704: "🟢 Easy",
    746: "🟢 Easy", 876: "🟢 Easy", 977: "🟢 Easy", 1143: "🟡 Medium",
    1448: "🟡 Medium", 1480: "🟢 Easy", 1544: "🟢 Easy", 1768: "🟢 Easy",
}

# ── Platform detection from filename ───────────────────────────────────────────
def classify(filename: str) -> str:
    name = filename.replace(".cpp", "")

    # LeetCode: starts with digit(s) ONLY before hyphen (e.g. 1-, 876-)
    if re.match(r"^\d+-", name):
        return "leetcode"

    # Codeforces numbered: digit(s) + uppercase letter + separator (e.g. 4A-, 158A-)
    if re.match(r"^\d+[A-Z][-_]", name):
        return "codeforces"

    # Codeforces letter-prefix: A-, B-, C-, A_, B_, C_ (e.g. A-Vanya, B_Skibidus, C1-)
    if re.match(r"^[A-D]\d?[-_]", name):
        return "codeforces"

    # CodeChef: all-uppercase slug, no lowercase (e.g. AMMEAT, MAXCOUNT, TWOSTR)
    if re.match(r"^[A-Z][A-Z0-9_]+$", name) and name == name.upper():
        return "codechef"

    return "other"


# ── Helpers ────────────────────────────────────────────────────────────────────
def friendly_name(filename: str) -> str:
    """Turn a filename into a readable problem name."""
    name = filename.replace(".cpp", "")
    # Strip leading number/letter prefix (e.g. "1-", "158A-", "A-", "B_")
    name = re.sub(r"^[\dA-Za-z]+[-_]", "", name)
    return name.replace("_", " ").strip()


def leetcode_number(filename: str) -> int:
    m = re.match(r"^(\d+)-", filename)
    return int(m.group(1)) if m else 0


def cf_prefix(filename: str) -> str:
    """Extract Codeforces problem ID prefix (e.g. '4A', '158A', 'A', 'B')."""
    name = filename.replace(".cpp", "")
    m = re.match(r"^(\d+[A-Z]|[A-D]\d?)[-_]", name)
    return m.group(1) if m else name


# ── Scan repo root for .cpp files ──────────────────────────────────────────────
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

leetcode   = []
codeforces = []
codechef   = []

for f in sorted(os.listdir(repo_root)):
    if not f.endswith(".cpp"):
        continue
    plat = classify(f)
    if plat == "leetcode":
        leetcode.append(f)
    elif plat == "codeforces":
        codeforces.append(f)
    elif plat == "codechef":
        codechef.append(f)

# Sort LeetCode by problem number
leetcode.sort(key=leetcode_number)


# ── Table generators ───────────────────────────────────────────────────────────
def gen_stats_block():
    total = len(leetcode) + len(codeforces) + len(codechef)
    return f"""\
<div align="center">

| Platform | Solved |
|:---:|:---:|
| 🟡 LeetCode | **{len(leetcode)}** |
| 🔵 Codeforces | **{len(codeforces)}** |
| 🟤 CodeChef | **{len(codechef)}** |
| **Total** | **{total}** |

</div>"""


def gen_leetcode_table():
    rows = ["| # | Problem | Difficulty | Solution |",
            "|:---:|:---|:---:|:---:|"]
    for f in leetcode:
        num   = leetcode_number(f)
        pname = friendly_name(f)
        diff  = LEETCODE_DIFFICULTY.get(num, "—")
        link  = f"https://leetcode.com/problems/{pname.lower().replace(' ', '-')}/"
        rows.append(f"| {num} | [{pname}]({link}) | {diff} | [Code]({f}) |")
    return "\n".join(rows)


def gen_codeforces_table():
    rows = ["| Problem ID | Problem Name | Solution |",
            "|:---:|:---|:---:|"]
    for f in codeforces:
        prefix = cf_prefix(f)
        pname  = friendly_name(f)
        rows.append(f"| `{prefix}` | {pname} | [Code]({f}) |")
    return "\n".join(rows)


def gen_codechef_table():
    rows = ["| Problem | Solution |",
            "|:---|:---:|"]
    for f in codechef:
        slug = f.replace(".cpp", "")
        rows.append(f"| {slug} | [Code]({f}) |")
    return "\n".join(rows)


# ── Patch README.md ────────────────────────────────────────────────────────────
readme_path = os.path.join(repo_root, "README.md")

with open(readme_path, "r", encoding="utf-8") as fh:
    content = fh.read()


def replace_section(text: str, tag: str, new_body: str) -> str:
    pattern = rf"(<!-- {tag}_START -->).*?(<!-- {tag}_END -->)"
    replacement = rf"\1\n{new_body}\n\2"
    return re.sub(pattern, replacement, text, flags=re.DOTALL)


content = replace_section(content, "AUTO_STATS",      gen_stats_block())
content = replace_section(content, "LEETCODE_TABLE",  gen_leetcode_table())
content = replace_section(content, "CODEFORCES_TABLE",gen_codeforces_table())
content = replace_section(content, "CODECHEF_TABLE",  gen_codechef_table())

with open(readme_path, "w", encoding="utf-8") as fh:
    fh.write(content)

lc = len(leetcode)
cf = len(codeforces)
cc = len(codechef)
print(f"✅ README updated — LeetCode: {lc} | Codeforces: {cf} | CodeChef: {cc} | Total: {lc+cf+cc}")
