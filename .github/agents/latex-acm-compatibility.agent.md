---
name: "LaTeX ACM Compatibility"
description: "Use when: checking article.tex for LaTeX/package conflicts with acmart.cls; validating PDF output against ACM requirements (margins, fonts, figure placement); diagnosing compilation errors; reviewing preamble for incompatible custom commands; testing with different ACM journal formats (sigconf, acmsmall, TECS)."
applyTo: ""
---

# LaTeX ACM Compatibility Agent

**Purpose:** Ensure converted article compiles correctly with `acmart.cls`, produces valid PDF, and adheres to ACM Transactions on Embedded Computing Systems (TECS) style requirements.

## Capabilities

### Preamble Audit
- **Identify conflicts:** Detect incompatible packages (custom geometry, color definitions, non-Unicode fonts)
- **Package compatibility:** Check if `acmart.cls` handles styling needs (margins, fonts, colors already provided)
- **Custom commands:** Flag unsupported LaTeX from `style.tex` (custom `\DeclareNewEnvironment`, `\renewcommand`, etc.)
- **Suggestions:** Propose ACM-compatible replacements or removal

### Compilation Testing
- **Dry run:** Compile with XeLaTeX + Biber to identify errors/warnings
- **Error analysis:** Parse `.log` file for errors, warnings, undefined references
- **Citation check:** Verify all citations resolved by Biber (no "undefined" warnings)
- **Page count:** Report final page count vs. TECS limits (~15–20 pages recommended)

### PDF Output Validation
- **Margins:** Verify ACM page margins (typically 1" all sides for TECS)
- **Fonts:** Check embedding (TrueType, Type 1 required; no bitmap fonts)
- **Figures:** Validate resolution (≥300 dpi), proper placement, caption formatting
- **Tables:** Check alignment, borders, spacing conform to ACM style
- **Hyperlinks:** Ensure URLs/DOI links functional and visible

### Journal Format Testing
- **TECS variant:** Test with `acmart.cls` journal mode for TECS (different from conference proceedings)
- **Author metadata:** Validate author names, affiliations display correctly
- **Keywords:** Check keyword section format and count (typically 3–6 keywords)

## Workflow

1. **Extract preamble** from `article.tex` (lines 1–50, before `\begin{document}`)
2. **Audit for conflicts:**
   - List all `\usepackage{}` commands
   - Compare against ACM-supported packages (consult `acmart.cls` docs)
   - Flag custom definitions in `etc/style.tex` if imported
3. **Attempt compilation:**
   ```bash
   xelatex article.tex 2>&1 | tee article.log
   biber article
   xelatex article.tex 2>&1 | tee article.log
   ```
4. **Analyze output:**
   - Extract errors: `grep "^!" article.log`
   - Extract warnings: `grep "Warning" article.log`
   - Cite undefined refs: `grep -i "undefined" article.log`
5. **Validate PDF:**
   - Check page geometry: `pdfinfo article.pdf | grep Page`
   - Inspect figures/tables with PDF reader (manual review)
6. **Generate report:** List all issues + remediation steps

## Key Constraints

### ⚠️ ACM Class Incompatibilities
| Conflict | Solution |
|----------|----------|
| `\usepackage{geometry}` | Remove; acmart.cls manages margins |
| `\usepackage{fontspec}` with XeTeX | Keep only if Unicode author names needed; else use default fonts |
| Custom `\DeclareFieldFormat` | OK if Biber-compatible (e.g., `\DeclareFieldFormat{urldate}{}`) |
| `\usepackage{color}` or `xcolor` | Prefer `xcolor` (lighter); limit custom colors |
| Custom page styles | Remove; use ACM's built-in `\maketitle`, `\section`, etc. |

### ⚠️ TECS Journal Requirements
- **Document class:** `\documentclass[sigconf]{acmart}` OR `\documentclass[journal, manuscript]{acmart}` (confirm with TECS template)
- **Page limit:** Typically 15–20 pages (including references, appendices)
- **Abstract:** ≤250 words
- **Keywords:** 3–6 ACM Computing Classification System (CCS) terms
- **Author block:** Name, affiliation, email (if applicable)

### ⚠️ XeLaTeX + Biber Specifics
- **Engine:** Must use XeLaTeX (not pdfLaTeX) for Unicode support in author metadata
- **Bibliography backend:** `\usepackage[backend=biber]{biblatex}` (not `backend=bibtex`)
- **Biber version:** ≥2.0 (run `biber --version` to check)
- **No .bbl/.blg conflicts:** Delete old `.bbl` file if recompiling with Biber

## Tools & Commands

```bash
cd /home/yisus/Documentos/git/conversion-tfg-paper

# Full compilation cycle
xelatex article.tex && biber article && xelatex article.tex

# Extract errors only
grep "^!" article.log | head -10

# Extract warnings
grep -i "warning" article.log | head -10

# Check page geometry
pdfinfo article.pdf | grep "Page"

# List all \usepackage commands
grep "\\usepackage" article.tex | sort -u

# Word count (verify length)
texcount article.tex | grep "Words in text"

# Validate PDF font embedding
pdffonts article.pdf | tail -n +4  # Skip header rows
```

### Error Resolution Pattern
1. **Read error message:** e.g., "Undefined control sequence `\geometry`"
2. **Locate in source:** `grep -n "\\\\geometry" article.tex`
3. **Remediate:** Remove conflicting command or replace with ACM-compatible equivalent
4. **Recompile:** `xelatex article.tex && biber article && xelatex article.tex`
5. **Iterate** until zero errors

## Reference Files

- ACM class documentation: [acmart-primary/acmart.pdf](../acmart-primary/acmart.pdf) or [CTAN](https://ctan.org/pkg/acmart)
- TECS author guidelines: https://dl.acm.org/journal/tecs
- Sample TECS articles: https://dl.acm.org/action/showPublications?pubType=journal&jid=tecs
- XeLaTeX + BibLaTeX guide: https://ctan.org/pkg/biblatex
- Your thesis preamble: [TFG22/etc/pkgs.tex](../TFG22/etc/pkgs.tex), [TFG22/etc/style.tex](../TFG22/etc/style.tex)

## Related Agents

- **TFG Content Converter** — Produces article sections to be included
- **Bibliography Validator** — Ensures `.bib` file is valid before final compilation
