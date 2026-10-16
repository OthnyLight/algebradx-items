#!/usr/bin/env python3
"""Build the printable PDFs from the item bank.

  exports/student_form_A.pdf, exports/student_form_B.pdf   20-item parallel forms
  exports/teacher_guide.pdf                                 item-by-item diagnosis and teaching moves

Every page carries a DRAFT watermark unless run with --final (only after the author's
verification; see docs/VERIFY_CHECKLIST.md).
Usage: python code/03_print.py [--final]
"""
import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib
import yaml
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

ROOT = Path(__file__).resolve().parent.parent
FINAL = "--final" in sys.argv

# Fonts: DejaVu ships inside matplotlib, so this works on any machine with the requirements installed.
FD = Path(matplotlib.get_data_path()) / "fonts/ttf"
pdfmetrics.registerFont(TTFont("Sans", str(FD / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("Sans-Bold", str(FD / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Sans-Oblique", str(FD / "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("Serif", str(FD / "DejaVuSerif.ttf")))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-Bold", italic="Sans-Oblique",
                              boldItalic="Sans-Bold")

INK = colors.HexColor("#1F2933")
MUTED = colors.HexColor("#5B6770")
ACCENT = colors.HexColor("#0F5E63")
SOFT = colors.HexColor("#EEF4F4")
RULE = colors.HexColor("#C9D3D6")
KEYC = colors.HexColor("#1B7F3B")

S = {
    "title": ParagraphStyle("title", fontName="Sans-Bold", fontSize=24, leading=29, textColor=INK),
    "sub": ParagraphStyle("sub", fontName="Sans", fontSize=12, leading=16, textColor=MUTED),
    "h1": ParagraphStyle("h1", fontName="Sans-Bold", fontSize=16, leading=20, textColor=ACCENT,
                         spaceBefore=6, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="Sans-Bold", fontSize=11.5, leading=15, textColor=INK,
                         spaceBefore=8, spaceAfter=3),
    "body": ParagraphStyle("body", fontName="Serif", fontSize=10, leading=14.2, textColor=INK,
                           spaceAfter=5),
    "small": ParagraphStyle("small", fontName="Sans", fontSize=8.2, leading=11, textColor=MUTED),
    "cell": ParagraphStyle("cell", fontName="Sans", fontSize=8.4, leading=11, textColor=INK),
    "cellb": ParagraphStyle("cellb", fontName="Sans-Bold", fontSize=8.4, leading=11, textColor=INK),
    "stem": ParagraphStyle("stem", fontName="Serif", fontSize=11, leading=15.5, textColor=INK),
    "opt": ParagraphStyle("opt", fontName="Serif", fontSize=10.5, leading=14.5, textColor=INK),
    "itemhead": ParagraphStyle("itemhead", fontName="Sans-Bold", fontSize=9, leading=12,
                               textColor=colors.white),
    "center": ParagraphStyle("center", fontName="Sans", fontSize=9, leading=12, alignment=TA_CENTER,
                             textColor=MUTED),
}

_MINUS = re.compile(r"(?<![A-Za-z'])-")


def m(text):
    """Escape for ReportLab and use a true minus sign in mathematics (hyphens between letters stay)."""
    return escape(_MINUS.sub("−", str(text)))


def load():
    bank = yaml.safe_load((ROOT / "items/items.yaml").read_text())["items"]
    cat = yaml.safe_load((ROOT / "items/misconceptions.yaml").read_text())
    strands = yaml.safe_load((ROOT / "items/strands.yaml").read_text())
    stats = json.loads((ROOT / "docs/stats.json").read_text())
    authors = json.loads((ROOT / "AUTHORS.json").read_text())["authors"]
    return bank, cat, strands, stats, authors


def page_deco(label, author):
    def deco(canvas, doc):
        canvas.saveState()
        w, h = letter
        canvas.setFont("Sans", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(0.75 * inch, 0.5 * inch,
                          f"{label}  ·  © {author}  ·  CC BY 4.0")
        canvas.drawRightString(w - 0.75 * inch, 0.5 * inch, f"{doc.page}")
        if not FINAL:
            canvas.setFont("Sans-Bold", 64)
            canvas.setFillColor(colors.Color(0.75, 0.2, 0.2, alpha=0.10))
            canvas.translate(w / 2, h / 2)
            canvas.rotate(35)
            canvas.drawCentredString(0, 0, "DRAFT")
            canvas.restoreState()
            canvas.saveState()
            canvas.setFont("Sans-Bold", 7.5)
            canvas.setFillColor(colors.HexColor("#A33"))
            canvas.drawString(0.75 * inch, h - 0.45 * inch,
                              "DRAFT: not yet verified by the author. Do not use with students or cite.")
        canvas.restoreState()
    return deco


def doc(path, title, author):
    return SimpleDocTemplate(str(path), pagesize=letter, title=title, author=author,
                             leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                             topMargin=0.7 * inch, bottomMargin=0.75 * inch)


# ------------------------------------------------------------------ student forms
def student_form(form, bank, strands, stats, author):
    by_id = {i["id"]: i for i in bank}
    path = ROOT / f"exports/student_form_{form}.pdf"
    story = []
    story.append(Paragraph(f"Algebra Readiness Check · Form {form}", S["title"]))
    story.append(Spacer(1, 6))
    hdr = Table([["Name", "", "Class", "", "Date", ""]],
                colWidths=[0.5 * inch, 2.6 * inch, 0.5 * inch, 1.3 * inch, 0.45 * inch, 1.05 * inch])
    hdr.setStyle(TableStyle([("FONT", (0, 0), (-1, -1), "Sans", 9),
                             ("TEXTCOLOR", (0, 0), (-1, -1), MUTED),
                             ("LINEBELOW", (1, 0), (1, 0), 0.6, RULE),
                             ("LINEBELOW", (3, 0), (3, 0), 0.6, RULE),
                             ("LINEBELOW", (5, 0), (5, 0), 0.6, RULE)]))
    story += [hdr, Spacer(1, 10)]
    story.append(Paragraph(
        "Choose the best answer and circle its letter. Show any work in the space beside the "
        "question. This check is not graded; it helps your teacher see how you are thinking, "
        "so a careful guess is better than a blank.", S["body"]))
    story.append(Spacer(1, 6))
    for n, iid in enumerate(stats[f"form_{form}"], 1):
        it = by_id[iid]
        opts = [[Paragraph(f"<b>{L}</b>", S["opt"]), Paragraph(m(it["options"][L]["text"]), S["opt"])]
                for L in "ABCD"]
        ot = Table(opts, colWidths=[0.3 * inch, 5.9 * inch])
        ot.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                                ("TOPPADDING", (0, 0), (-1, -1), 1)]))
        block = Table([[Paragraph(f"<b>{n}.</b>", S["stem"]), Paragraph(m(it["stem"]), S["stem"])],
                       ["", ot]], colWidths=[0.4 * inch, 6.6 * inch])
        block.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("LINEBELOW", (0, 1), (-1, 1), 0.4, RULE),
                                   ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
                                   ("TOPPADDING", (0, 0), (-1, 0), 8)]))
        story.append(KeepTogether(block))
    d = doc(path, f"Algebra Readiness Check Form {form}", author)
    deco = page_deco(f"AlgebraDx Form {form}", author)
    d.build(story, onFirstPage=deco, onLaterPages=deco)
    return path


