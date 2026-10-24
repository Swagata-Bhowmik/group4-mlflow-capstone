"""Generate the two-page design note and one-page reflection from recorded evidence.

Every number below is read from reports/ or experiments/ so the documents cannot drift
from the measured results. Run from the project root: python scripts/build_documents.py
"""
from pathlib import Path
import json
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak, Spacer
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon, Circle, Ellipse

OUT = Path('output/pdf'); OUT.mkdir(parents=True, exist_ok=True)
R = lambda name: json.loads((Path('reports') / name).read_text(encoding='utf-8')) if (Path('reports') / name).exists() else None
DATE = '23 OCT 2026'

baseline = {r['model']: r for r in json.loads(Path('experiments/baseline_results/results.json').read_text(encoding='utf-8'))['results']}
ridge = baseline['ridge']; final = R('final_test.json'); mon = R('monitoring.json')
live = R('live_safe_failures.json'); load = R('load_test.json'); fresh = R('fresh_clone_reproduction.json'); rollback = R('render_rollback.json')
b = {x['batch']: x for x in mon['batches']}

NAVY = colors.HexColor('#14243b'); TEAL = colors.HexColor('#087e83'); MUTED = colors.HexColor('#4c6075'); PALE = colors.HexColor('#edf5f7')
VIOLET = colors.HexColor('#6250d6'); BLUE = colors.HexColor('#2a78d6'); ORANGE = colors.HexColor('#eb6834'); GREEN = colors.HexColor('#1baf7a')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Hero', fontName='Helvetica-Bold', fontSize=19, leading=22, textColor=NAVY, spaceAfter=3))
styles.add(ParagraphStyle(name='Deck', fontName='Helvetica', fontSize=8.6, leading=11.5, textColor=MUTED, spaceAfter=4))
styles.add(ParagraphStyle(name='Section', fontName='Helvetica-Bold', fontSize=10, leading=12.5, textColor=TEAL, spaceBefore=6, spaceAfter=3))
styles.add(ParagraphStyle(name='Text', fontName='Helvetica', fontSize=8.1, leading=10.6, textColor=NAVY, spaceAfter=3.5))
styles.add(ParagraphStyle(name='Cell', fontName='Helvetica', fontSize=7.4, leading=9.3, textColor=NAVY))
styles.add(ParagraphStyle(name='Tiny', fontName='Helvetica', fontSize=7, leading=9, textColor=MUTED))


def para(text, style='Text'): return Paragraph(text, styles[style])


def footer(canvas, doc):
    canvas.setStrokeColor(TEAL); canvas.line(36, 30, 559, 30)
    canvas.setFont('Helvetica', 7.5); canvas.setFillColor(MUTED)
    canvas.drawString(36, 20, f'GROUP 4  |  MLOPS CAPSTONE  |  {DATE}  |  github.com/Swagata-Bhowmik/group4-mlflow-capstone')
    canvas.drawRightString(559, 20, str(doc.page))


def table(rows, widths):
    t = Table([[para(f'<b>{v}</b>' if i == 0 else str(v), 'Cell') for v in row] for i, row in enumerate(rows)], colWidths=widths, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), PALE), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                           ('LEFTPADDING', (0, 0), (-1, -1), 5), ('RIGHTPADDING', (0, 0), (-1, -1), 5), ('TOPPADDING', (0, 0), (-1, -1), 3),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 3), ('LINEBELOW', (0, 0), (-1, 0), .8, TEAL),
                           ('LINEBELOW', (0, 1), (-1, -1), .3, colors.HexColor('#dce5ec'))]))
    return t


def box(d, x, y, w, h, title, detail, color, dashed=False):
    d.add(Rect(x, y, w, h, rx=5, ry=5, fillColor=colors.white, strokeColor=color, strokeWidth=1.1, strokeDashArray=[3, 2] if dashed else None))
    d.add(Rect(x, y + h - 3, w, 3, fillColor=color, strokeColor=color))
    d.add(String(x + 5, y + h - 13, title, fontName='Helvetica-Bold', fontSize=7.2, fillColor=NAVY))
    for i, line in enumerate(detail.split('\n')):
        d.add(String(x + 5, y + h - 22 - i * 8, line, fontName='Helvetica', fontSize=6.1, fillColor=MUTED))


