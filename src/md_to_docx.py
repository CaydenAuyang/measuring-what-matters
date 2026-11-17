"""Convert a Markdown file to a Word document with python-docx.

Handles: headings (# to ####), paragraphs, **bold**, *italic*, `code`, [text](url) links,
bullet and numbered lists (two levels), pipe tables, block quotes and fenced code blocks.
HTML comments are dropped, except three layout directives written as comments:
    <!-- pagebreak -->      start a new page
    <!-- wide-pages -->     start a new section with the page turned sideways (for wide tables)
    <!-- normal-pages -->   go back to upright pages

Layout: Times New Roman 12 pt, 1 inch margins, tables with a simple grid and 9 pt text,
page numbers centered in the footer.

Usage: python src/md_to_docx.py <input.md> <output.docx>
"""
import re, sys
from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

FONT = "Times New Roman"
MONO = "Courier New"
BODY_PT, TABLE_PT = 12, 9
HEADING_PT = {1: 16, 2: 14, 3: 12, 4: 12}
DIRECTIVES = {"pagebreak": "\x00PAGEBREAK", "wide-pages": "\x00WIDE", "normal-pages": "\x00NORMAL"}

COMMENT = re.compile(r"<!--(.*?)-->", re.S)
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
BULLET = re.compile(r"^(\s*)[-*+]\s+(.*)$")
NUMBERED = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
INLINE = re.compile(
    r"(?P<code>`[^`]+`)"
    r"|(?P<link>\[[^\]]+\]\(https?://[^\s)]+\))"
    r"|(?P<url>https?://[^\s<>|]*[^\s<>|.,;:)\]])"
    r"|(?P<bolditalic>\*\*\*.+?\*\*\*)"
    r"|(?P<bold>\*\*.+?\*\*)"
    r"|(?P<italic>(?<![\w*])\*(?!\s)[^*]+?(?<!\s)\*(?![\w*]))")


# ------------------------------------------------------------------ reading the Markdown
def strip_comments(text):
    def rep(m):
        word = m.group(1).strip().lower()
        return "\n\n" + DIRECTIVES[word] + "\n\n" if word in DIRECTIVES else ""
    return COMMENT.sub(rep, text)

def split_row(line):
    s = line.strip()
    if s.startswith("|"): s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"): s = s[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s)]

def parse_blocks(text):
    """Returns a list of blocks: (kind, payload)."""
    lines = strip_comments(text).replace("\r\n", "\n").split("\n")
    blocks, para, i = [], [], 0
    def flush():
        if para:
            blocks.append(("p", " ".join(s.strip() for s in para))); para.clear()
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s in DIRECTIVES.values():
            flush(); blocks.append(("directive", s)); i += 1; continue
        if not s:
            flush(); i += 1; continue
        if s.startswith("```"):
            flush(); code = []; i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i]); i += 1
            blocks.append(("code", code)); i += 1; continue
        m = HEADING.match(line)
        if m:
            flush(); blocks.append(("h", (len(m.group(1)), m.group(2)))); i += 1; continue
        if s.startswith("|") and i + 1 < len(lines) and TABLE_SEP.match(lines[i + 1]) and "-" in lines[i + 1]:
            flush()
            header = split_row(line); aligns = []
            for c in split_row(lines[i + 1]):
                aligns.append("center" if c.startswith(":") and c.endswith(":") else ("right" if c.endswith(":") else "left"))
            rows = []; i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i])); i += 1
            blocks.append(("table", (header, aligns, rows))); continue
        if re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", line):          # horizontal rule: left out
            flush(); i += 1; continue
        if s.startswith(">"):
            flush(); quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            blocks.append(("quote", quote)); continue
        m = BULLET.match(line) or NUMBERED.match(line)
        if m:
            flush(); items = []
            while i < len(lines):
                b, n = BULLET.match(lines[i]), NUMBERED.match(lines[i])
                if b:
                    items.append({"level": 1 if len(b.group(1)) >= 2 else 0, "numbered": False, "text": b.group(2)})
                elif n:
                    items.append({"level": 1 if len(n.group(1)) >= 2 else 0, "numbered": True, "text": n.group(3)})
                elif lines[i].strip() and lines[i].startswith(" ") and items:      # continuation line of the item above
                    items[-1]["text"] += " " + lines[i].strip()
                else:
                    break
                i += 1
            blocks.append(("list", items)); continue
        para.append(line); i += 1
    flush()
    return blocks


