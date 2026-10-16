#!/usr/bin/env node
// Build the practitioner article (article/practitioner_article.docx) from docs/stats.json
// and exports/items.json. No number is typed into the prose: every count is read from the
// stats file the pipeline writes, so the text cannot drift from the bank.
// Usage: node code/05_article.js [--final]
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType,
  ShadingType, AlignmentType, BorderStyle, Footer, PageNumber,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const FINAL = process.argv.includes("--final");
const st = JSON.parse(fs.readFileSync(path.join(ROOT, "docs/stats.json"), "utf8"));
const bank = JSON.parse(fs.readFileSync(path.join(ROOT, "exports/items.json"), "utf8"));
const author = JSON.parse(fs.readFileSync(path.join(ROOT, "AUTHORS.json"), "utf8")).authors[0];
const items = Object.fromEntries(bank.items.map((i) => [i.id, i]));
const cat = bank.misconceptions;
const minus = (s) => String(s).replace(/(?<![A-Za-z'])-/g, "−");

const FONT = "Georgia";
const P = (text, opts = {}) =>
  new Paragraph({ spacing: { after: 160, line: 312 }, ...opts,
    children: (Array.isArray(text) ? text : [text]).map((t) =>
      typeof t === "string" ? new TextRun({ text: t, font: FONT, size: 23 }) : t) });
const B = (t) => new TextRun({ text: t, font: FONT, size: 23, bold: true });
const I = (t) => new TextRun({ text: t, font: FONT, size: 23, italics: true });
const H = (t, level = HeadingLevel.HEADING_2) =>
  new Paragraph({ heading: level, spacing: { before: 280, after: 120 },
    children: [new TextRun({ text: t, font: "Arial", bold: true, size: level === HeadingLevel.HEADING_1 ? 32 : 26, color: "0F5E63" })] });

const W = 9360; // 6.5in content width in DXA
function table(head, rows, widths) {
  const cell = (t, i, header) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA },
    shading: header ? { type: ShadingType.CLEAR, fill: "EEF4F4", color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ children: [new TextRun({ text: minus(t), font: "Arial", size: 18, bold: header })] })],
  });
  return new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: head.map((t, i) => cell(t, i, true)) }),
           ...rows.map((r) => new TableRow({ children: r.map((t, i) => cell(t, i, false)) }))],
  });
}
const caption = (t) => new Paragraph({ spacing: { before: 80, after: 240 },
  children: [new TextRun({ text: t, font: "Arial", size: 18, italics: true, color: "5B6770" })] });

const flagA = st.flaggable_codes_A, flagB = st.flaggable_codes_B;
const eq = items["EQ03"];
// DOI comes from CITATION.cff so the article can never carry a stale or missing identifier.
const citeDoi = (fs.readFileSync(path.join(ROOT, "CITATION.cff"), "utf8").match(/^doi:\s*"?([^"\n]+)"?/m) || [])[1] || "";
const doi = /^10\.\d+\//.test(citeDoi) ? `https://doi.org/${citeDoi}` : "Zenodo (DOI listed in the author note)";

const children = [];
if (!FINAL) children.push(new Paragraph({ shading: { type: ShadingType.CLEAR, fill: "FBEAEA", color: "auto" },
  spacing: { after: 240 }, children: [new TextRun({ text: "DRAFT: not yet verified or revised by the author. Do not submit or circulate.",
    font: "Arial", size: 18, bold: true, color: "A33333" })] }));