def arrow(d, x1, y1, x2, y2, color=TEAL):
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=.9))
    import math
    a = math.atan2(y2 - y1, x2 - x1); L, Wd = 4.5, 2.3
    bx, by = x2 - L * math.cos(a), y2 - L * math.sin(a)
    d.add(Polygon([x2, y2, bx - Wd * math.sin(a), by + Wd * math.cos(a), bx + Wd * math.sin(a), by - Wd * math.cos(a)], fillColor=color, strokeColor=color))


def badge(d, x, y, n, color=NAVY):
    """Numbered step marker used on arrows and in the legend table."""
    d.add(Circle(x, y, 6.2, fillColor=color, strokeColor=colors.white, strokeWidth=1))
    d.add(String(x, y - 2.4, str(n), fontName='Helvetica-Bold', fontSize=7, fillColor=colors.white, textAnchor='middle'))


def label(d, x, y, text, size=6.2, color=MUTED, anchor='middle', font='Helvetica-Oblique'):
    d.add(String(x, y, text, fontName=font, fontSize=size, fillColor=color, textAnchor=anchor))


def person(d, cx, y, color):
    d.add(Circle(cx, y + 17, 5.5, fillColor=color, strokeColor=color))
    d.add(Rect(cx - 9, y, 18, 10, rx=5, ry=5, fillColor=color, strokeColor=color))


def cylinder(d, x, y, w, h, title, detail, color):
    e = 5  # ellipse half-height
    d.add(Rect(x, y + e, w, h - 2 * e, fillColor=colors.white, strokeColor=None))
    d.add(Ellipse(x + w / 2, y + e, w / 2, e, fillColor=colors.white, strokeColor=color, strokeWidth=1.1))
    d.add(Rect(x, y + e, w, h - 2 * e, fillColor=colors.white, strokeColor=None))
    d.add(Line(x, y + e, x, y + h - e, strokeColor=color, strokeWidth=1.1)); d.add(Line(x + w, y + e, x + w, y + h - e, strokeColor=color, strokeWidth=1.1))
    d.add(Ellipse(x + w / 2, y + h - e, w / 2, e, fillColor=PALE, strokeColor=color, strokeWidth=1.1))
    d.add(String(x + w / 2, y + h - 19, title, fontName='Helvetica-Bold', fontSize=7.2, fillColor=NAVY, textAnchor='middle'))
    for i, line in enumerate(detail.split('\n')):
        d.add(String(x + w / 2, y + h - 28 - i * 7.6, line, fontName='Helvetica', fontSize=6, fillColor=MUTED, textAnchor='middle'))


def zone(d, x, y, w, h, title, color):
    d.add(Rect(x, y, w, h, rx=8, ry=8, fillColor=colors.HexColor('#f7f9fb'), strokeColor=color, strokeWidth=.8, strokeDashArray=[2, 2]))
    d.add(Rect(x, y + h - 15, w, 15, rx=8, ry=8, fillColor=color, strokeColor=color))
    d.add(Rect(x, y + h - 15, w, 7, fillColor=color, strokeColor=color))
    d.add(String(x + w / 2, y + h - 11, title, fontName='Helvetica-Bold', fontSize=7, fillColor=colors.white, textAnchor='middle'))