# ------------------------------------------------------------------ writing the document
def set_font(run, size=None, name=FONT, bold=None, italic=None):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts"); rpr.append(rfonts)
    for att in ("w:ascii", "w:hAnsi", "w:cs"):
        rfonts.set(qn(att), name)
    if size: run.font.size = Pt(size)
    if bold is not None: run.bold = bold
    if italic is not None: run.italic = italic
    run.font.color.rgb = RGBColor(0, 0, 0)

def add_link(par, text, url, size):
    """A clickable link: blue underlined text."""
    rid = par.part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    link = OxmlElement("w:hyperlink"); link.set(qn("r:id"), rid)
    r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    fonts = OxmlElement("w:rFonts")
    for att in ("w:ascii", "w:hAnsi", "w:cs"): fonts.set(qn(att), FONT)
    rpr.append(fonts)
    color = OxmlElement("w:color"); color.set(qn("w:val"), "0563C1"); rpr.append(color)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rpr.append(u)
    for tag in ("w:sz", "w:szCs"):
        sz = OxmlElement(tag); sz.set(qn("w:val"), str(int(size * 2))); rpr.append(sz)
    r.append(rpr)
    t = OxmlElement("w:t"); t.text = text; t.set(qn("xml:space"), "preserve"); r.append(t)
    link.append(r); par._p.append(link)

def add_inline(par, text, size=BODY_PT, bold=False, italic=False):
    """Write text with **bold**, *italic*, `code` and [text](url) into a paragraph."""
    pos = 0
    for m in INLINE.finditer(text):
        if m.start() > pos:
            set_font(par.add_run(unescape(text[pos:m.start()])), size, bold=bold or None, italic=italic or None)
        tok = m.group(0)
        if m.group("code"):
            set_font(par.add_run(tok[1:-1]), size - 1, name=MONO, bold=bold or None, italic=italic or None)
        elif m.group("link"):
            label, url = re.match(r"\[([^\]]+)\]\((.+)\)$", tok).groups()
            add_link(par, unescape(label), url, size)
        elif m.group("url"):
            add_link(par, tok, tok, size)
        elif m.group("bolditalic"):
            add_inline(par, tok[3:-3], size, True, True)
        elif m.group("bold"):
            add_inline(par, tok[2:-2], size, True, italic)
        elif m.group("italic"):
            add_inline(par, tok[1:-1], size, bold, True)
        pos = m.end()
    if pos < len(text):
        set_font(par.add_run(unescape(text[pos:])), size, bold=bold or None, italic=italic or None)

def unescape(s):
    return re.sub(r"\\([\\`*_{}\[\]()#+\-.!|>:&])", r"\1", s)

def spacing(par, before=0, after=6, line=1.15):
    f = par.paragraph_format
    f.space_before = Pt(before); f.space_after = Pt(after); f.line_spacing = line

def page_number_footer(section):
    par = section.footer.paragraphs[0] if section.footer.paragraphs else section.footer.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = par.add_run()
    for kind, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if kind:
            el = OxmlElement("w:fldChar"); el.set(qn("w:fldCharType"), kind)
        else:
            el = OxmlElement("w:instrText"); el.set(qn("xml:space"), "preserve"); el.text = text
        run._r.append(el)
    set_font(run, 10)

def set_margins(section):
    section.left_margin = section.right_margin = section.top_margin = section.bottom_margin = Inches(1)

def new_section(doc, wide):
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    w, h = sec.page_width, sec.page_height
    long_side, short_side = max(w, h), min(w, h)
    sec.orientation = WD_ORIENT.LANDSCAPE if wide else WD_ORIENT.PORTRAIT
    sec.page_width, sec.page_height = (long_side, short_side) if wide else (short_side, long_side)
    set_margins(sec)
    return sec

