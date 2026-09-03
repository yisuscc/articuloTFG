# AI Agent Instructions: TFG-to-ACM Article Conversion

## Project Overview

**Goal:** Convert thesis "Análisis y optimización de modelos de lenguaje en plataformas embebidas" (Analysis and Optimization of Language Models on Embedded Platforms) into a publishable article for **ACM Transactions on Embedded Computing Systems**.

**Current State:**
- Complete thesis (TFG22/) with 5 main chapters + 3 appendices
- ACM template available (acmart-primary/)
- XeLaTeX + Biber build system

**Key Research:** Evaluation of Small Language Models (1-4B parameters) on Raspberry Pi 5, comparing quantization strategies (4-bit optimal), inference engines (llama.cpp > Ollama), and hardware accelerators (Hailo-10H). Active cooling required.

---

## Build & Compilation

### Thesis Compilation (Current)
```bash
cd TFG22
latexmk -xelatex TFG.tex
# Or: xelatex TFG.tex && biber TFG && xelatex TFG.tex
```

### ACM Article Compilation (Target)
```bash
# Once converted to acmart.cls format
xelatex article.tex && biber article && xelatex article.tex
# Alternative: latexmk -xelatex article.tex
```

**Critical Settings:**
- Engine: XeLaTeX (Unicode support for author metadata, special chars)
- Bibliography backend: Biber (modern, required for BibLaTeX)
- Bibliography style: ACM numeric or author-year (configured in `acmart.cls`)

---

## Document Structure & Conversion Tasks

### Current Thesis Structure → Target ACM Format

| Current (TFG22/) | Target ACM Format | Notes |
|---|---|---|
| `00_portada.tex` | Remove/skip | Not used in journal format |
| `00_resumen.tex` (Spanish) | Remove or Appendix | ACM format uses English only |
| `00_abstract.tex` (English) | Keep as Abstract | Adapt to ~250 words max |
| `01_Introduccion.tex` | **Introduction** | Merge with motivation, state context concisely |
| `02_EstadoDelArte.tex` | **Related Work** | Extensive (1-2 pages typical for ACM) |
| `03_Metodologia.tex` | **Methodology & Experimental Setup** | Include hardware spec, quantization params, inference config |
| `04_Resultados.tex` | **Results & Discussion** | Separate results from interpretation |
| `05_Conclusiones.tex` | **Conclusion & Future Work** | Emphasize novelty and impact |
| `anexos/*` | **Appendices** (optional) | Include if space permits; reference in main text |

### Key Sections to Adapt

1. **Abstract** (250 words max for ACM)
   - Current: Check `00_abstract.tex`
   - Revise: Emphasize performance gains, practical impact on embedded systems
   - Include: Key metrics (throughput, latency, energy efficiency)

2. **Introduction**
   - Set context: Why embedded LLMs matter (edge deployment, privacy, latency)
   - Hook: Quantization + inference engine evaluation as novel contribution
   - Structure: Problem → Motivation → Contribution → Outline

3. **Related Work** (Major rewrite)
   - Compare to existing SLM optimization work
   - Separate categories: Quantization techniques, inference engines, hardware accelerators
   - Position your work relative to competitors (TensorRT, TVM, etc.)

4. **Methodology**
   - Hardware: Raspberry Pi 5 specs, Hailo-10H specs
   - Model selection: Which SLMs tested? (e.g., Mistral, TinyLlama, Phi)
   - Experimental variables: Quantization bits (4, 8, etc.), context windows, batch sizes
   - Tools: llama.cpp, Ollama versions
   - Metrics: Inference latency, throughput, memory usage, energy (if measured)

5. **Results**
   - Table 1: Model × Quantization × Engine performance matrix (from `figures/04_Resultados/`)
   - Graphs: Latency vs accuracy tradeoffs
   - Finding: Active cooling essential (critical practical insight)
   - Finding: 4-bit quantization optimal (cost-benefit)

6. **Discussion/Conclusion**
   - Real-world implications (edge AI deployment)
   - Limitations (only Raspberry Pi 5 tested, limited model variety)
   - Future work: Multi-device evaluation, energy profiling, integration patterns

---

## Key Files & Conventions

### Thesis Files (Reference/Source)
- `TFG22/TFG.tex` — Main document orchestrator
- `TFG22/etc/pkgs.tex` — LaTeX packages (DO NOT copy to ACM format; use `acmart.cls` built-ins)
- `TFG22/etc/style.tex` — Custom styling (may conflict with `acmart.cls`; merge carefully)
- `TFG22/TFG-yisuscc.bib` — Bibliography in BibLaTeX format
- `TFG22/figures/04_Resultados/` — Raw data visualizations (tables, graphs)
- `TFG22/tables/04_Resultados/` — Detailed result tables

### ACM Template (Target)
- `acmart-primary/acmart.cls` — ACM article class (use as document class)
- `acmart-primary/samples/sigconf.tex` — Example: conference proceedings (closest to journal format)
- `acmart-primary/samples/acmsmall.tex` — Example: smaller journal format
- ACM Reference Format (`.bst`, `.bbx/.cbx` in `acmart-primary/`)

### Output Files to Create
- `article.tex` (or rename from TFG.tex) — Main converted article
- `article.bib` — Cleaned/validated bibliography
- `article.pdf` — Compiled output

---

## Common Conversion Pitfalls

