# Group 4 · End-to-End MLflow Capstone

> **Historical research log.** Read [CLAUDE.md](CLAUDE.md) first for current instructions. This file preserves the detailed earlier investigation, decisions, and execution history; it is not the current task checklist.
>
> **Current position (22 October 2026):** GitHub publishing, Docker Hub releases, Render Free API deployment, and automatic main-branch deployment are complete and verified. Read [CLAUDE.md](CLAUDE.md) for the authoritative current handoff, remaining tasks, and local/remote Git discrepancy. Dated sections below preserve earlier research and may describe superseded pending work.

**Current-status header updated:** 22 October 2026; historical research below dates from 5 October 2026 · **Course:** Elective II: Machine Learning Operations (MLOps)  
**Assignment:** Project 4 — Capstone: End-to-End MLflow Pipeline from Raw Data to Monitored Deployment  
**Brief prepared by:** Dr. Santosh Kumar

**Status legend:** 🟢 Complete / verified · 🟡 Pending / proposed · 🔴 Blocked / failed  
Color symbols always have accompanying words so the document remains understandable in plain text.

## 1. Team, intent, and working agreement

| Member | Roll number | GitHub |
|---|---|---|
| Swagata Bhowmik | B053 | https://github.com/Swagata-Bhowmik |
| Sumit Kothari | B062 | https://github.com/sum1tk |

The user wants one complete, coherent project, with implementation organized by dependency and phase. Do not split engineering responsibilities between the two students by default. The intended repository owner is **Swagata-Bhowmik**; the repository is public at https://github.com/Swagata-Bhowmik/group4-mlflow-capstone.

The user starts without having read the assignment and wants clear, beginner-friendly explanations. Explain what each step accomplishes, what the user needs to do, and whether anything must be downloaded. Keep conversational updates concise to manage token use; preserve detailed context here.

**Current authorization:** The user authorized routine implementation, GitHub writes using the team credential, Docker Hub publishing, free Render hosting, and automatic deployment. Earlier Git deferral and per-step permission requests are superseded. Never fabricate contributions or expose secrets; respect active environment permissions. Current hosting is free with no payment card.

The user values thoughtful investigation, visual clarity, restrained color, and a distinctive result. Distinction should come from demonstrated engineering quality and clear explanations, supported by attractive presentation.

### Academic requirements that affect the plan

The assignment requires both students to have genuine commits; individual contributions are checked. Both must be able to explain, justify, and modify every part live without reading notes they did not write themselves. Assistant support must be accompanied by student understanding and actual participation; do not fabricate authorship or contribution history.

Do not copy another group's repository, code, configuration, dashboard, or report. Substantially similar submissions may both be investigated. Reusing a previous year's submission, public repository, or another course's project as a starting point requires explicit citation and a clear separation of original contributions. The brief does not provide an explicit AI-use policy; do not invent one.

## 2. Source record and limits of current knowledge

| Source | What is known | Inspection status |
|---|---|---|
| `Capstone End_to_End_Pipeline.docx` | Authoritative professor's brief | 🟢 Complete text read, including all tasks, constraints, and rubric; document layout was not reviewed |
| `capstone_house_prices_train.csv` | Supplied historical training data | 🟢 Fully parsed: 4,000 rows, 11 columns; initial quality and distribution analysis completed |
| `capstone_incoming_batches.csv` | Supplied incoming data | 🟢 Fully parsed: 1,500 rows, 12 columns; batches 1–3 have 500 rows each; initial quality and distribution analysis completed |
| Swagata's GitHub profile | Profile page accessible during initial inspection | 🟢 Public profile read; no repository selected or account access verified |
| Sumit's GitHub profile | User supplied the URL | 🟡 Browser retrieval failed with a cache-miss error; this does not establish that the profile is invalid |

Full CSV parsing confirms the brief's row/column counts and batch sizes. Missingness, duplicates, basic ranges, categories, distribution differences, and initial historical validation metrics have been investigated; findings appear in Section 4. Final test accuracy, incoming-batch performance drift, and production alert outcomes remain unmeasured. This initial audit does not establish that every possible data-quality issue has been ruled out.

Workspace at creation: `/Users/krishsoni/Documents/swagata/ml-ops`. The three source files were already present. No downloads were necessary to read the brief. The initial directory listing contained no `.git` directory or implementation files. Local tools have now been inspected as recorded below. Authentication and deployment resources remain unchecked.

This document distinguishes **assignment requirements**, **observed facts**, and **proposals**. The original brief remains authoritative if a discrepancy is discovered. Record corrections here rather than silently treating a proposal as a requirement.

## 3. The problem in plain language

A real-estate analytics startup predicts property **asking prices in ₹ lakhs**. Listings arrive in batches. Its current retraining and release process is manual, and it cannot reliably identify which data and code produced a model.

We must build one automated system that accepts data, prepares features, trains and evaluates a candidate model, registers an acceptable model, deploys it, and monitors it. We act as lead MLOps engineers presenting the system to the startup's founders.

**Central safety requirement:** If the data or candidate model fails a gate, stop the attempted update with an explanatory message while the previous production model and endpoint continue serving unchanged.

### Vocabulary

- **Pipeline:** Connected automated stages that turn input data into a monitored deployment.
- **Features:** Property attributes used to predict the price.
- **Experiment tracking:** A record of parameters, metrics, artifacts, and conditions for each run.
- **Registry:** A versioned catalog of models and their lifecycle transitions.
- **Production model:** The model currently answering API prediction requests.
- **Gate:** A configurable condition that must pass before an update proceeds.
- **Lineage:** The chain from a deployed model back to its run, configuration, data version, and code version.
- **CI/CD:** Automated checks and release actions triggered by repository changes.
- **Data drift:** A change in the distribution of incoming inputs.
- **Performance drift:** A change in prediction quality, measurable here because incoming batches include actual prices.
- **Rollback:** Returning to a previous working release using a documented, tested procedure.

## 4. Supplied data and handling rules

| File | Rows stated in brief | Columns | Intended use |
|---|---:|---:|---|
| `capstone_house_prices_train.csv` | 4,000 | 11 | Train and validate the first model |
| `capstone_incoming_batches.csv` | 1,500 | 12 | Simulate three later batches: `Batch` 1, 2, and 3, each with 500 listings |

### Full data dictionary

