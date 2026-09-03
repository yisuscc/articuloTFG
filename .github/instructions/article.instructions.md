---
applyTo: "article.tex"
description: "Instructions for editing article.tex (the converted ACM article). Use when working on the main article document to maintain ACM compatibility and style consistency."
---

# Article.tex Editing Instructions

This file will contain your converted article in ACM Transactions format.

## Key Constraints for This File

### Structure
- **Document class:** `\documentclass{acmart}` with `acmart.cls` (ACM-provided)
- **Language:** English only (no Spanish content)
- **Bibliography backend:** `backend=biber` in BibLaTeX preamble
- **Page limit:** Typically 15–20 pages for TECS

### Content Guidelines
- **Title:** Brief, descriptive (≤20 words)
- **Abstract:** Maximum 250 words; include problem, approach, key findings
- **Keywords:** 3–6 ACM Computing Classification System terms
- **Sections:** Introduction, Related Work, Methodology, Results, Conclusion (standard ACM structure)

### LaTeX Do's & Don'ts

#### ✅ DO
- Use `\cite{key}` with entries in `article.bib`
- Place figures/tables near first reference in text
- Use `\includegraphics[width=\linewidth]{fig.pdf}` for responsive sizing
- Keep custom commands minimal (rely on `acmart.cls` built-ins)

#### ❌ DON'T
- Add `\usepackage{geometry}` (margins controlled by acmart.cls)
- Define custom colors beyond what ACM supports
- Use unsupported packages (first check `acmart.cls` documentation)
- Import `etc/style.tex` from TFG22 (conflicts with acmart.cls)
- Create orphaned section references or undefined `\cite{}` keys

### When Making Changes
1. **Before modifying:** Consult **LaTeX ACM Compatibility** agent for preamble/package questions
2. **After adding sections:** Run `xelatex article.tex && biber article && xelatex article.tex`
3. **Before citations:** Ensure keys exist in `article.bib` (ask **Bibliography Validator** if unsure)
4. **Formatting issues:** Ask **Compatibility Checker** agent (likely simple ACM style fix)

### Checklist for Article Completion

- [ ] Title: concise, captures main contribution
- [ ] Abstract: 200–250 words, includes problem/approach/findings
- [ ] Intro: context + motivation + contribution + outline
- [ ] Related Work: comprehensive, categorized, positions against SOTA
- [ ] Methodology: hardware specs, experimental design, metrics clear
- [ ] Results: tables/figures with concise captions, key findings highlighted
- [ ] Conclusion: summary, limitations, future work
- [ ] Preamble: no custom styling, only ACM-compatible packages
- [ ] Bibliography: all entries validated, all citations resolved
- [ ] PDF: compiles without errors, 15–20 pages, readable at print size

---

## Related Resources

- **Main instructions:** [AGENTS.md](AGENTS.md)
- **Specialized agents:** See `.github/agents/` (project manager, content converter, validators)
- **ACM class docs:** [acmart-primary/README](acmart-primary/README)
- **Bibliography:** [article.bib](article.bib) — keep synchronized with `\cite{}` keys in article.tex
