"""Render terminal-style screenshot captures for the assignment docs.

Produces dark-theme terminal window PNGs showing the real prompt/response
exchanges with the agentic CLI assistant.
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = r"C:\Windows\Fonts\consola.ttf"
FONT_SIZE = 15
TITLE_FONT_SIZE = 13
PAD = 14
LINE_H = 21

BG = (18, 18, 24)
TITLEBAR = (40, 40, 52)
TITLE_TEXT = (200, 200, 210)
PROMPT = (120, 220, 140)      # green  - user prompt
LABEL = (255, 200, 90)        # amber  - section labels
ASSIST = (210, 215, 225)      # near-white - assistant text
CODE = (140, 190, 255)        # blue   - code lines
DIM = (130, 135, 150)         # grey   - meta
OK = (90, 220, 120)           # green  - success markers

font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
title_font = ImageFont.truetype(FONT_PATH, TITLE_FONT_SIZE)

_tmp = Image.new("RGB", (10, 10))
_d = ImageDraw.Draw(_tmp)
CHAR_W = int(_d.textlength("M", font=font))

COLS = 100
WIDTH = PAD * 2 + COLS * CHAR_W


def render(title, lines, out_path):
    rows = []
    for kind, text in lines:
        rows.append((kind, text))
    height = 40 + PAD * 2 + len(rows) * LINE_H + 10
    img = Image.new("RGB", (WIDTH, height), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, WIDTH, 34], fill=TITLEBAR)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([12 + i * 22, 11, 24 + i * 22, 23], fill=c)
    d.text((WIDTH // 2 - int(d.textlength(title, font=title_font) // 2), 9),
           title, font=title_font, fill=TITLE_TEXT)
    colors = {"prompt": PROMPT, "label": LABEL, "assist": ASSIST,
              "code": CODE, "dim": DIM, "ok": OK, "blank": BG}
    y = 40 + PAD
    for kind, text in rows:
        if kind != "blank":
            d.text((PAD, y), text, font=font, fill=colors[kind])
        y += LINE_H
    img.save(out_path)
    print("wrote", out_path, img.size)


# ---------------------------------------------------------------- row 1
render(
    "hermes-agent — expense-splitter session — zero-shot scaffold",
    [
        ("dim", "$ hermes-agent  (agentic CLI coding assistant, session 2026-08-27)"),
        ("blank", ""),
        ("label", "YOU ▸ prompt (zero-shot):"),
        ("prompt", "Create a Python project for an expense splitter: pyproject.toml"),
        ("prompt", "(setuptools, src layout, pytest config) and a package"),
        ("prompt", "src/expense_splitter with a function validate_members(members) that"),
        ("prompt", "raises ValueError if the member list is empty, contains blank names,"),
        ("prompt", "or contains duplicates."),
        ("blank", ""),
        ("label", "ASSISTANT ▸ response:"),
        ("assist", "Creating the src-layout scaffold and the validation function."),
        ("code", "pyproject.toml                          (new, setuptools + pytest)"),
        ("code", "src/expense_splitter/__init__.py        (new, public API exports)"),
        ("code", "src/expense_splitter/splitter.py        (new)"),
        ("blank", ""),
        ("code", "def validate_members(members: Iterable[str]) -> None:"),
        ("code", '    """Raise ``ValueError`` unless ``members`` is a non-empty'),
        ("code", '    collection of unique, non-blank names."""'),
        ("code", "    names = list(members)"),
        ("code", "    if len(names) == 0:"),
        ('code', '        raise ValueError("at least one member is required")'),
        ("code", "    if any(not isinstance(n, str) or not n.strip() for n in names):"),
        ('code', '        raise ValueError("member names must be non-empty strings")'),
        ("code", "    if len(set(names)) != len(names):"),
        ('code', '        raise ValueError("member names must be unique")'),
        ("blank", ""),
        ("ok", "✓ 3 checks in order: empty -> blank -> duplicate. Accepted as-is."),
        ("dim", "  technique: ZERO-SHOT — standard unambiguous scaffold/validation."),
    ],
    r"docs\screenshots\row1_zero_shot_scaffold.png",
)

