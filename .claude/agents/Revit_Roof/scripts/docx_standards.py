"""List the standards a project Word document (ТЗ / specification, .docx) already names.

Revit_Roof uses this before a roof code check: if the document names any
standards, those are the basis and the roof-code-check skill's own rules are
NOT added (roof-code-check SKILL.md §0).

Usage:
  python -I docx_standards.py <file.docx> [--context N]
Prints JSON: {"file", "has_standards", "standards": [{"ref", "count", "context"}],
              "roof_mentions": [...]} — context = N chars around the first hit (default 120).
Standard library only; reads word/document.xml (body text; headers/footers/tables included
because tables live in document.xml).
"""
import json
import re
import sys
import zipfile

# Code families seen in RU / TR / EU / US / international project documents.
PATTERNS = [
    r"СП\s*\d[\d.]*(?:-\d+)?",            # СП 478.1325800.2019, СП 17.13330.2017
    r"СНиП\s*[\d.\-*]+",
    r"ГОСТ(?:\s*Р)?(?:\s*(?:ISO|ИСО|EN|ЕН|IEC|МЭК))?\s*[\d.\-]+",
    r"СанПиН\s*[\d.\-]+",
    r"ВСН\s*[\d.\-]+",
    r"TS\s*EN(?:\s*ISO)?\s*[\d\-]+(?:[:/]\d+)?",
    r"TS\s*\d{2,5}(?:[\-/]\d+)?",
    r"(?:BS\s*)?EN(?:\s*ISO)?\s*\d{2,5}(?:-\d+)*",
    r"ISO\s*\d{2,5}(?:-\d+)*",
    r"DIN\s*\d{2,5}",
    r"IBC(?:\s*\d{4})?",
    r"NFPA\s*\d+",
    r"ASTM\s*[A-Z]\s*\d+",
    r"ASCE\s*\d+",
    r"UL\s*\d{3,4}",
    r"ICAO(?:\s*Annex\s*\d+)?",
    r"STANAG\s*\d+",
    # Generic "comply with national norms" clauses with no number.
    r"(?<![\w])(?:СП|ГОСТ|СНиП|СанПиН|ТУ)(?=[\s,.;])(?!\s*(?:Р\s*)?\d)",
    r"Yönetmeli[kğ]\w*",                  # Turkish "Yönetmelik" = regulation; matches document text, keep in Turkish
]
# Roof words to search for: Russian (кровля, крыша), Turkish (çatı) and English; keep as-is.
ROOF_WORDS = r"кровл\w*|крыш\w*|çatı\w*|roof\w*"


def main(path, ctx=120):
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml))
    found = {}
    for pat in PATTERNS:
        for m in re.finditer(pat, text):
            ref = re.sub(r"\s+", " ", m.group(0)).strip()
            if ref not in found:
                found[ref] = {"ref": ref, "count": 0,
                              "context": text[max(0, m.start() - ctx):m.end() + ctx]}
            found[ref]["count"] += 1
    roof = [text[max(0, m.start() - ctx):m.end() + ctx] for m in re.finditer(ROOF_WORDS, text, re.I)]
    out = {"file": path, "has_standards": bool(found),
           "standards": sorted(found.values(), key=lambda d: -d["count"]),
           "roof_mentions": roof}
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    args = sys.argv[1:]
    n = int(args[args.index("--context") + 1]) if "--context" in args else 120
    main(args[0], n)