# ------------------------------------------------------------------ teacher guide
def item_block(it, cat, strands, form_pos):
    head = Table([[Paragraph(f"{it['id']}  ·  {escape(strands[it['strand']]['name'])}", S["itemhead"]),
                   Paragraph(f"Difficulty {it['difficulty']} (hypothesized)  ·  {form_pos}",
                             ParagraphStyle("r", parent=S["itemhead"], fontName="Sans", alignment=2))]],
                 colWidths=[3.9 * inch, 3.1 * inch])
    head.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT),
                              ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    meta = Paragraph(f"<b>Diagnoses:</b> {m(it['skill'])}  ·  <b>CCSS:</b> {', '.join(it['ccss'])}  ·  "
                     f"<b>NAEP focus:</b> {escape(it['naep_focus'])}", S["small"])
    stem = Paragraph(m(it["stem"]), S["stem"])
    rows = [[Paragraph("<b>Choice</b>", S["cellb"]), Paragraph("<b>What it suggests</b>", S["cellb"]),
             Paragraph("<b>Misconception</b>", S["cellb"])]]
    style = [("GRID", (0, 0), (-1, -1), 0.4, RULE), ("BACKGROUND", (0, 0), (-1, 0), SOFT),
             ("VALIGN", (0, 0), (-1, -1), "TOP")]
    for r, L in enumerate("ABCD", 1):
        txt = m(it["options"][L]["text"])
        if L == it["key"]:
            rows.append([Paragraph(f"<b>{L}</b>  {txt}", S["cell"]),
                         Paragraph("<font color='#1B7F3B'><b>Correct.</b></font>", S["cell"]), ""])
            style.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#EAF5EE")))
        else:
            d = it["distractors"][L]
            rows.append([Paragraph(f"<b>{L}</b>  {txt}", S["cell"]), Paragraph(m(d["reveals"]), S["cell"]),
                         Paragraph(f"<b>{d['code']}</b><br/>{escape(cat[d['code']]['name'])}", S["cell"])])
    tbl = Table(rows, colWidths=[2.0 * inch, 3.3 * inch, 1.7 * inch])
    tbl.setStyle(TableStyle(style))
    move = Table([[Paragraph(f"<b>Teaching move.</b> {m(it['teaching_move'])}", S["cell"])]],
                 colWidths=[7.0 * inch])
    move.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), SOFT),
                              ("LINEBEFORE", (0, 0), (0, -1), 2.5, ACCENT),
                              ("LEFTPADDING", (0, 0), (-1, -1), 8)]))
    return KeepTogether([head, Spacer(1, 4), meta, Spacer(1, 5), stem, Spacer(1, 6), tbl,
                         Spacer(1, 5), move, Spacer(1, 16)])