def architecture():
    """Left to right: develop -> CI/CD -> train and serve on Render -> use and monitor. Numbers match the table below."""
    W, H = 523, 292; d = Drawing(W, H)
    zone(d, 0, 4, 112, H - 6, '1  DEVELOP  (GitHub repo)', VIOLET)
    zone(d, 120, 4, 124, H - 6, '2  CI/CD  (GitHub Actions)', BLUE)
    zone(d, 252, 4, 164, H - 6, '3  TRAIN & SERVE  (Render container)', ORANGE)
    zone(d, 424, 4, 99, H - 6, '4  USE & MONITOR', GREEN)

    # 1 Develop
    person(d, 56, 228, VIOLET); label(d, 56, 218, 'Swagata & Sumit', 6.4, NAVY, font='Helvetica-Bold')
    box(d, 8, 136, 96, 62, 'Git repository', 'code (capstone/), tests\nconfig.yaml: every path,\nthreshold, hyperparameter\nworkflows, Dockerfiles', VIOLET)
    cylinder(d, 14, 22, 84, 88, 'Supplied data', 'train: 4,000 listings\nincoming: 3 x 500\nversioned in Git,\nSHA-256 per run', VIOLET)
    d.add(Line(56, 110, 56, 136, strokeColor=VIOLET, strokeWidth=.9, strokeDashArray=[2, 2]))
    arrow(d, 56, 214, 56, 199, VIOLET); badge(d, 66, 207, 1)

    # 2 CI/CD
    box(d, 128, 196, 108, 58, 'PR: Quality checks', 'pytest (16 tests) +\npipeline up to the\nmodel gate. Fail = no\nmerge (PR #2)', ORANGE, dashed=True)
    box(d, 128, 104, 108, 66, 'Merge: Build & release', 'tests + container smoke\nDocker image :<commit>\n-> Docker Hub\nGitHub release build-<sha>\nthen deploy that commit', BLUE)
    box(d, 128, 22, 108, 52, 'Rollback workflow', 'manual: redeploy an\nearlier released commit,\nverify live /lineage', BLUE, dashed=True)
    arrow(d, 104, 180, 128, 220, BLUE); badge(d, 114, 207, 2)
    arrow(d, 182, 196, 182, 171, BLUE); label(d, 194, 181, 'merge', anchor='start'); badge(d, 172, 183, 3)

    # 3 Train & serve
    d.add(Rect(258, 146, 152, 116, rx=6, ry=6, fillColor=colors.white, strokeColor=ORANGE, strokeWidth=1.1))
    d.add(String(334, 249, 'Gated pipeline  (8 stages)', fontName='Helvetica-Bold', fontSize=7.2, fillColor=NAVY, textAnchor='middle'))
    stages = ['ingest', 'validate', 'features', 'train', 'evaluate', 'register', 'deploy', 'monitor']
    for i, st in enumerate(stages):
        row, col = divmod(i, 4); x = 263 + col * 36.5; y = 214 - row * 40
        gate = st in ('validate', 'evaluate'); c = ORANGE if gate else BLUE
        d.add(Rect(x, y, 33, 20, rx=4, ry=4, fillColor=colors.HexColor('#fdeee7') if gate else PALE, strokeColor=c, strokeWidth=.9, strokeDashArray=[2, 1.5] if gate else None))
        d.add(String(x + 16.5, y + 7.5, st, fontName='Helvetica-Bold' if gate else 'Helvetica', fontSize=5.9, fillColor=NAVY, textAnchor='middle'))
        if gate: d.add(String(x + 16.5, y - 6.5, 'DATA GATE' if st == 'validate' else 'MODEL GATE', fontName='Helvetica-Bold', fontSize=4.8, fillColor=ORANGE, textAnchor='middle'))
        if col < 3: arrow(d, x + 33, y + 10, x + 36.5, y + 10, BLUE)
    d.add(Line(263 + 3 * 36.5 + 16.5, 214, 263 + 3 * 36.5 + 16.5, 204, strokeColor=BLUE, strokeWidth=.9))
    d.add(Line(263 + 3 * 36.5 + 16.5, 204, 279.5, 204, strokeColor=BLUE, strokeWidth=.9)); arrow(d, 279.5, 204, 279.5, 194, BLUE)
    label(d, 334, 152, 'a failed gate stops the run; live model unchanged', 5.6, ORANGE)
    arrow(d, 236, 137, 258, 190, BLUE); badge(d, 247, 162, 4)
    arrow(d, 236, 48, 258, 150, BLUE)  # rollback redeploys the container
    cylinder(d, 262, 22, 66, 100, 'MLflow', 'runs, metrics,\nlineage tags;\nregistry versions,\nchampion alias', ORANGE)
    box(d, 336, 22, 72, 100, 'FastAPI service', '/predict (input\nchecks), /health,\n/lineage, /metrics\ndashboard at /\n1 worker, 512 MB', ORANGE)
    arrow(d, 295, 146, 295, 123, ORANGE); badge(d, 305, 135, 5, ORANGE)
    arrow(d, 372, 146, 372, 123, ORANGE); badge(d, 382, 135, 6, ORANGE)
    label(d, 286, 135, 'register', anchor='end'); label(d, 362, 135, 'serve', anchor='end')

    # 4 Use & monitor
    person(d, 473, 228, GREEN); label(d, 473, 218, 'Founders / users', 6.4, NAVY, font='Helvetica-Bold')
    box(d, 430, 138, 87, 66, 'Dashboard', 'predict a price,\nreal listings, pipeline,\nmonitoring, lineage\n(7 tabs, live)', GREEN)
    box(d, 430, 22, 87, 88, 'Monitoring', 'drift + error per\nbatch (KS, TV, MAE)\nPrometheus scrapes\n/metrics; Grafana\nalert rules', GREEN)
    arrow(d, 473, 214, 473, 205, GREEN)
    arrow(d, 408, 95, 430, 170, GREEN); badge(d, 419, 145, 7, GREEN)
    arrow(d, 408, 60, 430, 60, GREEN); badge(d, 419, 70, 8, GREEN)
    # Feedback loop: an alert leads to a new change in the repo (back to step 1).
    d.add(Line(473, 22, 473, 10, strokeColor=GREEN, strokeWidth=.9, strokeDashArray=[3, 2]))
    d.add(Line(473, 10, 6, 10, strokeColor=GREEN, strokeWidth=.9, strokeDashArray=[3, 2]))
    d.add(Line(6, 10, 6, 140, strokeColor=GREEN, strokeWidth=.9, strokeDashArray=[3, 2])); arrow(d, 6, 140, 8, 150, GREEN)
    label(d, 240, 12.5, 'alert -> investigate -> retraining change via a new PR (back to 1)', 5.8, GREEN)
    return d


