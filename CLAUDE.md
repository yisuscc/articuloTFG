# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LaTeX project to convert the thesis "Análisis y optimización de modelos de lenguaje en plataformas embebidas" (TFG, Universidad de Sevilla) into an English-language article for **ACM Transactions on Embedded Computing Systems (TECS)**. The research evaluates Small Language Models (1–4B params) on Raspberry Pi 5: quantization strategies, inference engines (llama.cpp vs Ollama), and the Hailo-10H accelerator.

**See [AGENTS.md](AGENTS.md) for the full conversion plan**: section-by-section mapping from thesis chapters to ACM structure, conversion pitfalls, and the step-by-step workflow. [.github/instructions/article.instructions.md](.github/instructions/article.instructions.md) has the editing rules and completion checklist for `article.tex`.

Project subagents in `.claude/agents/` (ported from the Copilot definitions in `.github/agents/`): `acm-article-planner` (phase planning/status), `tfg-content-converter` (section translation+conversion), `bibliography-validator` (bib migration), `latex-acm-compatibility` (build/PDF compliance). The planner returns a plan; delegation to the specialists happens from the main session.

## Build Commands

Everything compiles with **XeLaTeX + Biber** (not pdflatex/bibtex).

```bash
# Compile the thesis (source material)
cd TFG22 && latexmk -xelatex TFG.tex

# Compile the converted article (once it exists, at repo root)
latexmk -xelatex article.tex
# or manually: xelatex article.tex && biber article && xelatex article.tex

# Debugging
grep -i "error" article.log | head -20
texcount article.tex                      # word counts (abstract ≤250 words)
biber --validate_datamodel article.bcf    # check .bib entries against ACM datamodel
```

`TFG22/.latexmkrc` sets `$pdf_mode = 5` (XeLaTeX). XeLaTeX is required for Unicode (Spanish names/metadata in the bibliography).

## Layout

- `TFG22/` — the complete thesis (read-only source material; do not modify)
  - `TFG.tex` orchestrates `sections/00_*` (front matter, Spanish) through `sections/05_Conclusiones.tex`; results subsections live in `sections/SubResultados/` (E0–e5, sintesis), appendices in `sections/anexos/`
  - `etc/pkgs.tex` and `etc/style.tex` — thesis-only preamble; **never import into the ACM article** (conflicts with acmart.cls)
  - `TFG-yisuscc.bib` — BibLaTeX bibliography to migrate into `article.bib`
  - `figures/` and `tables/` — reusable assets (results are under `04_Resultados/` subdirs)
- `acmart-primary/` — pristine ACM template distribution; `acmart.cls` is the document class, `samples/` has starting-point examples (e.g. `acmsmall-biblatex.tex` for the BibLaTeX+Biber route)
- Output files (`article.tex`, `article.bib`, `article.pdf`) go at the repo root

## Key Constraints

- Article is **English only**; the thesis is in Spanish, so converting means translating and condensing, not copying
- `acmart.cls` controls margins, fonts, and colors — do not add `geometry`, custom colors, or fontspec hacks
- TECS target: ~15–20 pages, abstract ≤250 words, figures sized with `\includegraphics[width=\linewidth]`
- This directory is **not a git repository** — there is no history to consult and nothing to commit unless the user initializes one