| Column | Declared type | Meaning / role |
|---|---|---|
| `House_ID` | String | Unique listing identifier; exclude from predictive features |
| `Batch` | Integer | Incoming file only; batch identifier; exclude from predictive features |
| `Area_sqft` | Integer | Built-up area in square feet |
| `Bedrooms` | Integer | Number of bedrooms |
| `Bathrooms` | Integer | Number of bathrooms |
| `Age_Years` | Integer | Property age in years; missing values expected |
| `Distance_to_Center_km` | Float | Distance to city centre; missing values expected |
| `Neighborhood_Score` | Float | Neighborhood quality from 1 to 10; missing values expected |
| `Has_Parking` | Integer, 0 or 1 | Whether parking is available |
| `Property_Condition` | Category | Poor, Fair, Good, Excellent |
| `City_Zone` | Category | North, South, East, West, Central |
| `Price_Lakhs` | Float | Target: asking price in ₹ lakhs |

The first records serialize some integer-valued ages as decimals, for example `32.0`. The future schema must account for actual CSV representation and permitted missingness; declared types are not proof of inferred parser types.

**Required constraints:**

- Preserve and use the supplied datasets. Do not generate or replace them unless a task explicitly permits it.
- Substitution with data from Project 1 or Project 2 requires the instructor's written approval.
- Do not assume incoming batches resemble historical data; investigate this during monitoring.
- Handle the expected missing values rather than rejecting every incomplete listing.
- Keep identifiers and the target out of predictive input features.

**Proposed methodological safeguards, not yet implemented:** Split historical data before fitting preprocessing; fit imputers and encoders only on training partitions. Keep a held-out evaluation set. Compare candidate and production models on the same evaluation data. Define how incoming labeled data can enter future retraining without contaminating monitoring or evaluation. Preserve the original CSV files when constructing isolated failure demonstrations, and document any derived test inputs.

### Dataset investigation · 4 October 2026 · completed

**Method:** Read both complete CSVs with pandas 2.3.3 using the existing Python 3.12 environment. Calculate group-level counts, missingness, duplicates, numeric summaries, category proportions, and distribution differences against all 4,000 historical rows. Use observed non-missing values for numeric summaries and distribution comparisons. This is exploratory data analysis, not a trained-model evaluation or a configured production monitoring run. No imputation, cleaning, deletion, or source-file rewriting was performed.

#### Structural quality

- Confirmed 4,000 historical rows and 1,500 incoming rows, with exactly 500 in each of batches 1, 2, and 3.
- Zero duplicate complete rows or duplicate `House_ID` values within either file; zero ID overlap between files.
- Across all 5,500 records, no duplicate vectors of the nine predictive features, and no duplicate records after excluding identifiers.
- No missing targets, identifiers, batch numbers, or categories; no blank strings in text columns; no numeric infinities.
- All property-condition and city-zone values match the brief's allowed categories. Incoming batches introduce no unseen categories.
- All parking values are 0 or 1; neighborhood scores are within 1–10. Area, bedrooms, bathrooms, and price are positive. Age and distance are nonnegative.
- Observed area, bedrooms, bathrooms, and non-missing ages are all integer-valued. Ages parse as floats because of missing values.
- These checks found no obvious structural rejection scenario in the supplied files. The later bad-data demonstration will require a clearly documented, isolated invalid input; preserve the originals.

#### Missing values

| Measure | Historical | Batch 1 | Batch 2 | Batch 3 |
|---|---:|---:|---:|---:|
| Rows | 4,000 | 500 | 500 | 500 |
| Missing `Age_Years` | 160 (4%) | 20 (4%) | 20 (4%) | 20 (4%) |
| Missing `Distance_to_Center_km` | 160 (4%) | 20 (4%) | 20 (4%) | 20 (4%) |
| Missing `Neighborhood_Score` | 160 (4%) | 20 (4%) | 20 (4%) | 20 (4%) |
| Rows with any missing field | 456 (11.4%) | 60 (12.0%) | 57 (11.4%) | 57 (11.4%) |

All other columns have zero missing values. Missingness overlaps: historical data has 433 rows missing one field, 22 missing two, and one missing three; batches 2 and 3 each have 54 missing one and three missing two. Batch 1 has 60 rows missing one field.

**Implication:** A gate must accommodate the supplied 4% per-column missingness. Per-column and per-row missingness are different quantities. Dropping every incomplete historical row would discard 456 listings; train-only imputation is a proposed approach. Exact gate limits still need justification and approval.

#### Numeric ranges

| Field | Historical min–max | All incoming min–max |
|---|---|---|
| Area, sq ft | 350–2,699 | 350–2,445 |
| Bedrooms | 1–6 | 1–6 |
| Bathrooms | 1–5 | 1–5 |
| Age, years | 0–40 | 0–40 |
| Distance, km | 1.0–45.0 | 1.2–45.0 |
| Neighborhood score | 1–10 | 1–10 |
| Parking | 0–1 | 0–1 |
| Price, ₹ lakhs | 8.00–157.86 | 8.00–156.03 |

All incoming numeric values fall within the historical min–max ranges. **Range checks alone would therefore miss the distribution changes described below.** Historical extrema are descriptive observations, not automatically valid business limits for future listings.

#### Batch comparison

| Measure | Historical | Batch 1 | Batch 2 | Batch 3 |
|---|---:|---:|---:|---:|
| Mean area, sq ft | 1,149.86 | 1,152.29 | 1,064.39 | 936.32 |
| Mean bedrooms | 2.418 | 2.424 | 2.268 | 2.024 |
| Mean bathrooms | 1.987 | 1.976 | 1.856 | 1.724 |
| Mean age, years | 20.02 | 19.94 | 20.17 | 20.16 |
| Mean distance, km | 11.93 | 11.72 | 12.39 | 11.47 |
| Mean neighborhood score | 6.03 | 6.09 | 6.10 | 5.93 |
| Parking available | 59.73% | 57.20% | 60.60% | 62.60% |
| Mean price, ₹ lakhs | 61.90 | 61.96 | 63.82 | 69.61 |
| Median price, ₹ lakhs | 60.57 | 59.14 | 62.91 | 65.87 |
| Price standard deviation, ₹ lakhs | 22.10 | 21.80 | 24.03 | 27.51 |

Relative to historical data, mean area changes by **+0.21%, −7.43%, and −18.57%** in batches 1, 2, and 3. Mean asking price changes by **+0.09%, +3.11%, and +12.45%**, respectively.

| City-zone share | Historical | Batch 1 | Batch 2 | Batch 3 |
|---|---:|---:|---:|---:|
| North | 19.90% | 19.40% | 14.40% | 11.20% |
| South | 24.58% | 24.80% | 23.40% | 14.80% |
| East | 19.40% | 20.60% | 22.60% | 19.80% |
| West | 20.45% | 19.80% | 23.40% | 23.40% |
| Central | 15.68% | 15.40% | 16.20% | 30.80% |