def teacher_guide(bank, cat, strands, stats, authors):
    author = authors[0]
    path = ROOT / "exports/teacher_guide.pdf"
    pos = {iid: f"Form A #{n}" for n, iid in enumerate(stats["form_A"], 1)}
    pos.update({iid: f"Form B #{n}" for n, iid in enumerate(stats["form_B"], 1)})
    st = []
    st.append(Spacer(1, 1.4 * inch))
    st.append(Paragraph("AlgebraDx", ParagraphStyle("k", parent=S["sub"], textColor=ACCENT,
                                                    fontName="Sans-Bold", fontSize=13)))
    st.append(Paragraph("Open Diagnostic Item Bank for Algebra Readiness", S["title"]))
    st.append(Spacer(1, 8))
    st.append(Paragraph(f"Teacher guide · Grades 9–12 · Version {stats['version']}", S["sub"]))
    st.append(Spacer(1, 30))
    st.append(Paragraph(f"{escape(author['name'])}<br/>{escape(author['affiliation'])}<br/>"
                        f"ORCID {author['orcid']}", S["body"]))
    st.append(Spacer(1, 24))
    st.append(Paragraph(
        f"{stats['n_items']} original multiple-choice items in {stats['n_strands']} strands. Every wrong "
        f"answer is written to reveal one of {stats['n_misconception_codes_catalog']} documented "
        f"misconceptions, and every misconception comes with a teaching move. No student data is collected. "
        f"Schools calibrate the items on their own students with the included kit.", S["body"]))
    st.append(Spacer(1, 1.6 * inch))
    st.append(Paragraph(
        "Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0). You may copy, adapt and "
        "share these items for any purpose, including commercial use, with attribution to the author. "
        "Items were drafted with AI assistance from the published misconception research and reviewed and "
        "verified by the author. No NAEP or TIMSS item text is reproduced.", S["small"]))
    st.append(PageBreak())

    st.append(Paragraph("How to use this bank", S["h1"]))
    for h, b in [
        ("1. Give a form (20 minutes).", "Forms A and B are parallel 20-item checks covering all eight strands. "
         "Use one as a start-of-unit diagnostic and the other after re-teaching. Tell students the check is "
         "not graded and that a careful guess is useful."),
        ("2. Read the wrong answers, not just the score.", "Each wrong option points to a specific "
         "misconception code. A student who chooses two or more options with the same code is showing a "
         "pattern worth acting on. One isolated choice may be a slip."),
        ("3. Confirm with the probe.", "Before re-teaching, ask the one-line probe question listed for that "
         "code in Appendix A. A 30-second conversation separates a misconception from a careless error."),
        ("4. Teach the move, then re-check.", "Each item and each code carries a teaching move drawn from "
         "the research. Use the parallel form, or any other item with the same code, to check the change."),
        ("5. Calibrate locally (optional).", "The difficulty levels in this guide are the author's "
         "hypotheses. To get real difficulty and discrimination values for your students, enter responses in "
         "calibration/response_template.csv and run calibration/calibrate.py. Data stays in your school."),
    ]:
        st.append(Paragraph(f"<b>{h}</b> {escape(b)}", S["body"]))
    st.append(Paragraph("The eight strands", S["h2"]))
    rows = [[Paragraph("<b>Strand</b>", S["cellb"]), Paragraph("<b>Why it matters for readiness</b>", S["cellb"]),
             Paragraph("<b>Items</b>", S["cellb"])]]
    for code, s in strands.items():
        ids = ", ".join(i["id"] for i in bank if i["strand"] == code)
        rows.append([Paragraph(f"<b>{code}</b> {escape(s['name'])}", S["cell"]), Paragraph(escape(s["why"]), S["cell"]),
                     Paragraph(ids, S["cell"])])
    t = Table(rows, colWidths=[1.7 * inch, 3.9 * inch, 1.4 * inch])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, RULE), ("BACKGROUND", (0, 0), (-1, 0), SOFT),
                           ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    st.append(t)
    st.append(PageBreak())

    for code, s in strands.items():
        st.append(Paragraph(f"{code} · {escape(s['name'])}", S["h1"]))
        for it in [i for i in bank if i["strand"] == code]:
            st.append(item_block(it, cat, strands, pos[it["id"]]))
        st.append(PageBreak())

    st.append(Paragraph("Appendix A · Misconception catalog", S["h1"]))
    st.append(Paragraph("Each code lists what it suggests about a student's thinking, a teaching move, and a "
                        "quick probe to confirm the diagnosis. Bracketed keys refer to Appendix C.", S["body"]))
    for code, c in cat.items():
        used = [i["id"] + L for i in bank for L, d in i["distractors"].items() if d["code"] == code]
        rows = [[Paragraph(f"<b>{code}</b> · {escape(c['name'])}", S["cellb"])],
                [Paragraph(f"<b>Suggests:</b> {m(c['reveals'])}", S["cell"])],
                [Paragraph(f"<b>Move:</b> {m(c['move'])}", S["cell"])],
                [Paragraph(f"<b>Probe:</b> {m(c['probe'])}", S["cell"])],
                [Paragraph(f"<b>Options:</b> {', '.join(used)}   <b>Research:</b> "
                           f"{', '.join('[' + r + ']' for r in c['refs'])}", S["small"])]]
        t = Table(rows, colWidths=[7.0 * inch])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), SOFT), ("BOX", (0, 0), (-1, -1), 0.4, RULE),
                               ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
        st.append(KeepTogether([t, Spacer(1, 6)]))
    st.append(PageBreak())

    st.append(Paragraph("Appendix B · Answer keys and scoring grids", S["h1"]))
    by_id = {i["id"]: i for i in bank}
    for form in ("A", "B"):
        st.append(Paragraph(f"Form {form}", S["h2"]))
        rows = [[Paragraph(f"<b>{h}</b>", S["cellb"]) for h in ("#", "Item", "Key", "A", "B", "C", "D")]]
        for n, iid in enumerate(stats[f"form_{form}"], 1):
            it = by_id[iid]
            rows.append([str(n), iid, it["key"]] +
                        [("✓" if L == it["key"] else it["distractors"][L]["code"]) for L in "ABCD"])
        t = Table(rows, colWidths=[0.35 * inch, 0.75 * inch, 0.45 * inch] + [1.36 * inch] * 4, repeatRows=1)
        t.setStyle(TableStyle([("FONT", (0, 1), (-1, -1), "Sans", 7.6), ("GRID", (0, 0), (-1, -1), 0.4, RULE),
                               ("BACKGROUND", (0, 0), (-1, 0), SOFT), ("TEXTCOLOR", (0, 1), (-1, -1), INK)]))
        st.append(t)
        st.append(Spacer(1, 10))
    st.append(PageBreak())
    st.append(Paragraph("Appendix C · References", S["h1"]))
    for line in (ROOT / "docs/REFERENCES.md").read_text().splitlines():
        if line.startswith("**["):
            txt = escape(line)
            txt = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", txt)
            txt = re.sub(r"\*(.+?)\*", r"<i>\1</i>", txt)
            st.append(Paragraph(txt, ParagraphStyle("ref", parent=S["body"], fontSize=8.8, leading=12)))

    d = doc(path, "AlgebraDx Teacher Guide", author["name"])
    deco = page_deco("AlgebraDx Teacher Guide v" + stats["version"], author["name"])
    d.build(st, onFirstPage=deco, onLaterPages=deco)
    return path


def main():
    bank, cat, strands, stats, authors = load()
    for f in ("A", "B"):
        print(student_form(f, bank, strands, stats, authors[0]["name"]))
    print(teacher_guide(bank, cat, strands, stats, authors))


if __name__ == "__main__":
    main()
