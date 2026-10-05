"""Generate the two-page design note and one-page reflection from actual evidence."""
from pathlib import Path
import json
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

OUT=Path('output/pdf');OUT.mkdir(parents=True,exist_ok=True)
NAVY=colors.HexColor('#14243b');TEAL=colors.HexColor('#087e83');MUTED=colors.HexColor('#4c6075');PALE=colors.HexColor('#edf5f7')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Hero',fontName='Helvetica-Bold',fontSize=24,leading=28,textColor=NAVY,spaceAfter=10))
styles.add(ParagraphStyle(name='Deck',fontName='Helvetica',fontSize=10,leading=14,textColor=MUTED,spaceAfter=10))
styles.add(ParagraphStyle(name='Section',fontName='Helvetica-Bold',fontSize=12,leading=15,textColor=TEAL,spaceBefore=10,spaceAfter=5))
styles.add(ParagraphStyle(name='Text',fontName='Helvetica',fontSize=9.2,leading=13,textColor=NAVY,spaceAfter=7))
styles.add(ParagraphStyle(name='SmallText',fontName='Helvetica',fontSize=8,leading=11,textColor=MUTED,spaceAfter=5))

def para(text,style='Text'):return Paragraph(text,styles[style])
def footer(canvas,doc):
 canvas.setStrokeColor(TEAL);canvas.line(42,40,553,40)
 canvas.setFont('Helvetica',8);canvas.setFillColor(MUTED)
 canvas.drawString(42,28,'GROUP 4  |  MLOPS CAPSTONE  |  05 OCT 2026')
 canvas.drawRightString(553,28,str(doc.page))
def table(rows,widths):
 t=Table([[para(str(v),'SmallText') for v in row] for row in rows],colWidths=widths,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),1,TEAL),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#dce5ec'))]))
 return t

def architecture():
 d=Drawing(510,124)
 names=[('INGEST','Hash snapshot'),('VALIDATE','Data gate'),('FEATURES','Fixed partitions'),('TRAIN','Fit on train only'),('EVALUATE','Quality + champion'),('REGISTER','MLflow version'),('DEPLOY','Atomic pointer'),('MONITOR','Drift + operations')]
 for i,(title,detail) in enumerate(names):
  row=i//4;col=i%4;x=col*129;y=76-row*63
  d.add(Rect(x,y,119,44,rx=6,ry=6,fillColor=PALE,strokeColor=TEAL,strokeWidth=.6))
  d.add(String(x+8,y+27,title,fontName='Helvetica-Bold',fontSize=9,fillColor=NAVY))
  d.add(String(x+8,y+12,detail,fontName='Helvetica',fontSize=7.4,fillColor=MUTED))
  if col<3:
   d.add(Line(x+119,y+22,x+128,y+22,strokeColor=TEAL))
   d.add(Polygon([x+128,y+22,x+125,y+24,x+125,y+20],fillColor=TEAL,strokeColor=TEAL))
 d.add(String(0,2,'Execution order: top row, then bottom row. Failed gates keep the existing serving model.',fontName='Helvetica',fontSize=8,fillColor=MUTED))
 return d

def build(path,story):
 doc=SimpleDocTemplate(str(path),pagesize=(595.28,841.89),leftMargin=42,rightMargin=42,topMargin=40,bottomMargin=53)
 doc.build(story,onFirstPage=footer,onLaterPages=footer)