Rounded shares may not sum to exactly 100%. Property-condition shares also change: `Good` is 45.525% historically versus 42.6%, 52.0%, and 41.0%; `Poor` is 9.075% historically versus 10.2%, 7.8%, and 12.8%.

#### Exploratory distribution measures

For numeric features, the two-sample Kolmogorov–Smirnov **D statistic** is the maximum gap between empirical cumulative distributions; a larger value indicates more separation. Below are descriptive effect measures, not production alert decisions. For categorical data, total variation is half the sum of absolute differences between category proportions; 0 means identical proportions and 1 means disjoint categories.

| Difference from historical data | Batch 1 | Batch 2 | Batch 3 |
|---|---:|---:|---:|
| Area KS D | 0.0338 | 0.1145 | 0.2470 |
| Bedrooms KS D | 0.0170 | 0.0730 | 0.1770 |
| Bathrooms KS D | 0.0143 | 0.0643 | 0.1515 |
| Price KS D (target distribution) | 0.0398 | 0.0610 | 0.1555 |
| City-zone total variation | 0.01425 | 0.06675 | 0.18475 |
| Property-condition total variation | 0.03375 | 0.06475 | 0.05575 |

Exploratory SciPy KS calculations also produced unadjusted p-values. They have not been used to declare alerts: multiple comparisons and tied/discrete observations need consideration before a formal statistical alert policy is adopted. No alert threshold has been selected retrospectively to force a desired batch result.

**Interpretation:** Batch 1 is close to historical data on the inspected summaries. Batch 2 shows a smaller-property mix and some category changes. Batch 3 has the largest observed changes in property size, room counts, city-zone mix, and price distribution. Its Central share rises by 15.125 percentage points. This can motivate investigation, but does not establish why asking prices changed or prove that a trained model will be inaccurate. **Target-distribution change is not the same as performance drift or proof of concept drift.** Those questions need a fixed trained model and labeled evaluation.

#### Unusual observations to retain and investigate

- Exactly 350 sq ft occurs 76 times historically and 10, 11, and 32 times in the respective incoming batches. Exactly ₹8 lakhs occurs 10, 2, 3, and 0 times. These repeated lower boundaries may reflect clipping or data-construction rules, but provenance is unknown; do not assert that the data is synthetic or delete these records automatically.
- Bathrooms exceed bedrooms in 113 historical records and 10, 14, and 21 incoming records. This is not inherently impossible and should not become an automatic rejection rule without a business justification.
- Using historical Q1 − 1.5×IQR and Q3 + 1.5×IQR fences, historical outlier counts are 15 for area, 98 for distance, and 60 for price. The corresponding batch counts are (3, 5, 6), (2, 20, 8), and (0, 7, 27). These are descriptive flags, not confirmed errors. Batch 3 has no area observations outside those historical fences despite a clear shift toward smaller homes.
- Overall schema/range quality and stable missingness can coexist with meaningful input shifts. The design needs separate validation gates, distribution monitoring, and model-performance monitoring.

#### Integrity and scope

SHA-256 hashes were computed before and after the analysis and matched exactly:

| Source | SHA-256 |
|---|---|
| `capstone_house_prices_train.csv` | `8696565fd2a80775efee9574463c81877a23cbf51314a72e5919c81936036a3c` |
| `capstone_incoming_batches.csv` | `94c1c5aeac37d19d620b0698f7b65dcc792e2dc2196d4e68ced356921359318e` |

Calculations used pandas group-by summaries, sample standard deviations (`ddof=1`), observed-value distributions, and SciPy 1.16.3 `ks_2samp`. Results are rounded for readability. No model was trained and no data gate, drift alert, or performance threshold was finalized. Incoming target summaries have now been inspected; be transparent about this exploration and do not present these batches later as an untouched blind test set. Future model fitting and tuning should use a predefined split of the historical data; use the incoming batches for the assigned monitoring demonstration.

### Initial model comparison · 4 October 2026 · completed

**Scope:** One exploratory experiment on historical data only, using the existing installed libraries. The incoming CSV was not loaded during model comparison. No packages were installed and no Git activity occurred.

#### Evaluation design and preprocessing

- Fixed random seed: **42**. First reserve 20% of historical rows for test; split the remaining 80% into training and validation using validation fraction 0.20 / 0.80, also with seed 42.
- Result: **2,400 training rows, 800 validation rows, 800 reserved test rows**. Membership is recorded by `House_ID` and checked to be disjoint and exhaustive.
- This is a random split because the supplied historical schema has no date field. It does not demonstrate generalization across time; incoming batches provide a separate later monitoring exercise.
- Predictive inputs: seven numeric columns and two categorical columns; exclude `House_ID` and target. `Batch` is excluded by validation of the feature list.
- Numeric preprocessing: median imputation followed by standardization. Categorical preprocessing: most-frequent imputation and dense one-hot encoding with unknown categories ignored. Each candidate gets its own preprocessing fitted only on training rows.
- Select the candidate with the lowest **validation MAE**, the average absolute asking-price error in ₹ lakhs. Report RMSE alongside it to expose larger errors; report R² as supplementary context.
- No parameter search, test-set prediction, incoming-batch prediction, or refitting on combined training/validation rows was performed. The selected artifact remains trained on 2,400 rows.

#### Actual measured results

| Model | Training MAE, ₹ lakhs | Validation MAE, ₹ lakhs | Validation RMSE, ₹ lakhs | Validation R² |
|---|---:|---:|---:|---:|
| Constant training median | 17.182 | 17.729 | 22.721 | −0.0002 |
| **Ridge regression** | **5.623** | **5.742** | **7.522** | **0.8904** |
| Random forest | 3.500 | 7.943 | 10.152 | 0.8003 |
| Histogram gradient boosting | 3.875 | 6.002 | 7.818 | 0.8816 |

The constant predictor always outputs **₹61.27 lakhs**, the training-target median. Ridge reduces validation MAE by **67.61%** relative to this baseline. Its average absolute validation error is approximately **₹5.74 lakhs (₹574,199)**; this is neither a per-house error guarantee nor a confidence interval. RMSE is approximately ₹7.52 lakhs.

Ridge is the **initial candidate**, not a registered or deployed production model. It has the lowest validation MAE in this fixed comparison. Gradient boosting is only ₹0.26 lakhs worse in validation MAE; no statistical test or repeated-split experiment establishes that Ridge is universally superior. The forest and boosting models show larger training-to-validation gaps. Keep the simpler model as the current candidate while preserving the other results.

