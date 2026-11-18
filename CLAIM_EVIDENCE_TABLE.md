# Claim–Evidence Table

|ID|Claim (read with report assumptions)|Theory / code|Measured evidence under results/tables|Figure under results/figures|
|---|---|---|---|---|
|C01|Exact translation and continuous invariants|report/theory.tex eq exact; src/exact_solution.py|joint_convergence.csv; diagnostic_history.csv|profiles; mass_tv|
|C02|Upwind conservative first-order dissipative update|src/upwind.py; modified equation in report|spatial_separated.csv; fourier_modes.csv|separated_convergence; modal_fidelity|
|C03|LW smooth joint order two but fixed-grid limiting time order one|src/lax_wendroff.py; B(dt) derivation|joint_convergence.csv; temporal_separated.csv|joint_convergence; separated_convergence|
|C04|Linear CFL sharp bound under periodic uniform constant-coefficient setting|Fourier factors and Parseval derivation|stability_summary.csv; stability_history.csv|amplification; stability_growth|
|C05|MC TVD for stated flux and 0<=C<=1|src/tvd.py; effective-coefficient proof|diagnostic_history.csv; validation.csv|mass_tv|
|C06|Square Linf need not decay while L1 converges|half-open point reference; front-width reasoning|square_diagnostics.csv|joint_convergence; profiles|
|C07|MC smooth global L2 rate can be below two|limiter extrema mechanism|spatial_separated.csv; oracle checks|separated_convergence|
|C08|Conservation cannot establish accuracy|flux telescoping; contrasting profiles|diagnostic_history.csv; joint_convergence.csv|mass_tv; profiles|
|C09|Modal amplitude and phase are distinct|log G and unwrapped coefficient|fourier_modes.csv; harmonic_L2 and phase_reliable fields|modal_fidelity|
|C10|Long-time defects accumulate|per-step phase unwrap|long_time.csv|long_time|
|C11|Efficiency ranking is conditional on datum and target|same-target search; measured timing procedure|cost_accuracy.csv; matched_targets.csv; timing_samples.csv|cost_accuracy|
|C12|Results have independent implementation checks|analytic tests and scalar index-loop implementation|validation.csv; pytest.log|VALIDATION_REPORT.md|