def repeat_header(row):
    trpr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader"); el.set(qn("w:val"), "true"); trpr.append(el)

def add_table(doc, header, aligns, rows):
    ncol = len(header)
    table = doc.add_table(rows=1 + len(rows), cols=ncol)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    amap = {"left": WD_ALIGN_PARAGRAPH.LEFT, "right": WD_ALIGN_PARAGRAPH.RIGHT, "center": WD_ALIGN_PARAGRAPH.CENTER}
    for r, cells in enumerate([header] + rows):
        cells = (cells + [""] * ncol)[:ncol]
        for c, text in enumerate(cells):
            par = table.cell(r, c).paragraphs[0]
            par.alignment = amap[aligns[c] if c < len(aligns) else "left"]
            spacing(par, 0, 0, 1.0)
            add_inline(par, text, TABLE_PT, bold=(r == 0))
    repeat_header(table.rows[0])
    after = doc.add_paragraph(); spacing(after, 0, 4, 1.0)

def convert(md_text, out_path):
    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = FONT; normal.font.size = Pt(BODY_PT)
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts"); rpr.append(rfonts)
    for att in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(att), FONT)
    set_margins(doc.sections[0])
    page_number_footer(doc.sections[0])

    seen_h2 = False; counters = {}
    for kind, payload in parse_blocks(md_text):
        if kind == "directive":
            if payload == DIRECTIVES["pagebreak"]:
                doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
            else:
                new_section(doc, wide=(payload == DIRECTIVES["wide-pages"]))
        elif kind == "h":
            level, text = payload
            level = min(level, 4)
            if level >= 2: seen_h2 = True
            par = doc.add_paragraph()
            par.paragraph_format.keep_with_next = True
            spacing(par, 14 if level <= 2 else 10, 6, 1.0)
            if level == 1: par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_inline(par, text, HEADING_PT[level], bold=True, italic=(level == 4))
        elif kind == "p":
            par = doc.add_paragraph(); spacing(par)
            if not seen_h2: par.alignment = WD_ALIGN_PARAGRAPH.CENTER       # title block
            if payload.startswith("**Table"): par.paragraph_format.keep_with_next = True   # keep a caption with its table
            add_inline(par, payload)
        elif kind == "quote":
            par = doc.add_paragraph(); spacing(par)
            par.paragraph_format.left_indent = Inches(0.4); par.paragraph_format.right_indent = Inches(0.4)
            add_inline(par, " ".join(s.strip() for s in payload if s.strip()), italic=True)
        elif kind == "code":
            for line in payload:
                par = doc.add_paragraph(); spacing(par, 0, 0, 1.0)
                par.paragraph_format.left_indent = Inches(0.3)
                set_font(par.add_run(line), BODY_PT - 2, name=MONO)
            spacing(doc.add_paragraph(), 0, 2, 1.0)
        elif kind == "list":
            counters = {0: 0, 1: 0}
            for it in payload:
                lv = it["level"]
                if lv == 0: counters[1] = 0
                par = doc.add_paragraph(); spacing(par, 0, 3)
                par.paragraph_format.left_indent = Inches(0.25 + 0.25 * lv + 0.25)
                par.paragraph_format.first_line_indent = Inches(-0.25)
                if it["numbered"]:
                    counters[lv] += 1; marker = f"{counters[lv]}.\t"
                else:
                    marker = ("•" if lv == 0 else "◦") + "\t"
                set_font(par.add_run(marker), BODY_PT)
                par.paragraph_format.tab_stops.add_tab_stop(Inches(0.25 + 0.25 * lv + 0.25))
                add_inline(par, it["text"])
        elif kind == "table":
            add_table(doc, *payload)
    doc.save(out_path)
    return out_path

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python src/md_to_docx.py <input.md> <output.docx>")
    convert(open(sys.argv[1], encoding="utf-8").read(), sys.argv[2])
    print("wrote", sys.argv[2])