Parameters: Ridge `alpha=10`; forest 300 trees, minimum leaf size 2, one job, seed 42; histogram boosting learning rate 0.08, 200 iterations, 15 maximum leaf nodes, L2 regularization 1.0, seed 42, internal early stopping disabled. Other estimator settings use defaults from **scikit-learn 1.8.0**. The exploratory script explicitly disables boosting early stopping so it does not silently allocate a different internal validation split. When integrating into the production configuration, expose this setting there as well.

#### Artifacts and reproduction

| Path | Contents |
|---|---|
| `experiments/baseline_config.yaml` | Input/output paths, feature lists, split fractions, seed, preprocessing, and model settings |
| `experiments/run_baselines.py` | Executable comparison, input/split checks, train-only preprocessing, validation metrics, and artifact recording |
| `experiments/baseline_results/results.json` | Full-precision metrics, configuration and source hashes, package versions, split sizes, and selection result |
| `experiments/baseline_results/split_membership.csv` | Listing IDs assigned to training, validation, or reserved test |
| `experiments/baseline_results/validation_predictions.csv` | Actual validation prices and all four candidates' predictions |
| `experiments/baseline_results/selected_model.joblib` | Fitted Ridge preprocessing and estimator from this experiment |

Run from the workspace root with the same installed package versions:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B experiments/run_baselines.py --config experiments/baseline_config.yaml
```

The script completed successfully. It checked source SHA-256 before and after training; the historical CSV hash still matches Section 4. It records that the test was not evaluated and incoming data was not loaded. A small follow-up read confirmed saved split counts, selected-model improvement, and artifact names. No separate software test suite or fresh-clone reproduction has been run. Rerunning this command overwrites the files in its configured output directory; this is an exploratory runner, not a versioned orchestration system.

**Limitations and next design decisions:** The test rows were included in earlier whole-dataset descriptive analysis, but have not been used for fitting, model comparison, or prediction-error evaluation. Keep them reserved until the evaluation protocol and candidate are fixed. Validation results are used for selection, so they are not an unbiased final generalization estimate. Numeric acceptance thresholds, champion comparison tolerance, latency targets, and freshness objectives remain undecided. Do not label any suggested cutoff as a professor-provided requirement.

## 5. Assignment acceptance checklist

Checked items have local implementation/evidence. Unchecked items require external execution, presentation, or genuine Git history; do not infer full assignment completion from implemented files alone.

### Task 1 · Problem framing and lifecycle map

- [x] Define the business objective and at least one prediction-error metric.
- [x] Explain the metric in language the founders understand.
- [x] Define non-functional requirements, including prediction latency and model freshness.
- [x] Choose numeric success thresholds and justify them.
- [x] Produce a design note of **at most two pages**, including an architecture diagram.
- [x] Map every architecture component to an MLOps lifecycle stage.

### Task 2 · Configuration, code, and data management

- [x] Use one YAML configuration as the pipeline's single source of truth.
- [ ] Version code, configuration, and data.
- [x] Validate configuration when loading it.
- [ ] Avoid hard-coded paths, thresholds, and hyperparameters.
- [ ] Demonstrate that a fresh clone reproduces reported metrics within an explicitly stated tolerance.

### Task 3 · Orchestrated pipeline

- [x] Implement separate stages: **ingest → validate data → build features → train → evaluate → register → deploy → monitor**.
- [x] Define each stage's inputs and outputs.
- [x] Make each stage independently re-runnable without repeating the entire pipeline.
- [x] Provide stage-level logs and run history.
- [x] Supply a workflow graph that matches the implemented code.

### Task 4 · Gates and safe failure

- [x] Implement a data gate, with checks such as schema, ranges, and missingness limits.
- [x] Implement a model gate with both an absolute quality threshold and comparison against the current production model.
- [x] Make gate thresholds configurable and justify them.
- [x] Demonstrate a **bad-data failure**.
- [x] Demonstrate a **model-below-threshold failure**.
- [x] After each failure, prove that the production model and endpoint are unchanged and continue serving.
- [x] Explain the rejection in logs or run output and stop the attempted promotion cleanly.

### Task 5 · Tracking, registry, and lineage

- [x] Track every run and register models with lifecycle/stage transitions.
- [x] Allow registry transitions only through the pipeline.
- [x] Include data version and configuration in run records.
- [ ] Starting from the deployed model, demonstrate its **code version → data version → configuration → producing run** linkage.
- [ ] Show that lineage live as required, and retain supporting evidence.

### Task 6 · Automated build and release

- [ ] A pull request triggers tests and a lightweight pipeline run.
- [ ] A merge to `main` builds a deployable image and releases the new version.
- [ ] CI history includes a passing PR, a failing PR, and at least one release.
- [ ] Tag images so a running container can be traced to a commit.
- [ ] Write the rollback procedure and test it at least once.

### Task 7 · Serving and monitoring

- [ ] Serve the production model through a containerized API.
- [ ] Measure latency, throughput, errors, and the distribution of predicted prices.
- [x] Process all three incoming batches for data drift.
- [x] Measure performance drift using the supplied actual prices.
- [x] Provide a dashboard or report covering operational metrics and all three batches.
- [x] Define and justify alert thresholds.
- [x] Identify which batches trigger which alerts, with evidence.
- [x] Explain the pipeline's intended response to each alert.

### Task 8 · Final demonstration

- [ ] Prepare a **5–10 minute** live or recorded demonstration.
- [ ] Show a code change, CI run, pipeline run, deployment, and monitoring update.
- [ ] Follow with a failure scenario that visibly preserves safe serving behavior.
- [ ] Have every team member explain part of the system.
- [ ] Prepare both members to explain, justify, and modify any part live.

## 6. Deliverables and evidence register

| Required deliverable | Expected evidence | Status |
|---|---|---|
| One repository | Pipeline, configuration, tests, workflows, Dockerfile, README | 🟡 Pending |
| Design note | At most two pages with architecture diagram | 🟡 Pending |
| Workflow and history | Graph, run history, registry screenshots | 🟡 Pending |
| Two gate failures | Bad-data and bad-model rejection, with serving continuity evidence | 🟡 Pending |
| Lineage demonstration | Deployed model traced to code, data, configuration, and run | 🟡 Pending |
| CI/CD history | Passing/failing PRs and at least one release | 🟡 Pending |
| Rollback proof | Written procedure plus a recorded successful test | 🟡 Pending |
| Monitoring dashboard/report | Operational metrics and drift across all three batches | 🟡 Pending |
| Final demonstration | 5–10 minutes, with team participation and safe failure | 🟡 Pending |
| Reflection | One page on improvements possible with more time | 🟡 Pending |

Store real command outputs, artifact paths, run IDs, commit IDs, and links as they become available. Never mark a requirement complete using an invented metric, screenshot, CI result, deployment, or unexecuted command.

## 7. Marking rubric and syllabus coverage

| Criterion | Marks | Main evidence |
|---|---:|---|
| Problem framing and design | 10 | Objectives, metrics, architecture |
| Pipeline architecture and orchestration | 20 | Separate, re-runnable stages and matching graph |
| Gates and failure handling | 15 | Both gates, safe stops, continued production serving |
| Tracking, registry, and lineage | 15 | Complete records and working lineage demonstration |
| CI/CD and release | 15 | PR checks, release on merge, rollback |
| Deployment and monitoring | 20 | Operational metrics, drift, justified alerts |
| Demonstration and documentation | 5 | Complete explanation and team participation |
| **Total** | **100** | |

Syllabus mapping: Topic 1, fundamentals/lifecycle → Task 1; Topic 2, CI/CD → Task 6; Topic 7, endpoint monitoring → Task 7; Topic 15, end-to-end pipeline → Tasks 3–5. Integrated topics: 4 and 10, versioning/YAML → Task 2; 6 and 13, deployment/orchestration → Tasks 3, 6, 7; 12, training/tuning → Task 3.

## 8. Tools and operating constraints

These are the **brief's suggested tools**, not a finalized technology selection or a list of installed software.

| Purpose | Suggested tools | AWS service replaced in syllabus |
|---|---|---|
| Tracking and registry | MLflow | SageMaker Experiments / Registry |
| Orchestration | Prefect or ZenML | Step Functions / SageMaker Pipelines |
| Versioning | Git, GitHub, DVC | CodeCommit |
| CI/CD | GitHub Actions, pytest | CodePipeline / CodeDeploy |
| Packaging | Docker | — |
| Monitoring | Prometheus, Grafana, Evidently | CloudWatch / Model Monitor |
| Configuration | YAML, PyYAML | — |

Equivalent free tools may be substituted if justified in the report. Use only free tools and free-tier resources. Do not assume a service is free for the intended use without checking its current terms and limits when selecting it.

Every stage must be automated; no manual copying of files between stages. Only the pipeline may change the production model. Never commit credentials or secrets.

Before implementation, check current official documentation and compatible package versions. Resolve how the chosen MLflow version represents lifecycle transitions and show how that implementation satisfies the brief. Deployment location, image registry, data-version storage, artifact storage, and how CI reaches the deployment environment all remain undecided.

## 9. Proposed work sequence

This was the initial dependency-based plan. The user subsequently authorized autonomous completion on 5 October; do not wait for phase approvals. See the delivery record for current status.

| Phase | Work | Completion condition |
|---|---|---|
| 1 · Context | Read brief; create this document | Requirements, preferences, and next action recorded |
| 2 · Environment | Inspect local Python, Docker, and relevant tooling; defer Git/GitHub work per user instruction | Local inventory complete; installation plan pending approval |
| 3 · Data and success criteria | Parse both CSVs, audit quality, investigate batches, establish a baseline and evaluation approach | Evidence-backed data report and justified proposed thresholds |
| 4 · Design | Select tools; define stage contracts, versioning, promotion, storage, and deployment | Approved architecture, configuration plan, and two-page design note |
| 5 · Core workflow | Implement preprocessing, training, evaluation, orchestration, and stage artifacts | Re-runnable stages with logs and real evaluation results |
| 6 · Safety and lineage | Add gates, tracking, registry, and controlled promotion | Two demonstrated rejections and deployed-model lineage |
| 7 · Release | Containerize API; implement PR checks, release automation, and rollback | Genuine CI history, commit-linked image, and tested rollback |
| 8 · Monitoring | Instrument serving and process three batches | Operational evidence, drift results, and justified alert actions |
| 9 · Submission | Assemble documentation, screenshots, reflection, and demonstration | Complete deliverables and both students ready to explain them |

Some design and implementation steps may need iteration. Record approved changes to sequence and their reasons. Do not treat the table as evidence that a phase has run.

### Proposed ways to make the work distinctive

- Show the same endpoint serving before and after a rejected release, with model-version evidence.
- Make every prediction release traceable to code, data, configuration, and a run.
- Clearly separate input drift from actual loss of prediction accuracy; an input shift alone does not prove model failure.
- Explain error in ₹ lakhs and alert consequences in language a founder can act on.
- Show useful error breakdowns by city zone or property condition if sample sizes support them.
- Demonstrate recovery through a tested rollback and a reproducible fresh-clone run.
- Use consistent colors and diagrams in the final dashboard and presentation; keep textual status labels alongside colors.

These are proposals. No experimental result or extra scope has been approved by listing them here.

### Engineering decisions to resolve

1. Evaluation split, random seed, baseline model, error metrics, tolerance, and defensible numeric thresholds.
2. Preprocessing behavior for missing values and unseen categories.
3. First deployment behavior when no production model exists for comparison.
4. Durable stage inputs/outputs so individual stages can be rerun safely.
5. Candidate-versus-production comparison and rules for promotion, including release health checks.
6. Failure fixture construction that preserves supplied source data and produces a fair demonstration.
7. Registry lifecycle implementation, model storage, data versioning, and artifact retention.
8. Deployment environment, container registry, CI access, and rollback mechanics within free-resource limits.
9. Monitoring reference data, statistical/effect-size thresholds, performance thresholds, and alert responses.
10. Whether and when incoming batches are eligible for retraining; monitoring order and evaluation isolation.

## 10. User involvement and downloads

**Nothing needed downloading for reading, documentation, or the local tool check.** Existing Python libraries are sufficient to begin data investigation. The full pipeline will need additional tools, listed below; install only after approval and dependency selection.

### Local tool inventory · 4 October 2026

Inspection used executable discovery, Python package metadata, and direct import checks. No packages were installed, no services started, and no account authentication inspected.

| Component | Observed status |
|---|---|
| Operating system | macOS 26.5.2, Apple Silicon (`arm64`) |
| Python | 3.12.0 at `/opt/anaconda3/bin/python3` |
| Environment tooling | `venv` module available; `conda` executable found; pip 25.3 |
| Data libraries | pandas 2.3.3; NumPy 2.3.5; SciPy 1.16.3 |
| Modeling | scikit-learn 1.8.0 |
| Plotting | matplotlib 3.10.8; seaborn 0.13.2 (metadata checked; imports not checked) |
| Configuration | PyYAML 6.0.3; Pydantic 2.13.4 |
| Tests and HTTP client | pytest 9.0.3; httpx 0.28.1 |
| API serving | FastAPI 0.135.3; Uvicorn 0.44.0 |
| Metrics instrumentation | prometheus-client 0.24.1; this is a Python client, not the Prometheus server |
| Tracking | MLflow not installed in the inspected Python |
| Orchestration | Neither Prefect nor ZenML installed in the inspected Python; choose one later |
| Data versioning | DVC not installed in the inspected Python; Git-related setup deferred |
| Drift reporting | Evidently not installed in the inspected Python |
| Containers | Docker, Docker Compose, Podman, and Colima executables not found on PATH; Docker/OrbStack/Podman Desktop apps not found at the checked standard `/Applications` paths |
| Monitoring servers | Prometheus and Grafana executables not found on PATH; may later run in containers |
| Other tooling | Homebrew found; `uv` not on PATH (not a prerequisite) |
| Storage | Approximately 36 GiB available on the workspace filesystem at inspection |
| Memory | Hardware memory query denied by environment permissions; capacity not established |

Direct imports succeeded for NumPy, pandas, SciPy, scikit-learn, PyYAML, Pydantic, pytest, FastAPI, Uvicorn, prometheus-client, and httpx. This establishes basic importability, not complete application compatibility. No model training or project tests were run. Missing Python packages refer only to the active Anaconda Python; other environments were not exhaustively searched. Container runtime absence is limited to the paths checked.

**Proposed setup approach:** Create a project-specific environment before installing the eventual pipeline dependencies, then record compatible versions for reproducibility. The present inventory is not a dependency lock file. Docker setup can wait until container work; GitHub Actions and access can wait until the user resumes Git work. Prometheus/Grafana need not also be installed natively if the approved design uses containers.

The assistant can prepare code, configuration, reports, and explanations within approved scope and available access. The user may need to complete account sign-in, authorize repository access, or install/start a desktop application if necessary. Explain the specific need when it arises. Never request that passwords or tokens be pasted into this document or committed.

The final teaching and demonstration phase must include both students' genuine understanding and participation. No deadline, repository visibility preference, deployment requirement beyond the brief, or available hardware budget has been supplied.

## 11. Progress and approval log

| Date | Event | Scope / outcome |
|---|---|---|
| 2026-10-04 | User described Group 4 and requested careful reading, durable context, sequential guidance, and approval before actions | Team identity and working preferences recorded |
| 2026-10-04 | Initial read-only inspection | Complete brief text read; source files found; CSV headers, sample rows, and line counts checked; profile access results recorded |
| 2026-10-04 | Assistant proposed `PROJECT_CONTEXT.md`; user answered “yes” | Creation and population of this document authorized |
| 2026-10-04 | Context document created | 🟢 Phase 1 complete; implementation phases remain pending |
| 2026-10-04 | User approved tool checks and deferred Git access/work | Local inspection only; no GitHub authentication checks |
| 2026-10-04 | Local inventory and Python import checks completed | 🟢 Existing data/model/API libraries usable for imports; missing pipeline/container tools recorded; no installations |
| 2026-10-04 | User approved investigation of both datasets | Data analysis and context update; original files preserved; model training not included |
| 2026-10-04 | Initial dataset investigation completed | 🟢 Shapes, missingness, duplicates, ranges, categories, and batch differences recorded in Section 4; source hashes unchanged |
| 2026-10-04 | User approved initial historical baseline-model comparison | Existing tools only; reserve test set; no installations or Git work |
| 2026-10-04 | Four baseline candidates trained and compared | 🟢 Ridge selected by validation MAE 5.74199; 800 test rows reserved; config, runner, predictions, split membership, results, and model saved |

**Measured model results:** Validation MAE 5.74199 / RMSE 7.52218; final 800-row historical test MAE 5.77518 / RMSE 7.50646 lakhs. Incoming batch MAEs 5.56241, 6.86657, 13.11252. See delivery record and reports.
**Tests or pipeline runs:** 15 tests passed; real MLflow runs and two registered versions; two gate failures; safe-serving and model rollback evidence; in-process HTTP benchmark. No actual GitHub CI or Docker runs.
**Repository URL / commits / PRs:** Not established.  
**Local model state:** Champion version 1, MLflow run `e956f36b75c640a5b5dbdcdb9f4f3e0c`; version 2 archived after rollback. Local API model-pointer deployment was executed; actual network/container deployment remains pending.
**Installations:** MLflow 3.10.1 and missing dependencies installed into workspace `.venv` after verified direct wheel downloads. The virtual environment inherits existing scientific libraries. No accounts changed; no Git work performed.

## 12. Resume instructions for any future AI session

1. Read this entire file and the user's latest message. Follow the latest autonomous-completion authorization, while preserving the Git/GitHub deferral.
2. Inspect actual artifacts before claiming implementation progress; this file may lag behind subsequent work.
3. Distinguish completed work, proposed work, missing information, and measured evidence.
4. Do not regenerate or replace supplied datasets, invent metrics, or fabricate team commits.
5. Proceed autonomously with required local work. Avoid routine confirmation requests; do not infer Git/GitHub access from general implementation authorization.
6. After approved work, update this file with decisions, artifact paths, results, remaining issues, and the next action. Keep old failed results clearly labeled if they explain a decision.
7. Keep this file self-contained: a new reader should understand what was requested, what was delivered, and what still needs doing without access to the original chat.

**Next action:** No routine approval required. Use `docs/SUBMISSION.md` to finish real Docker/network/GitHub/presentation evidence when the environment and accounts are available. Do not claim those steps have already run. Preserve the final test result rather than repeatedly selecting on it.


## 13. Delivery record · 5 October 2026

### Authorization and actual execution

The user said: “now you can stop asking and start completing the assignment ... don't ask but make logical decisions.” Local implementation, package installation and verification therefore proceeded without repeated permission requests. Git/GitHub remained deferred.

The default pip network path could not resolve PyPI. Direct `curl` downloads worked when invoked separately. Nineteen required wheels were fetched from PyPI, SHA-256 checked against package metadata, and installed offline into `.venv`, which uses existing system scientific libraries. Full MLflow 3.10.1 is operational. Prefect was investigated but not installed: the implementation uses a documented small persisted DAG instead. No invented third-party orchestration execution is claimed.

### Implementation map

| Artifact | Purpose / evidence |
|---|---|
| `README.md` | Main usage guide, architecture, measured results, limitations and commands |
| `config.yaml` | Validated workflow configuration, thresholds, paths, features, model and serving settings |
| `capstone/config.py` | Pydantic configuration validation; YAML `schema` maps internally to `data_schema` |
| `capstone/core.py` | Eight-stage persisted DAG, artifact hashes, independent reruns, MLflow, gates, locked promotion and rollback |
| `capstone/api.py` | FastAPI prediction/health/lineage/Prometheus endpoints; immutable release loading and cached model fallback |
| `capstone/monitoring.py` | Actual batch drift/performance computation and styled HTML report |
| `capstone/demo.py` | Executed safe failures, second release, rollback, lineage and in-process HTTP measurements |
| `capstone/__main__.py` | CLI for full workflow, individual stages, monitoring, serving, lineage, rollback and one-time final test |
| `tests/test_capstone.py` | 15 passing tests covering config, leakage, malformed data, reruns, hashes, baseline reproduction, gates and safe failure/rollback |
| `requirements.txt`, `requirements.lock` | Direct dependencies and exact 87-package installed dependency closure |
| `data_manifest.json` | SHA-256 versions of original supplied data; commit alongside data once Git is enabled |
| `Dockerfile`, `compose.yaml` | Containerized API, pipeline job, MLflow, Prometheus, Grafana; named model/report volumes; not executed here |
| `monitoring/` | Generated alert thresholds, Prometheus scraping, Grafana dashboard/provisioning |
| `.github/workflows/` | Prepared PR checks and main-branch test/container smoke/build/image/release workflow; optional persistent self-hosted deployment |
| `scripts/deploy.sh` | Container deployment and attempted health-failure model/image rollback; not executed here |
| `scripts/check_reproduction.py` | Fresh-directory reproduction with the existing interpreter, explicitly not a fresh clone/clean-install claim |
| `scripts/snapshot_registry.py` | Exports real MLflow run and model-version records |
| `scripts/generate_monitoring_config.py` | Generates deployment alert/dashboard files from primary YAML |
| `scripts/build_documents.py` | Rebuilds design/reflection PDFs using ReportLab; document tooling is separate from application dependencies |
| `output/pdf/design_note.pdf` | Exactly two pages, rendered and visually inspected |
| `output/pdf/reflection.pdf` | Exactly one page, rendered and visually inspected; team should review/personalize |
| `docs/OPERATIONS.md`, `docs/DEMO.md`, `docs/SUBMISSION.md` | Stage contracts/recovery, 8-minute presentation plan, honest remaining evidence checklist |

### Configured policies and decisions

- Data: exact schema; unique IDs; plausible ranges and integer constraints; known categories; minimum 100 rows; <=8% missing per column, only the three declared nullable columns. Dataset extrema are not used as strict universal business limits.
- Quality: MAE <=7 and RMSE <=9 lakhs; no more than 2% MAE regression against the incumbent on the same validation data. First model uses absolute limits. These limits are project choices justified by baseline results, not professor-provided thresholds.
- Drift: numeric KS D >0.10, categorical total variation >0.10, missingness-rate change >0.03. Effect-size alerts; not p-value significance claims.
- Performance alert: batch MAE >7 lakhs or >1.25 times deployed validation MAE.
- Operations: warm p95 <=200 ms, error fraction <=1%, model age <=30 days before review. Generated Prometheus rules reference those configured values. No outbound alert transport is configured.
- Free-tool substitutions: explicit persisted Python DAG for Prefect/ZenML; SciPy/pandas reports for Evidently; version-controlled source CSVs plus SHA-256/run snapshots for DVC. Git setup itself is still pending. Rationale is in the design note/README.
- MLflow registry uses aliases and lifecycle tags because legacy stages are deprecated; official reference: https://www.mlflow.org/docs/latest/ml/model-registry/workflow/ . The serving manifest is the authoritative model pointer; the registry alias is a descriptive mirror.
- The API uses a read-only model-state volume in Compose. The pipeline alone mutates model versions/pointers. Alias and filesystem pointer updates are not a shared transaction; crash recovery/reconciliation is documented.

### Measured evidence

| Evidence | Actual result |
|---|---|
| `reports/final_test.json` | Model v1, 800 historical held-out rows: MAE 5.7751786370, RMSE 7.5064627264 lakhs; evaluated once after initial selection |
| `reports/monitoring.json` | Batch 1 MAE 5.5624149483, RMSE 7.2391183854; no alert |
| Same report | Batch 2 MAE 6.8665661579, RMSE 9.1032349070; area input alert, no configured MAE performance alert |
| Same report | Batch 3 MAE 13.1125163967, RMSE 16.0852033673; area/bedrooms/bathrooms/city-zone alerts plus performance alert |
| `reports/safe_failures.json` | Missingness failure and dummy-model quality failure both preserve production-manifest hash, model version and prediction; HTTP 200 remains available in TestClient |
| `reports/rollback.json` | Real model release 2 -> 1 rollback verified by identical API response |
| `reports/operational.json` | 100 warm sequential in-process HTTP requests, zero errors; p95 ~3.69 ms, ~289.8 sequential requests/sec in this measurement; not network load capacity |
| `reports/prometheus_metrics.txt` | Real endpoint metrics response including deliberate invalid-request 422 |
| `reports/lineage.json`, `reports/registry.json` | Real registered versions, experiment history, source/data/configuration/model hashes and run linkage |
| `reports/pytest.log`, `reports/junit.xml` | 15 passed; two MLflow schema advisory warnings. Nullable numeric columns are floats; required integer features reject null at the API |
| `reports/source_integrity.json` | Both supplied CSV hashes unchanged |
| `reports/reproduction.json` | Fresh-directory experiment using the existing dependencies; consult file for exact difference/tolerance |

The model serving state is currently local version 1 after rollback. Source snapshots refer to the code at the time each real run occurred; later robustness/documentation changes do not rewrite historical provenance. All CI commit identifiers remain honestly `uncommitted-local-source` until GitHub injects a real commit.

### External limitations: do not mark these complete

1. No Docker runtime is installed. The Python `docker` package required by MLflow is only an SDK. Dockerfile, Compose, container health checks, image rollback and generated Grafana configuration are prepared but not runtime-verified.
2. Starting Uvicorn reached application startup but socket binding on 0.0.0.0:8000 failed with `Operation not permitted` in this sandbox. Actual network serving and UI screenshots remain pending. API behavior was verified through FastAPI TestClient, clearly labeled in reports.
3. Git access was deferred. No repository initialization, pushes, PRs, releases, real CI history or individual student commits were made. Workflow files are not evidence of executed workflows.
4. Persistent automated deployment requires a Docker host/self-hosted runner with label `capstone` and `ENABLE_LOCAL_DEPLOY=true`. Without it, the prepared main workflow publishes a deployable image/release but does not update a persistent endpoint.
5. Dependency pins are recorded; a genuinely fresh installation and fresh-clone reproduction have not run. The fresh-directory reproduction uses the same interpreter.
6. The required live/recorded full-loop demonstration, actual UI screenshots, and both students' genuine explanations/contributions must still be completed.

The project is therefore a working local implementation and prepared submission package, **not a claim that every external acceptance criterion has already been satisfied**. Continue from `docs/SUBMISSION.md` when those environments/accounts are available. Do not ask for routine local-work approval again.

### Packaged handoff

`group4_capstone_submission.zip` contains source/configuration, original datasets and brief, tests, workflow/container files, measured reports, baseline experiment evidence, and PDFs. It excludes runtime state, downloaded wheels, virtual environments and model binaries. Regenerate model/MLflow state with the README commands after extraction; saved local absolute paths in historical evidence are provenance, not portable deployment settings. Archive integrity was checked. The latest suite passed 15 tests; fresh-directory reproduction produced exactly the original MAE (difference 0.0, tolerance 1e-6).

### Windows handoff clarification

The user will do all remaining work on Windows. `WINDOWS_START_HERE.md` now lists the ready files, verified results, exact remaining commands, expected outcomes, screenshot filenames, GitHub steps and final submission checklist. Native Windows Python is not supported by the current POSIX `fcntl` lock; use Docker Linux containers (or an appropriately configured Linux environment). Docker is retained because the brief explicitly requires a containerized API and commit-linked deployable image; a public web URL is not explicitly required. Streamlit could be an optional frontend but does not replace the container/release requirements. The guide avoids running `scripts/check_reproduction.py` inside the current Docker image because the image excludes the exploratory baseline files that script references; the documented fresh-clone pipeline evaluation provides the Windows reproduction step.

### Docker Hub publishing selected

The user selected the Docker Hub image-publishing route. `.github/workflows/release.yml` now authenticates with GitHub variable `DOCKERHUB_USERNAME`, optional variable `DOCKERHUB_REPOSITORY` (default `group4-mlflow-capstone`), and secret `DOCKERHUB_TOKEN`. It publishes `linux/amd64` images tagged with the real commit, records the image digest in release notes, and passes the exact digest to the optional `capstone` self-hosted deployment job. GHCR publishing has been removed. `docs/DOCKER_HUB_DEPLOYMENT.md` explains account setup, image publishing, Windows/local or Linux-server startup, state initialization and private SSH-tunnel access. Account credentials, publishing, Docker execution and server access are still unavailable; none has been fabricated or performed. GitHub continues to host code and checks; choosing Docker Hub does not remove the assignment's GitHub evidence requirements. No server or paid plan was selected.

### Consolidated handoff requested

The user found the previous guidance mixed and requested one clear Markdown document covering the assignment, completed work, ready files, outstanding requirements, assistant capabilities, user-only actions and final delivery. `START_HERE_PROJECT_HANDOFF.md` is now the primary entry point. It explicitly distinguishes locally verified results from prepared infrastructure and real account/host/presentation work still pending, and orders execution into six phases. README and the Windows guide point to it. No new account, deployment or test result is claimed by this documentation update.

### Folder-specific Git identity wrappers

The user explicitly requested `./git-swagata commit ...` and `./git-sumit commit ...` with one authorized push token and no global configuration changes. Added these wrappers plus `scripts/git-identity.sh` and `docs/FOLDER_GIT_IDENTITIES.md`. They select author/committer identity per invocation and obtain verified emails from repository-local `team.swagata.email` / `team.sumit.email`. Authentication remains separate; both wrappers share the staging area and push credentials. No project repository was initialized, no remote/authentication configured, and no project commits/pushes were made. Checks in a temporary repository verified missing-repository/email guards, identity selection and absence of global writes/commits; the temporary repo was removed. User-requested Git setup work is now allowed within this scope, superseding the earlier blanket Git deferral; publishing and actual author emails/token configuration are still pending.

### Current laptop decision: macOS, superseding Windows

The user explicitly said to do all work on this laptop and forget Windows. The current execution platform is the Mac workspace `/Users/krishsoni/Documents/swagata/ml-ops`. Earlier Windows transfer instructions are historical and no longer the active route. Git wrappers and the local setup script work in the Mac Terminal; Git Bash is unnecessary. The assistant ran `bash setup-git-identities.local.sh` here, but initialization still failed with `.git: Operation not permitted`. This is an agent filesystem permission restriction; no repository, identities, commits, remote or authentication was created by the failed command. The user can run the prepared script from Terminal on this same Mac outside the restricted agent tool. Do not route Git metadata elsewhere or use another process to evade this restriction. The existing `.venv` remains available.

### Local Git initialization confirmed; remote supplied

The user ran the identity setup in the Mac Terminal. Read-only checks confirm this project is now a Git repository, both wrapper identities match the supplied emails, and no commits exist. The confirmed GitHub destination is `https://github.com/Swagata-Bhowmik/group4-mlflow-capstone.git`; the user reports creating the empty repository and an access token. The assistant attempted `git remote add origin` but the tool cannot lock `.git/config` due to filesystem permissions. Remote configuration, staging/committing and pushing must currently be run in the user's Mac Terminal. No token was requested or received in chat; do not embed one in repository files or remote URLs. The identity-setup script is excluded from both Git and Docker image context. Do not manufacture separate Sumit contribution commits for existing assistant-produced work.

### Ordered Mac commit guide

The user requested exact one-at-a-time commands with alternating identity wrappers. `COMMIT_COMMANDS_MAC.md` supplies six ordered import groups: foundations (Swagata), baseline (Sumit), application (Swagata), tests/evidence (Sumit), infrastructure (Swagata), documentation (Sumit), then one token-authenticated push. Messages describe imported AI-assisted work; the guide requires each member to review/authorize attribution and explicitly states that alternating import commits does not establish independent student contributions or past development history. Shell syntax and coverage of current intended untracked files were checked without executing commits. All real project commits/pushes remain unperformed by the assistant due to `.git` write restrictions.
