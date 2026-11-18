# Project 3: periodic advection research

Group C: Chuqiao Tang (2360692), Jinyu Ma (2363433), Muqing Xu (2362900), Shuoran Fu (2362626), Taiqi Zhang (2363684), Yujia Ding (2362094).


## Quick start
Use Python 3.12 or newer (tested interpreter and versions are recorded in results/raw/environment.json).

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
python run_all.py
python build_documents.py
```

`python run_all.py` regenerates all eight experiment families, CSV tables, saved profiles, PDF/PNG figures and VALIDATION_REPORT.md. It prints progress and fails if any declared validation fails. The nonlinear oracle computation can take several minutes. Repeated timing numbers will change with system load; numerical outputs should agree within recorded tolerances. `python build_documents.py` reads the current CSVs and regenerates numerical report tables, prose values, Beamer slides, speaking script and three compiled PDFs; requires pdflatex and bibtex (TeX Live/MacTeX). No network access is used by numerical reproduction. An equivalent `python3` command works if that is your interpreter name. Use `python clean_reproduce.py` for isolated-directory same-interpreter reproduction and numerical CSV comparison. The official independent teammate/machine check is still pending.

## Entry points and evidence
- report/report.pdf, report/report.tex, report/theory.tex, report/results_generated.tex and bibliography.bib: English reference report and editable sources.
- presentation/presentation.pdf and .tex: 17-slide English Beamer presentation, provisionally 15–18 minutes. SPEAKER_SCRIPT.md maps speech to each slide.
- docs/PROBLEM_DEFINITION_SHEET.pdf and .tex: one-page official eight-item form. Peer fields intentionally blank.
- src/: grid, data, exact solution, three methods (MC primary; Minmod sensitivity), diagnostics and validated production driver.
- experiments/study.py: experiment settings read from config/protocol.json; explicit high-CFL stress loop; DOP853 and FFT/expm references; data and plot generation.
- tests/: independent analytic and hand-update tests. experiments/validate.py additionally uses scalar-index loops and mathematical invariants.
- results/tables/: all measured diagnostics in CSV, including timing samples and actual final-time/CFL metadata.
- results/raw/: environment JSON, logs, saved profile NPZ, reproduction receipts.
- docs/source_text/: extracted course handouts; OFFICIAL_SOURCE_MANIFEST.json includes source hashes. Books and inspiring papers are a reference library, not required production inputs.
- REQUIREMENTS_CHECKLIST.md, EXPERIMENT_PROTOCOL.md, VALIDATION_REPORT.md, AI_CLAIM_AUDIT.md, CLAIM_EVIDENCE_TABLE.md, VIVA_PREPARATION.md, docs/ROLES_AND_ICS_TEMPLATE.md, FINAL_REVIEW.md: scope and audit records.

## Mathematical and data conventions
All variables dimensionless, a=1 baseline; point values x_j=j/N with periodic modulo indices and no duplicate endpoint. Square datum is one on [0.25,0.5), including the rising endpoint and excluding the falling endpoint. Exact references evaluate the same shifted point convention. Uniform dt is reset to T/ceil(T*N/C_requested); actual C is saved. Production C must be in (0,1]. Negative speed is implemented and unit-tested by reflection but is not a principal sweep. Low-level step functions deliberately do not contain a CFL guard: only the named stress experiment calls them outside the production bounds, with an amplitude/step cap.

Separated spatial studies use exact-in-time limiting spatial operators; separated temporal studies compare fixed-grid finite steps with their small-step limits. Classical LW is generally first-order in dt relative to that fixed-grid reference. Joint fixed-CFL PDE convergence is separately labelled. MC uses a numerical limiting-ODE reference, with tolerance-difference checks; these are not certified analytic bounds.

## Submission status
The local pack lacks the shared full rubric, official LaTeX template, official presentation duration and current module-homepage checklist. Tutorial13 gives a report length of at least eight pages. Brief says Monday Week15 23:59, lecture5 says Week14: Brief takes precedence here, but check the live course calendar. Actual repository invitations, commit history, milestone posts and completed ICS are not supplied or fabricated. Do not submit blank ICS as completed statements. No files in other projects or official source files were modified.

