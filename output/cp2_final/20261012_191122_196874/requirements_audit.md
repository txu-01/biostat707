# Checkpoint 2: consolidated notebook verification

Notebook: `checkpoint2.ipynb` (21 cells, 10 code cells). Scope: the supplied instructor screenshots, sections 2.1-2.7, plus the user's consolidation requirements. Unseen shared course requirements and submission-format instructions are not assumed.

## Changes identified before editing

The preceding finalized notebook already had one cleaned Ridge outer-CV workflow, one temperature/MAP cleaning pass, and one shared outer-fold list. The remaining consolidation opportunities were distributed data-integrity assertions, late creation of the spline feature subset, full-data diagnostic fits interleaved with outer evaluation, a redundant Top 25 coefficient figure, an unused paired-difference list, and scattered final table writes.

Retained: clinical cleaning rules and checks; complete predictor/drop inventories; all three models; training-fold preprocessing and nested tuning; benchmark missing-score policy; complete standardized coefficient plot; three spline effects with bootstrap bands; one five-method ROC figure; matched benchmark comparisons; final pipeline and OOF artifacts; serialization checks.

Removed or consolidated: distributed alignment/missingness assertions, the Top 25 coefficient figure, the unused difference accumulator, separately named search/fitted containers, early full-data diagnostic fits, separate output-writing blocks, and troubleshooting-history language. No uncleaned model or before-and-after experiment is trained.

## Consolidation requirements

| Requirement | Current implementation |
|---|---|
| One correctly cleaned Ridge workflow | Cell 10 evaluates Ridge once on the common cleaned X; no original/cleaned model pair |
| Temperature and MAP cleaning once, before features/models | Cell 4 contains the only cleaning rules and summary reconstruction |
| Build feature matrices once | Cell 6 builds X and X_spline; Ridge/forest reuse X; splines reuse the fixed subset |
| Define CV once, same outer folds | Cell 8 constructs one shared splits list and reusable inner CV |
| Consolidate integrity checks | Cell 8 checks IDs, headers, outcomes, schema, finite values, categories, count/missingness consistency, and fold membership before model fitting; the merge also retains its ingestion safeguard |
| Generate OOF once per model | Each model calls the shared evaluator once in cells 10, 12, 14 |
| Save OOF once | Cell 20 writes one aligned file containing all five prediction/score columns |
| Only final required figures | Exactly three PNG files: complete coefficients, three-panel spline effects, and five-method ROC |
| Separate outer evaluation from full-data fitting | All three outer evaluations finish before final model selection and full-data fitting in cell 16 |
| Avoid duplicate full-data fits | full_fit caches each result; selected Ridge is reused for its coefficient plot; spline is fitted once for required partial effects; forest is not refitted because it is not selected |
| Preserve scientific validity | Training-only preprocessing/tuning, full-data diagnostic fits, and stay-level bootstrap refits are retained and their purposes stated |

The extra spline full-data fit and 100 bootstrap refits are necessary for the instructor's partial-effect plots and uncertainty bands. They do not rerun outer CV or create another OOF vector. The selected final fit and Ridge diagnostic fit are the same cached object in this run.

## Instructor requirements

| Section | Status and evidence |
|---|---|
| 2.1 Modeling table | Meets: Outcomes-a.txt mortality joined one-to-one by RecordID; one row per stay checked; 4,000 stays, 554 deaths, 13.85%; cleaning decisions and revisions stated; multirow grouping/prediction conditions do not apply |
| 2.2 Predictors | Meets: every raw measurement is restricted to 0-48 hours; identifier, outcomes, survival/length of stay and benchmark scores excluded; ICUType/Gender categorical; all 263 raw predictors grouped with rationale and missingness; counts/indicators included; dropped columns listed; no sparsity-based exclusion threshold |
| 2.3 CV | Meets: five stratified outer folds, shared across all methods; three inner folds; seed 42; pipelines fit preprocessing and spline knots within training folds; all per-fold AUROCs, mean and sample SD reported; model-family selection optimism disclosed |
| 2.4 Regularized logistic | Meets: explicit pure L2 Ridge on all retained predictors, inner-CV C tuning and penalty rationale; complete 265-encoded-coefficient plot uses a common SD scale from the full-set-a refit; sparse-selection stability is not applicable to Ridge |
| 2.5 Nonlinear model | Meets: restricted cubic splines with explicit linear tails; 14 clinically chosen predictors; age/HR/temperature partial-effect plots, pointwise bootstrap bands and stated median references/log-odds scale; separate curve interpretations and clinical rationale; same outer folds |
| 2.6 Tree ensemble | Meets: random forest; 200 trees and depth/leaf/max_features search stated; tuning within training folds; imputation policy stated; same outer folds; no early stopping |
| 2.7 Comparison/final choice | Meets: one five-method table with each fold, mean/SD; SAPS-I/SOFA scores alone on shared fold assignments with missing -1 excluded and sample sizes disclosed; one OOF ROC figure; matched score-available comparisons and variation discussion; model-choice rationale; selected all-set-a refit with preprocessing saved alongside all OOF scores |

Calibration, decision curves, subgroups and SHAP are not added; the screenshots assign them to Checkpoint 3. Only set-a inputs are read.

## Verification results

- Fresh-kernel execution completed all 10 code cells with no notebook error.
- Structural checks found exactly three outer-evaluation calls, one per model, one spline-subset construction, one shared outer split definition, and one OOF export.
- Execution logs and metadata confirm one full-set-a Ridge fit and one full-set-a spline fit, with cached reuse. There is no forest full-data fit in this run.
- All saved OOF vectors and the complete comparison table agree with the preceding verified version within 1e-12 tolerance. Cleaning audit/checks, predictor inventory, coefficient table, spline effects/bands, and matched comparisons also agree.
- All 25 method-by-fold AUROCs were independently recalculated from saved OOF scores. Means and sample SDs agree.
- RecordID/outcome alignment was checked against Outcomes-a.txt; saved folds match StratifiedKFold(seed=42). Model/prediction reload checks passed.
- Exactly three final figure files were generated; the duplicate Top 25 plot is absent.

Final selection remains Ridge (mean fold AUROC 0.8461, SD 0.0244, full-data C=0.01). Random Forest remains 0.8485, spline logistic 0.7956, SAPS-I 0.6505, and SOFA 0.6226. Consolidation changed organization and removed redundancy without changing the scientific results.


## Additional AI-use reflection requirement

The opening Markdown cell and README now describe both advantages and disadvantages of AI assistance, using examples observed in this project. They disclose code generation/revision, benefits from consolidation and checks, a corrected AI-introduced string-formatting error, and the need to verify methodological and clinical assumptions. They do not claim that the student has already independently reviewed the revised analysis. This change updates explanatory text only; all executable code and model outputs remain unchanged.