### ⚠️ LaTeX Compatibility
- `acmart.cls` **does NOT support** arbitrary custom styling from `style.tex`
- Remove: Custom color definitions, page geometry commands (acmart enforces ACM margins)
- Simplify fonts: ACM uses standard fonts; drop fontspec hacks if present
- Fix: `\DeclareFieldFormat{urldate}{}` (already in TFG.tex; keep for BibLaTeX)

### ⚠️ Bibliography Handling
- Ensure all BibTeX entries match `acmdatamodel.dbx` schema
- Use proper entry types: `@article`, `@inproceedings`, `@misc`, etc.
- Validate URLs and DOI fields
- BibLaTeX `\printbibliography` works with acmart; ensure Biber backend

### ⚠️ Figures & Tables
- ACM limits figure size; check page width constraints
- Use `\includegraphics[width=\linewidth]` for responsive sizing
- Place figures near first reference per ACM style
- Captions: Short (one line) above tables, below figures

### ⚠️ Code Listings
- If showcasing code: Use `listings` package with ACM-compatible styling
- Current code examples (`code/html_example.html`, etc.) appear minimal; verify if needed for article

---

## Agent Workflow: Step-by-Step

1. **Review & Extract Content**
   - Read `TFG22/00_abstract.tex` → adapt to 250-word ACM abstract
   - Identify key results from `figures/04_Resultados/` and `tables/04_Resultados/`

2. **Create Article Skeleton**
   - Copy `acmart-primary/samples/sigconf.tex` → `article.tex`
   - Adapt template preamble: title, author, affiliation, keywords

3. **Port Content Sections** (in priority order)
   - Introduction (from `01_Introduccion.tex`)
   - Related Work (from `02_EstadoDelArte.tex` + research)
   - Methodology (from `03_Metodologia.tex` + hardware specs)
   - Results (from `04_Resultados.tex` + figures)
   - Conclusion (from `05_Conclusiones.tex`)

4. **Validate Bibliography**
   - Migrate entries from `TFG-yisuscc.bib` to `article.bib`
   - Ensure Biber compatibility
   - Test compile with Biber backend

5. **Test & Iterate**
   - Compile: `xelatex article.tex && biber article && xelatex article.tex`
   - Fix layout issues (ACM enforces strict margins/spacing)
   - Review PDF against [ACM article guidelines](https://www.acm.org/publications/authors)

---

## Commands for Agents

### Common Build/Test Tasks
```bash
# Test compilation
cd /home/yisus/Documentos/git/conversion-tfg-paper
xelatex article.tex && biber article && xelatex article.tex

# View errors
grep -i "error" article.log | head -20

# Count words (for abstract/section length checks)
texcount article.tex

# Validate BibTeX entries
biber --validate_datamodel article.bcf
```

### File Operations
- **Create**: Use `article.tex`, `article.bib` as output files (preserve originals in TFG22/)
- **Edit**: Minimal custom styling; rely on `acmart.cls` formatting
- **Copy**: Figures/tables from TFG22/figures/ and TFG22/tables/ to article directory

---

## References & Resources

- **ACM Template Docs:** [acmart-primary/README](acmart-primary/README)
- **ACM Transactions on Embedded Computing Systems:** https://dl.acm.org/journal/tecs (review scope, article length ~15-20 pages)
- **BibLaTeX Handbook:** https://ctan.org/pkg/biblatex
- **Thesis Content:** [TFG22/](TFG22/) (comprehensive source material)

---

## Specialized Agents for Conversion

Dedicated agents have been created to handle specific conversion tasks. Use these agents for focused work:

### 1. **ACM Article Project Manager** (`.github/agents/acm-article-project-manager.agent.md`)
   - **Role:** Orchestrate full conversion workflow
   - **Use when:** Planning conversion phases, coordinating between agents, tracking milestones
   - **Handles:** Phase breakdown, dependency mapping, compilation gating, final review

### 2. **TFG Content Converter** (`.github/agents/tfg-content-converter.agent.md`)
   - **Role:** Convert thesis sections to ACM format
   - **Use when:** Converting Introduction, Related Work, Methodology, Results, Conclusion
   - **Handles:** Section adaptation, abstract reduction, citation formatting, ACM style enforcement

### 3. **Bibliography Validator** (`.github/agents/bibliography-validator.agent.md`)
   - **Role:** Validate and migrate bibliography
   - **Use when:** Migrating entries from TFG-yisuscc.bib, ensuring ACM datamodel compliance
   - **Handles:** Entry validation, schema checking, Biber testing, citation consistency

### 4. **LaTeX ACM Compatibility** (`.github/agents/latex-acm-compatibility.agent.md`)
   - **Role:** Ensure LaTeX compatibility and PDF validation
   - **Use when:** Checking preamble conflicts, testing compilation, validating output
   - **Handles:** Preamble audit, error diagnosis, PDF validation, TECS format verification

---

## Suggested Workflow

1. **Start:** Invoke **Project Manager** → asks for clarifications, creates article skeleton
2. **Convert sections:** **Project Manager** → delegates to **Content Converter** for each section
3. **Handle references:** **Project Manager** → delegates to **Bibliography Validator**
4. **Validate output:** **Project Manager** → delegates to **Compatibility Checker** for final build
5. **Submit:** **Project Manager** → reports completion and generates final checklist

---

## Questions for Clarification

When working on conversion, ask the agent:
1. **Scope:** Should appendices be included in final submission (space constraints)?
2. **Code samples:** Are current code examples (`code/html_example.html`, etc.) essential for the article, or can they be removed?
3. **Results focus:** Emphasize performance metrics (latency/throughput) or energy efficiency?
4. **Author affiliations:** What organization/institution should appear in author metadata?