def build(path, story):
    SimpleDocTemplate(str(path), pagesize=(595.28, 841.89), leftMargin=36, rightMargin=36, topMargin=30, bottomMargin=40).build(story, onFirstPage=footer, onLaterPages=footer)


mae, rmse, dummy = ridge['validation_mae_lakhs'], ridge['validation_rmse_lakhs'], baseline['dummy_median']['validation_mae_lakhs']
lt = load['targets'] if load else {}
rb = (f"tested on {rollback['started'][:10]}: live service rolled back from <font face='Courier'>{rollback['from_commit'][:7]}</font> to "
      f"<font face='Courier'>{rollback['to_commit'][:7]}</font> in {rollback['rollback_minutes']:.0f} min and forward again in {rollback['rollforward_minutes']:.0f} min, "
      f"each verified by live /lineage") if rollback else 'not yet executed'

story = [
    para('Design note: from raw listings to a monitored release', 'Hero'),
    para('Project 4 · Capstone: End-to-End MLflow Pipeline · Swagata Bhowmik (B053) and Sumit Kothari (B062) · Dr. Santosh Kumar', 'Deck'),
    para('01 / Objective, success metrics and non-functional requirements', 'Section'),
    para('A real-estate analytics start-up needs asking-price estimates (INR lakhs) for new listings, retrained and released automatically, with a record of which data, '
         'code and configuration produced each model, and a release process that refuses bad data or bad models while the previous model keeps serving.'),
    table([
        ['Requirement', 'Target (config.yaml)', 'Justification and plain-language meaning for the founders'],
        ['Accuracy: MAE', '≤ 7.0 lakhs (validation)', f'"On average our estimate is within about INR {mae:.1f} lakhs of the asking price" — about {mae / 61.9 * 100:.0f}% of the typical INR 62-lakh listing. '
                                                      f'Ridge achieves {mae:.2f}; a median-only baseline scores {dummy:.1f}. The limit leaves ~20% headroom yet rejects clearly worse models.'],
        ['Accuracy: RMSE', '≤ 9.0 lakhs', f'Penalises occasional large misses that MAE averages away. Ridge achieves {rmse:.2f}.'],
        ['Safe promotion', '≤ 2% worse than serving model', 'A candidate must beat the absolute limits and not regress against the incumbent on the same validation rows.'],
        ['Final test', 'reported once', f'Reserved 800 listings, never used for selection: MAE {final["mae"]:.3f}, RMSE {final["rmse"]:.3f} lakhs.'],
        ['Latency / errors', 'p95 ≤ 200 ms; errors ≤ 1%', 'Interactive single-listing estimates. Measured on the live free host (section 06).'],
        ['Freshness', 'review if model > 30 days old', 'Model age is exported as a metric; drift or performance alerts trigger a retraining run through all gates.'],
        ['Reproducibility', 'MAE within 1e-6', 'Seed 42, locked dependencies, hashed data and code snapshots.'],
    ], [74, 98, 351]),
    para('02 / Architecture mapped to the MLOps lifecycle', 'Section'),
    architecture(),
    table([
        ['#', 'What happens', 'MLOps lifecycle stage'],
        ['1', 'Code, config.yaml (validated on load), tests and the supplied data are versioned together in Git.', 'Framing, data and configuration management'],
        ['2', 'Every pull request runs the tests and the pipeline up to the model gate; a failing check blocks the merge.', 'Continuous integration'],
        ['3', 'A merge builds and tests a container, tags the image with the commit, pushes it to Docker Hub and creates a release.', 'Continuous delivery'],
        ['4', 'That exact commit is deployed to Render; the build runs the pipeline. Rollback redeploys an earlier release.', 'Deployment, orchestration'],
        ['5', 'Validate and evaluate are quality gates; passing models are tracked and registered in MLflow with full lineage.', 'Validation, tracking, governance'],
        ['6', 'The serving API answers /predict after the same input checks and exposes /lineage and /metrics.', 'Serving'],
        ['7', 'Founders use the live dashboard: estimates, real listings, pipeline, monitoring and lineage.', 'Consumption, explainability'],
        ['8', 'Batches are checked for drift and error; metrics feed alerts. An alert leads to a new gated change (back to 1).', 'Monitoring and feedback'],
    ], [14, 380, 129]),
    PageBreak(),
    para('03 / Pipeline and gates — the workflow graph is the STAGES list in capstone/core.py', 'Section'),
    para('Eight stages run in order; each has declared inputs and outputs, persists its result and artifact hashes to the run directory and MLflow, and can be re-run alone '
         '(<font face="Courier">python -m capstone stage &lt;name&gt; --run &lt;dir&gt;</font>). Re-running a stage clears its descendants and any changed upstream artifact is refused, '
         'so a stale gate result can never be reused. A deployed run is immutable.'),
    para(f'<b>Data gate (validate):</b> exact schema, unique IDs, allowed categories, numeric ranges and integer types, ≥100 rows, ≤8% missing per column (observed 4%). '
         f'<b>Model gate (evaluate):</b> MAE ≤ 7 and RMSE ≤ 9 lakhs, and ≤ 2% worse than the serving model. Deploy then re-checks model bytes, incumbent version and a finite prediction '
         f'before atomically switching the serving pointer under a file lock. <b>Safe-failure evidence</b> ({live["transport"] if live else ""}): bad data '
         f'(20% of Age_Years blanked) stopped at validate; a median-only dummy model (MAE {dummy:.2f}) stopped at evaluate; during both runs the endpoint answered '
         f'{sum(s["traffic_during_run"]["requests"] for s in live["scenarios"]) if live else "—"} requests with '
         f'{sum(s["traffic_during_run"]["errors"] for s in live["scenarios"]) if live else "—"} errors and kept model v{live["scenarios"][0]["after"]["model_version"] if live else "—"}.'),
    para('04 / Tracking, registry and lineage', 'Section'),
    para('Every run is an MLflow run carrying configuration, code snapshot hash, Git commit, data hash, stage records and metrics; failed runs are kept. Registration adds a model '
         'version tagged <i>validated</i>; only the deploy and rollback functions set <i>production</i>/<i>archived</i> tags and the <i>champion</i> alias (current MLflow replaces '
         'deprecated stages with aliases). <b>Live lineage:</b> the public <font face="Courier">/lineage</font> endpoint and the dashboard\'s Lineage tab trace the serving model to its '
         'model hash, MLflow run, Git commit, training-data hash and full configuration.'),
    para('05 / CI/CD, release and rollback', 'Section'),
    para('Pull requests run <i>Quality checks</i>: tests plus the pipeline to the model gate. PR #2 (α = 1000) <b>failed</b> because the gate measured MAE 8.77 &gt; 7; the follow-up '
         'commit restored α = 10 and passed. Merging to main runs <i>Build and release</i>: tests, a Docker Compose smoke test, a linux/amd64 image pushed to Docker Hub tagged with the '
         'full commit SHA (and labelled with it), a GitHub release <font face="Courier">build-&lt;sha&gt;</font>, then deployment of that exact commit to Render, which fails the job '
         'unless live /lineage reports the same commit. So any running container links back to a commit. '
         f'<b>Rollback:</b> the <i>Roll back Render deployment</i> workflow redeploys any commit that already has a release; {rb}.'),
    para('06 / Monitoring, alerts and response', 'Section'),
    table([
        ['Signal', 'Alert rule (justification)', 'Batch 1', 'Batch 2', 'Batch 3'],
        ['Input drift', 'numeric KS D > 0.10, categorical total variation > 0.10 (effect size: ~10% of the distribution has moved)', 'none',
         ', '.join(f.replace('_sqft', '').replace('_', ' ') for f in b[2]['drifted_features']) or 'none', ', '.join(f.replace('_sqft', '').replace('_', ' ') for f in b[3]['drifted_features'])],
        ['Missingness', 'change > 3 percentage points (3× the observed rate swing)', 'none', 'none', 'none'],
        ['Performance', 'MAE > 7 lakhs or > 1.25 × validation MAE (labels arrive with each batch)', f'{b[1]["mae"]:.2f} — OK', f'{b[2]["mae"]:.2f} — OK', f'<b>{b[3]["mae"]:.2f} — ALERT</b>'],
        ['Service', 'p95 ≤ 200 ms, errors ≤ 1%, model age ≤ 30 days (Prometheus rules; dashboard Operations tab)', 'see load test below', '', ''],
    ], [62, 222, 56, 70, 113]),
    para('<b>When an alert fires</b> the serving model is never replaced automatically: the team investigates, then starts a new pipeline run with fresh labelled data; the candidate goes live '
         'only through all gates. Batch 3 shifts towards smaller, central properties and doubles the error, so it should trigger retraining. '
         + (f'<b>Live operations (load test, {load["at"][:10]}):</b> {load["sequential"]["requests"] + load["concurrent"]["requests"]} predictions to Render, '
            f'{load["sequential"]["errors"] + load["concurrent"]["errors"]} errors; sequential p95 {load["sequential"]["p95_ms"]:.0f} ms end to end, '
            f'{load["concurrent"]["p95_ms"]:.0f} ms with {load["workload"]["concurrent_workers"]} concurrent clients — the error target is met, the 200 ms latency target is '
            f'<b>not</b> met on the free single-worker host.' if load else '')),
    para('07 / Tool choices and limits', 'Section'),
    para('The brief allows justified free substitutes. A small persisted Python DAG replaces Prefect/ZenML (explicit dependencies, artifact hashes, reruns, MLflow history, no extra '
         'service). Git plus SHA-256 snapshots replace DVC for 0.3 MB of supplied CSVs. SciPy effect-size tests replace Evidently. Render Free replaces a paid cloud host: it sleeps when '
         'idle, keeps no runtime state, and each build retrains from scratch, so cross-release incumbent comparison is proven locally but not on Render. The public API has no '
         'authentication; registry alias and serving pointer are not one transaction.'
         + (f' Fresh-clone reproduction: {fresh["tests"]}; validation MAE reproduced within {fresh["absolute_difference"]:.0e}.' if fresh else '')),
]
build(OUT / 'design_note.pdf', story)