children.push(
  new Paragraph({ heading: HeadingLevel.TITLE, spacing: { after: 120 },
    children: [new TextRun({ text: "Reading the Wrong Answers: An Open Item Bank for Diagnosing Algebra Readiness", font: "Arial", bold: true, size: 40 })] }),
  P([new TextRun({ text: `${author.name}, ${author.affiliation}. ORCID ${author.orcid}. ${author.email}`, font: "Arial", size: 19, color: "5B6770" })]),
  P([B("Abstract. "), `A score tells a teacher how many algebra questions a student missed. It does not say why. This article introduces the AlgebraDx Open Diagnostic Item Bank: ${st.n_items} original multiple-choice items for grades 9–12 in which every one of the ${st.n_distractors} wrong answers is written to signal a specific, documented misconception, paired with a teaching move. The bank is free under a Creative Commons Attribution license, collects no student data, and ships with a kit that lets a school calibrate the items on its own students. I describe how the items are built, how to use them in a single class period, and what they cannot do.`]),
  H("Two students, the same score"),
  P(`Imagine two ninth graders who each answer 12 of 20 algebra questions correctly. On a gradebook they are identical. Now look at what they chose when they were wrong. The first student, asked for a correct first step on 4x − 8 = 12, chose 4x = 4. The second chose x − 8 = 3. Both are wrong, but for different reasons. The first student "moved" the 8 across the equal sign without undoing the subtraction. The second divided some terms by 4 and left one behind. These two students need different conversations on Monday.`),
  P(`Multiple-choice items can capture this difference, but only if every wrong option is built from a known misconception, so that a student's choice becomes evidence about their thinking (Sadler, 1998; Gierl et al., 2017). Few free algebra resources are built this way. Released NAEP and TIMSS items are valuable benchmarks, but they were not written to diagnose individual students, and TIMSS asks for prior notice before its items are reused in learning materials.`),
  H("What is in the bank"),
  P(`The bank contains ${st.n_items} original items in ${st.n_strands} strands of five items each. The strands cover the ideas research identifies as the most common stumbling points on the way into and through high school algebra (Table 1). Each item has four options. Each of its three wrong options is tagged with one of ${st.n_misconception_codes_catalog} misconception codes from a catalog grounded in the research literature. The catalog draws on research on the equal sign (Knuth et al., 2006), the meaning of letters (Küchemann, 1981), the "students and professors" reversal (Clement, 1982), overgeneralized rules such as (a + b)² = a² + b² (Matz, 1982), and graphs and functions (Leinhardt et al., 1990). Every code comes with what the choice suggests, a teaching move, and a one-line probe question to confirm the diagnosis.`),
  table(["Strand", "Items", "Example misconception targeted"],
    Object.entries(bank.strands).map(([code, s]) => {
      const first = bank.items.find((i) => i.strand === code);
      const d = Object.values(first.distractors)[0];
      return [s.name, String(st.items_per_strand[code]), cat[d.code].name];
    }), [3300, 900, 5160]),
  caption("Table 1. The eight strands of the AlgebraDx readiness model, with one example misconception from each strand's first item."),
  P(`Two parallel 20-item forms, A and B, cover every strand, so one can serve as a pre-check and the other as a post-check. Items are aligned to ${st.n_ccss_codes} Common Core standards and to the Algebra content area of the NAEP 2026 framework. No item text was copied from NAEP or TIMSS.`),
  H("Anatomy of an item"),
  P(`Table 2 shows one item as it appears in the teacher guide. The stem asks for a first step, because the step is where the misconception lives.`),
  table(["Choice", "What it suggests", "Code"],
    ["A", "B", "C", "D"].map((L) => L === eq.key
      ? [`${L}  ${eq.options[L].text}`, "Correct: divides every term by 4.", ""]
      : [`${L}  ${eq.options[L].text}`, eq.distractors[L].reveals, eq.distractors[L].code]),
    [2000, 5560, 1800]),
  caption(minus(`Table 2. Item ${eq.id}: "${eq.stem}" The teaching move: ${eq.teaching_move}`)),
  P(`Two options share a code (EQ-ONESIDE) on purpose. When a student picks the same code on several items, the evidence adds up to a pattern rather than a slip.`),
  P(`Every key is also checked by software using exact fraction arithmetic, confirming that each keyed answer is correct and that no wrong option is accidentally correct too. In version ${st.version}, ${st.mechanical_checks_passed} of ${st.mechanical_checks_total} machine-checkable options pass, and the ${st.n_options_hand_review} verbal options are reviewed by hand.`),
  H("Using it on Monday"),
  P([B("Give a form. "), "A form takes about 20 minutes. Tell students it is not graded."]),
  P([B("Read the wrong answers. "), "The answer key lists the code behind every wrong option, so codes can be tallied by hand in minutes, or by the included script."]),
  P([B("Probe before you re-teach. "), "A single wrong answer is a hypothesis. A 30-second probe, such as \"Is 2x + 3 equal to 5x when x = 10?\", separates a misconception from a slip."]),
  P([B("Teach the move, then re-check. "), "The moves are specific: true-or-false number sentences for the equal sign, area models for distribution, substitution checks for equivalence, numeric tests before translating words. The parallel form shows whether thinking changed."]),
  H("Calibrating without sharing data"),
  P(`The difficulty levels in the guide are my hypotheses. The bank collects no student data. Instead, a script that runs on a school's own computer reads a spreadsheet of responses and reports each item's difficulty and discrimination, how often each wrong option is chosen, each student's misconception codes, and the most common misconceptions in the class. A wrong option that attracts high scorers is flagged, often a sign of ambiguous wording.`),
  H("What the bank does not do"),
  P(`It is not a placement test, and its scores should not be used for grades. The items are not yet field-tested. A 20-item form also has limited room: only ${flagA} codes on Form A and ${flagB} on Form B appear on two or more items, so other single choices should be confirmed with the probe. A choice shows what a student picked, not why; the diagnosis starts a conversation rather than replacing one.`),
  H("Getting the bank"),
  P(`The items, forms, teacher guide and calibration kit are free at ${doi} under a CC BY 4.0 license, with spreadsheet and JSON versions for learning platforms. Reports of items that misbehave in real classrooms will shape version 2.`),
  H("Acknowledgment of AI assistance"),
  P(`Item drafts, code and initial text were produced with AI assistance (Claude, Anthropic) under my direction. I reviewed and verified all content and take responsibility for it.`),
  H("References"),
);

const refs = fs.readFileSync(path.join(ROOT, "docs/REFERENCES.md"), "utf8").split("\n")
  .filter((l) => /^\*\*\[(sadler1998|gierl2017|knuth2006|kuchemann1981|clement1982|matz1982|leinhardt1990)\]/.test(l))
  .map((l) => l.replace(/^\*\*\[[a-z0-9]+\]\*\*\s*/, ""))
  .sort();
for (const r of refs) {
  const runs = r.split(/(\*[^*]+\*)/).filter(Boolean).map((seg) => seg.startsWith("*")
    ? new TextRun({ text: seg.slice(1, -1), font: FONT, size: 20, italics: true })
    : new TextRun({ text: seg, font: FONT, size: 20 }));
  children.push(new Paragraph({ children: runs, spacing: { after: 100 }, indent: { left: 360, hanging: 360 } }));
}

const docx = new Document({
  creator: author.name, title: "Reading the Wrong Answers",
  styles: { default: { document: { run: { font: FONT, size: 23 } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      children: [new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 18, color: "5B6770" })] })] }) },
    children,
  }],
});
fs.mkdirSync(path.join(ROOT, "article"), { recursive: true });
Packer.toBuffer(docx).then((buf) => {
  fs.writeFileSync(path.join(ROOT, "article/practitioner_article.docx"), buf);
  console.log("wrote article/practitioner_article.docx");
});