# ---------------------------------------------------------------- row 5
render(
    "hermes-agent — expense-splitter session — few-shot test style",
    [
        ("label", "YOU ▸ prompt (few-shot, 3 examples embedded):"),
        ("prompt", "Write the pytest suite for everything so far, matching EXACTLY this"),
        ("prompt", "style — here are examples of the convention:"),
        ("blank", ""),
        ("code", "  def test_split_evenly_basic():"),
        ("code", '      assert split_evenly(Decimal("60"), 3) == \\'),
        ("code", '          [Decimal("20.00"), Decimal("20.00"), Decimal("20.00")]'),
        ("code", "  def test_split_evenly_single_share():"),
        ("code", '      assert split_evenly(Decimal("42.00"), 1) == [Decimal("42.00")]'),
        ("code", "  def test_split_evenly_rejects_nonpositive_n():"),
        ("code", "      with pytest.raises(ValueError):"),
        ("code", '          split_evenly(Decimal("10"), 0)'),
        ("blank", ""),
        ("prompt", "Same naming (test_<function>_<case>), Decimal literals, one assert"),
        ("prompt", "per test, pytest.raises for error cases."),
        ("blank", ""),
        ("label", "ASSISTANT ▸ response (excerpt):"),
        ("code", "tests/test_splitter.py"),
        ("code", "def test_validate_members_ok():"),
        ('code', '    validate_members(["alice", "bob", "carol"])  # no exception'),
        ("code", "def test_validate_members_duplicate():"),
        ("code", "    with pytest.raises(ValueError):"),
        ('code', '        validate_members(["alice", "alice"])'),
        ("code", "def test_validate_members_empty():"),
        ("code", "    with pytest.raises(ValueError):"),
        ("code", "        validate_members([])"),
        ("code", "def test_validate_members_blank_name():"),
        ("code", "    with pytest.raises(ValueError):"),
        ('code', '        validate_members(["alice", "  "])'),
        ("code", "def test_parse_expense_line():"),
        ('code', '    payer, amount, payees = parse_expense_line("alice 60.00 alice bob carol")'),
        ('code', '    assert payer == "alice"'),
        ('code', '    assert amount == Decimal("60.00")'),
        ('code', '    assert payees == ["alice", "bob", "carol"]'),
        ("code", "def test_parse_expense_line_too_short():"),
        ("code", "    with pytest.raises(ValueError):"),
        ('code', '        parse_expense_line("alice 60")'),
        ("blank", ""),
        ("ok", "✓ 12 tests, convention matched exactly. Accepted — one test left"),
        ("ok", "  red on purpose: the rounding-remainder test fails (see row 6)."),
        ("dim", "  an earlier zero-shot attempt returned unittest classes + string"),
        ("dim", "  amounts — the 3 examples pinned the style. technique: FEW-SHOT."),
    ],
    r"docs\screenshots\row5_few_shot_tests.png",
)

# ---------------------------------------------------------------- row 6
render(
    "hermes-agent — expense-splitter session — chain-of-thought debugging",
    [
        ("label", "YOU ▸ prompt (chain-of-thought):"),
        ("prompt", "test_split_evenly_rounding_remainder_goes_to_last is failing."),
        ("prompt", 'Splitting Decimal("10.00") three ways returns [3.33, 3.33, 3.33]'),
        ("prompt", "which sums to 9.99, not 10.00 — one cent vanishes. Think step by"),
        ("prompt", "step: trace exactly where the cent is lost in split_evenly, then"),
        ("prompt", "fix it so the shares ALWAYS sum exactly to the original amount."),
        ("prompt", "Explain your reasoning before changing code."),
        ("blank", ""),
        ("label", "ASSISTANT ▸ reasoning (step by step):"),
        ("assist", "1. 10.00 / 3 = 3.3333... (repeating)."),
        ("assist", "2. quantize(0.01, ROUND_HALF_EVEN) rounds each share to 3.33."),
        ("assist", "3. 3.33 x 3 = 9.99 — the 0.01 truncation remainder is dropped"),
        ("assist", "   because every share is computed independently."),
        ("assist", "4. Root cause: no share absorbs the remainder; the invariant"),
        ("assist", "   sum(shares) == amount is never enforced."),
        ("assist", "5. Fix: derive the LAST share as amount - share*(n-1) = 3.34."),
        ("assist", "   Then the sum is exact by construction, for any amount/n."),
        ("blank", ""),
        ("label", "ASSISTANT ▸ applying fix to split_evenly:"),
        ("code", "    share = raw.quantize(CENT, rounding=ROUND_HALF_EVEN)"),
        ("code", "    shares = [share] * (n - 1)"),
        ("code", "    shares.append(amount - share * (n - 1))   # <- absorbs remainder"),
        ("code", "    return shares"),
        ("blank", ""),
        ("label", "ASSISTANT ▸ re-running the suite:"),
        ("code", "$ .venv/Scripts/python.exe -m pytest tests/test_splitter.py -q"),
        ("code", "............                                                    [100%]"),
        ("ok", "12 passed in 0.03s"),
        ("blank", ""),
        ("ok", "✓ Root cause correct (independent rounding), invariant now holds."),
        ("dim", "  technique: CHAIN-OF-THOUGHT — forced trace surfaced the real cause"),
        ("dim", "  instead of a blind patch; verified by re-running the tests."),
    ],
    r"docs\screenshots\row6_cot_rounding_bug.png",
)

print("done")