story=[para('From raw listings<br/>to a monitored release','Hero'),para('Design note / Project 4<br/>Swagata Bhowmik (B053) and Sumit Kothari (B062)','Deck'),para('01 / Objective and measurable success','Section'),para('Predict property asking prices in INR lakhs for a real-estate analytics startup. Automate retraining and release while retaining the previous serving model whenever data or candidate quality is unacceptable. The supplied historical file has 4,000 listings; three later batches contain 500 labeled listings each.'),table([
 ['Criterion','Configured objective and justification'],
 ['Prediction quality','Validation MAE <=7 lakhs; RMSE <=9 lakhs. Initial Ridge results are 5.742 and 7.522; limits allow roughly 20% headroom while enforcing useful average error. These are project assumptions, not a client-signed SLA.'],
 ['Safe promotion','Candidate MAE <=1.02 x current-model MAE on the same validation rows; absolute limits must also pass. First deployment has no incumbent comparison.'],
 ['Operations','Warm p95 <=200 ms, request error fraction <=1%, model age <=30 days before a review alert. Network/container capacity still needs host verification.'],
 ['Reproduction','Fixed seed 42, exact dependency lock, source/data hashes and split membership; metric tolerance 1e-6. Fresh-clone execution remains pending.']
 ],[112,399]),para('02 / Architecture mapped to the lifecycle','Section'),architecture(),para('FastAPI serves predictions and exposes health, lineage and Prometheus metrics. MLflow records parameters/configuration, scores, source artifacts, model versions and lifecycle labels. Prometheus/Grafana support operational observation; an HTML/JSON report covers the three labeled batches. The serving API reads model storage without write permission in Compose.'),para('Tool decisions','Section'),para('A small persisted Python DAG substitutes for Prefect/ZenML: explicit dependencies, stage artifacts, reruns, hash verification, failure records and MLflow history. This keeps the local demonstration auditable; it is not a distributed scheduler. Git-tracked CSVs plus hashes/run snapshots replace DVC for the small supplied files. SciPy/pandas effect-size monitoring replaces Evidently. The brief permits justified equivalent free tools.'),PageBreak(),para('Gates, releases<br/>and evidence','Hero'),para('03 / Data and evaluation protocol','Section'),para('One validated YAML defines paths, features, model settings and policy thresholds. Data gates require the declared schema, unique IDs, valid categories, plausible numeric ranges, >=100 rows and <=8% missingness per column. Only age, distance and neighborhood score may be missing; observed missingness is 4%. IDs and Batch never enter the feature matrix.'),para('Historical split: 2,400 train / 800 validation / 800 final test, seed 42. Fit numeric imputation/scaling and categorical encoding only on training rows. Select Ridge by validation MAE, then evaluate the reserved test once. Its measured MAE is 5.775 lakhs and RMSE 7.506. Earlier whole-file summaries included test rows; prediction-error selection did not. Incoming batches are monitoring data, not training input.'),para('04 / Release safety and traceability','Section'),para('Each stage persists its inputs/outputs and status. Rerunning an upstream stage invalidates descendants; artifact hashes prevent stale gate reuse. Promotion requires unchanged evaluated model bytes and unchanged incumbent version, then a finite-prediction check. A filesystem lock serializes updates. The pipeline copies an immutable model release and atomically switches production.json. Failed gates never change it.'),para('MLflow uses validated/production/archived lifecycle tags and a champion alias, replacing deprecated stages. The API follows the serving manifest and retains a cached healthy model when replacement loading fails. Lineage links model hash, registry version, run ID, configuration, data hash and source snapshot; CI supplies a real commit ID once Git is enabled. Alias and file updates are not one transaction: an interrupted promotion requires reconciliation.'),para('05 / Monitoring and response','Section'),table([
 ['Signal','Trigger / response'],
 ['Input distribution','KS D >0.10 for numeric features; total variation >0.10 for categories; missing-rate change >3 percentage points. Investigate changes and schedule a candidate through all gates.'],
 ['Labeled performance','MAE >7 lakhs or >1.25 x validation MAE. Batch 1: 5.562, no alert. Batch 2: 6.867, area alert only. Batch 3: 13.113, input and performance alerts. Retain current model until a candidate passes.'],
 ['Service health','Observe latency, throughput, HTTP errors, predicted-price histogram, model age and load failures. Prometheus rules expose local alerts; outbound notifications are not configured.']
 ],[112,399]),para('06 / CI/CD, delivery status and limits','Section'),para('PR workflow runs tests and a lightweight pipeline. Main-branch workflow tests, smoke-checks a container, publishes a commit-tagged image and creates a release. Persistent deployment uses an opt-in self-hosted Docker runner. Model rollback was executed and verified. GitHub history, container execution/rollback, UI screenshots and the team recording remain external steps: no Git access, Docker runtime or server socket permission is available here.'),para('Reference: MLflow Model Registry Workflows, https://www.mlflow.org/docs/latest/ml/model-registry/workflow/ . Full operational procedures and evidence: README.md, docs/OPERATIONS.md, reports/.','SmallText')]
build(OUT/'design_note.pdf',story)
reflection=[para('What we would improve<br/>with more time','Hero'),para('Project reflection / Group 4 / One-page technical draft','Deck'),para('The strongest result','Section'),para('The useful outcome is a repeatable release decision with evidence. Ridge beat the larger baseline models on validation data and achieved a final historical test MAE of 5.775 lakhs. Two deliberately invalid update scenarios preserved the existing model and prediction, and a second valid release was rolled back successfully. This gives the accuracy result operational context.'),para('What the batches revealed','Section'),para('Batch 2 shifts toward smaller properties without crossing the configured MAE alert. Batch 3 changes both the property mix and prediction error: MAE rises to 13.113 lakhs. This illustrates why valid ranges and stable missingness do not imply stable model behavior, and why input drift must be separated from labeled performance drift. Thresholds were designed after exploratory inspection, so these batches are a demonstration rather than a blind validation of the monitoring policy.'),para('The next engineering priorities','Section'),para('<b>1. Verify the release environment.</b> Run the clean install, actual Docker deployment, GitHub checks and image rollback on an unrestricted host. Benchmark real HTTP traffic with cold starts, concurrent requests and sustained load. The current in-process timing does not establish production capacity.'),para('<b>2. Strengthen transactional deployment.</b> Replace the local pointer/alias coordination with a durable promotion journal and crash recovery; add health-checked blue/green serving, authenticated operations and a shared locking strategy. Keep the current explicit gates and model provenance.'),para('<b>3. Improve monitoring calibration.</b> Calibrate effect thresholds on repeated reference samples, study false-alert rates and seasonal patterns, and report uncertainty. Add subgroup errors and minimum sample sizes. Connect alert delivery to an acknowledged incident workflow.'),para('<b>4. Improve data and model governance.</b> Obtain dated listings for time-based evaluation, document data origin and labeling delay, track approved retraining datasets, and use an untouched prospective evaluation window. Extend reproducibility across operating systems before promising tight numerical tolerance.'),para('Scope and learning','Section'),para('A lightweight local workflow is easy to inspect but does not provide distributed scheduling, high availability or multi-user security. The final delivery must distinguish real local evidence from prepared infrastructure and missing account-dependent evidence. Both team members should review this draft, explain the tradeoffs in their own words, make genuine contributions, and practice a live modification before presenting.')]
build(OUT/'reflection.pdf',reflection)
print('Created design_note.pdf and reflection.pdf')