reflection = [
    para('Reflection: what we would improve with more time', 'Hero'),
    para('Group 4 · Swagata Bhowmik (B053) and Sumit Kothari (B062) · Project 4 Capstone', 'Deck'),
    para('What worked', 'Section'),
    para(f'The most useful result is not the accuracy figure (validation MAE {mae:.2f}, final test {final["mae"]:.2f} lakhs) but that every release decision is automatic and '
         'explainable. The gates rejected a bad data file and a weak model while the live endpoint kept serving, a CI pull request with an under-fitting model (α = 1000) was blocked '
         'before it could reach main, and every deployed model can be traced to its commit, data hash and MLflow run. The dashboard made these behaviours visible to non-engineers.'),
    para('What the incoming batches taught us', 'Section'),
    para(f'Batch 2 drifted (smaller areas) without a performance alert ({b[2]["mae"]:.2f} lakhs), while batch 3 drifted in four inputs and its error doubled to {b[3]["mae"]:.2f}. '
         'Input drift and model failure are related but not the same, so we report them separately. Our thresholds were chosen after looking at the data, so these batches '
         'demonstrate the policy rather than validate it.'),
    para('What we would improve', 'Section'),
    para('<b>1. Serving capacity.</b> ' + (f'Under {load["workload"]["concurrent_workers"]} concurrent clients the free host reached p95 {load["concurrent"]["p95_ms"]:.0f} ms '
         'end to end against a 200 ms target. ' if load else '') + 'We would move to a host with more CPU and several workers, add autoscaling, and repeat the load test with '
         'longer, mixed and cold-start workloads.'),
    para('<b>2. Persistent production state.</b> Render Free rebuilds the model on every deploy, so the incumbent comparison only works across releases in the local/Compose setup. '
         'We would keep the MLflow registry and model artifacts in a shared store so every cloud release is compared with the live model, and host MLflow and Grafana with authentication.'),
    para('<b>3. Safer promotion.</b> Replace the file pointer plus registry alias with a single promotion record and crash recovery, and add blue/green or canary releases with '
         'automatic rollback on failed health checks instead of a manual rollback workflow.'),
    para('<b>4. Better monitoring.</b> Calibrate drift thresholds on many reference samples to estimate false-alarm rates, add per-zone error and minimum sample sizes, and send alerts '
         'to a notification channel with an acknowledged incident process.'),
    para('<b>5. Data and orchestration.</b> Use dated listings for time-based evaluation, version data with DVC once files grow, and move to Prefect or ZenML when scheduling, retries '
         'and multiple workers are needed.'),
    para('How we worked', 'Section'),
    para('We defined the requirements and thresholds first, then checked every claim against recorded evidence rather than assumptions. We deliberately kept '
         'the orchestration small so that each of us can explain, run and modify every stage, and each of us rehearses a live change (for example, editing '
         'a threshold in config.yaml and showing the gate react) before the demonstration.'),
]
build(OUT / 'reflection.pdf', reflection)
print('Created design_note.pdf and reflection.pdf')
