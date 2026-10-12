# BIOS 707: ICU mortality modeling

Checkpoint 2 predicts in-hospital mortality using information recorded during the first 48 hours of ICU admission in PhysioNet Challenge 2012 set-a. The final analysis is in `checkpoint2.ipynb`, organized around instructor sections 2.1–2.7. Each row is one ICU stay. Set-b and set-c are reserved for Checkpoint 3 and are never read by this workflow.

## Inputs and environment

Required local files are `Data/set-a/*.txt`, `Data/Outcomes-a.txt`, and the Checkpoint 1 starting table `output/set-a_wide.csv`. Data are not bundled with the submission. The notebook verifies patient IDs and reconstructs the wide-table summaries from raw set-a measurements to enforce the time window and cleaning rules. It does not depend on variables from an earlier interactive session.

Use the existing locked Pixi environment:

```powershell
pixi install --locked
pixi run --locked python scripts/run_checkpoint2.py
```

The runner starts a fresh Jupyter kernel, executes the notebook from top to bottom, and saves executed outputs in `checkpoint2.ipynb`. It also prepares the native DLL search path when invoked directly on Windows. If the Pixi CLI cannot determine its home directory in a managed shell, use the already-installed environment:

```powershell
.\.pixi\envs\default\python.exe scripts/run_checkpoint2.py
```

For interactive work, use `pixi run --locked lab` and open the final notebook. Keep `scripts/cp2_support.py` with the notebook: it implements the training-fold restricted cubic spline transformer. No dependency or lockfile changes were made during finalization.

## Methods and cleaning

- One row per ICU stay; outcome joined by RecordID with one-to-one validation.
- Measurements restricted to 0–48 hours and ordered chronologically. Checkpoint 1 demographic `-1` codes and 100–250 cm height cleaning are retained; zero height/weight is revised to missing. Existing provisional temperature 25–45 C and MAP >=30 mmHg rules are retained.
- One common cleaned feature table has 263 raw predictors, including measurement counts/indicators. Age, Gender, Height, and ICUType retain their first value only. Gender and ICUType are categorical in both full-feature models. No sparse laboratory variable is excluded using a missingness threshold.
- Five fixed stratified outer folds and three stratified inner folds, both seed 42. All imputation, scaling, encoding, and knot placement occur inside training-fold pipelines.
- Ridge logistic regression: C in {0.01, 0.1, 1, 10, 100}.
- Restricted cubic spline logistic regression: 14 clinically chosen predictors; age, mean HR, and mean temperature use natural cubic bases with explicit linear tails. Four training-fold quantile knots and the same C grid are used. Partial effects have 100-refit, pointwise bootstrap bands conditional on the selected C.
- Random forest: 200 trees; max_depth in {10,20}, min_samples_leaf in {2,5}, max_features='sqrt'. Missing values are imputed inside the pipeline; early stopping is not used.
- SAPS-I and SOFA are risk scores alone. Their `-1` codes are missing; observed scores are evaluated within the same outer folds. Matched model-versus-score comparisons use the same score-available patients.

## Results

The cohort contains 4,000 stays and 554 deaths (13.85%). Mean outer-fold AUROC and sample SD are reported below; these are not pooled OOF AUROCs.

| Method | Mean fold AUROC | SD | Evaluated stays |
|---|---:|---:|---:|
| Ridge logistic | 0.8461 | 0.0244 | 4,000 |
| Restricted cubic spline logistic | 0.7956 | 0.0145 | 4,000 |
| Random forest | 0.8485 | 0.0215 | 4,000 |
| SAPS-I | 0.6505 | 0.0317 | 3,810 |
| SOFA | 0.6226 | 0.0435 | 3,856 |

Ridge is selected for simplicity and interpretability because its mean AUROC is within the stated 0.01 preference margin of the best model. This margin is a practical selection criterion, not a statistical equivalence test. Its final full-set-a tuning selects C=0.01. Missing-score benchmark evaluations use different subsets; consult the matched comparisons before interpreting performance differences. Pooled benchmark AUROCs are 0.6498 for SAPS-I and 0.6228 for SOFA.

The final notebook completed a fresh-kernel run successfully. The verified run is `output/cp2_final/20261012_191122_196874/`, with `execution_complete.json` and independently checked `final_verification.json`. Its HTML report is `checkpoint2.html` in that directory. `requirements_audit.md` records the item-by-item check against the supplied instructor screenshots, including the supplemented full coefficient figure. Each execution creates a new run directory; it never overwrites old model artifacts. Use a directory with a completion marker, rather than an incomplete development run.

## Outputs and submission

The notebook contains the comparison table, required plots, predictor inventory, cleaning decisions, curve interpretations, and limitations. Each run also saves:

- `cp2_final_model.joblib`: selected fitted pipeline, including preprocessing.
- `cp2_oof_predictions.csv`: RecordID, outcome, outer fold, three model probabilities, and both benchmark scores. Missing benchmark scores remain blank.
- `model_comparison.csv` and `fold_results.csv`: all five fold AUROCs, mean/SD, benchmark evaluation counts, and selected fold configurations.
- `roc_comparison.png`, `ridge_coefficients_all.png`, and `spline_partial_effects.png`: the three final figures. The full coefficient plot includes all encoded predictors on a common SD scale. The redundant Top 25 coefficient figure is no longer generated.
- `predictor_inventory.csv`, `dropped_predictors.csv`, `ridge_coefficients.csv`, `spline_partial_effects.csv`, and `matched_benchmark_comparison.csv`: complete supporting tables.
- `cleaning_audit.csv`, `cleaning_checks.csv`, `model_metadata.json`, and `selection_summary.txt`: cleaning evidence and Checkpoint 3 handoff information.

Proposed submission: `checkpoint2.ipynb`, `README.md`, `scripts/cp2_support.py`, `scripts/run_checkpoint2.py`, and the completed run's final model, OOF file, comparison table, required plots, and metadata. An HTML export is provided for reading the report if that format is accepted. The screenshots do not specify an exact submission format; these are proposed files, not an invented course requirement. Do not include the raw data, `.pixi/`, original exploratory notebooks, failed run directories, or archived backups unless requested.

For Checkpoint 3, the saved model expects the cleaned feature schema in metadata, not raw records. Apply identical measurement cleaning and feature construction. Only load joblib files from trusted sources.

## Changes, validation, and limitations

The original Checkpoint 2 notebook's 82 cells were consolidated into a coherent 21-cell analysis with 10 code cells. The redundant `checkpoint2_clean.ipynb` had identical source cells and was removed after comparison. Redundant imports, repeated CV fits, exploratory single-patient dumps, stale plots, object searches, and incremental correction/saving blocks were consolidated. Required models, nested CV, temperature/MAP checks, coefficients, bootstrap effects, ROC curves, benchmarks, and final artifact saving are retained.

Temperature and MAP cleaning run once before feature construction. The full feature table and the 14-predictor spline subset are built once. Data-integrity, outcome/ID alignment, missingness consistency, and fold-membership assertions are collected in one pre-model validation section. A shared evaluator generates one OOF vector per model using the same fixed outer folds. Model comparison precedes full-data fitting. Full-set-a fits are cached: the chosen final model and the Ridge/spline fits needed for required diagnostic plots reuse the same fitted objects. Bootstrap refits are retained because they estimate uncertainty. Final tables and the single OOF file are saved together, followed by serialization checks that do not repeat data cleaning or CV.

Corrected issues include undefined `modeling_df`, cleaning MAP after some model fits, categorical ICUType summaries, zero-weight handling, default B-splines that did not establish restricted cubic spline behavior, missing-score benchmark inconsistencies, and comparisons mixing pooled benchmark AUROC with mean fold model AUROC. RecordID checks, OOF coverage, CSV round-trip verification, and serialized-model reload checks are built into the final notebook.

Differences from historical performance are expected because baseline summaries, zero weights, categorical encoding, forest imputation indicators, and spline basis construction were corrected. No isolated experiment establishes which change caused a particular AUROC difference. Cleaning assumptions may discard true extremes, monitoring features can encode local practice, benchmark availability can be selective, bootstrap bands omit tuning uncertainty, and model-family selection can be optimistic. Independent external performance has not been evaluated. Calibration, decision curves, subgroup analysis, and SHAP belong to Checkpoint 3.

### AI-use reflection

ChatGPT/Codex assisted with code generation and revision, workflow organization, debugging, methodological checks, and execution verification. The opening Markdown cell of `checkpoint2.ipynb` contains the full reflection on advantages and disadvantages.

AI helped consolidate repeated analysis and automate reproducibility checks, while identifying inconsistent cleaning, an undefined saving variable, and potentially misleading AUROC comparisons. Its limitations were also evident: an early AI-assisted revision introduced a string-formatting error, and seemingly plausible spline implementations still required checking against the instructor's restricted cubic spline requirement. Generated code needed fresh-kernel execution and checks against source data and documentation. AI assistance did not independently validate clinical thresholds or establish statistical significance. The submission author remains responsible for reviewing the final code, assumptions, and interpretation.

Original Checkpoint 1 is preserved. The finalized notebook now uses the main filename `checkpoint2.ipynb`; the original exploratory notebook is backed up at `archive/checkpoint2_original.ipynb`. The original README is backed up at `archive/README_checkpoint1_original.md`. Cleanup removed the duplicate notebook, obsolete Checkpoint 2 model/prediction/figure files, two incomplete runs, the refactoring prompt, the notebook generator, and temporary caches. The output directory retains only the latest completed Checkpoint 2 run and all Checkpoint 1 inputs and outputs. Superseded Checkpoint 2 runs and old root-level model/figure files were removed; source backups are kept separately in archive/. Checkpoint 1 still runs with `pixi run --locked checkpoint1`, producing `output/checkpoint1.html` and its original tables.
