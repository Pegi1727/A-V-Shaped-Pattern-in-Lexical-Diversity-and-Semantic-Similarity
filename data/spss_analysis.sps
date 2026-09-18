* SPSS Replication Analysis: V-shaped trajectories (N = 30).
* Data: data/vshape_30_clean_long.csv (long format, 90 rows).
* Run from File > Open > Syntax, then Run > All.
* Adjust /FILE below to the absolute path of the CSV if not running from repo root.

PRESERVE.
SET DECIMAL=DOT.

GET DATA /TYPE=TXT
  /FILE="data/vshape_30_clean_long.csv"
  /ENCODING='UTF8'
  /DELIMITERS=","
  /QUALIFIER='"'
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /VARIABLES=
    Participant_ID A6
    Country A20
    Discipline A20
    Stage A20
    MTLD F8.3
    MLU F8.3
    Cohesion_Score F8.3
    SBERT_Similarity F8.3.

DATASET NAME long.

* ---------- Descriptives by stage ----------.
SORT CASES BY Stage.
SPLIT FILE LAYERED BY Stage.
DESCRIPTIVES VARIABLES=MTLD MLU Cohesion_Score SBERT_Similarity
  /STATISTICS=MEAN STDDEV MIN MAX.
SPLIT FILE OFF.

* ---------- Reshape to wide: one row per participant ----------.
SORT CASES BY Participant_ID Stage.
CASESTOVARS
  /ID=Participant_ID
  /INDEX=Stage
  /GROUPBY=VARIABLE.
DATASET NAME wide.

* ---------- GLM repeated measures per metric ----------.
* The Polynomial within-subjects contrast includes the QUADRATIC term, which
* tests the V-shaped hypothesis. See the "Tests of Within-Subjects Contrasts"
* table (Quadratic row) for each metric.

GLM MTLD.Original MTLD.AI_Revised MTLD.Author_Refined
  /WSFACTOR=Stage 3 Polynomial
  /EMMEANS=TABLES(Stage) COMPARE ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE ETASQ.

GLM MLU.Original MLU.AI_Revised MLU.Author_Refined
  /WSFACTOR=Stage 3 Polynomial
  /EMMEANS=TABLES(Stage) COMPARE ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE ETASQ.

GLM Cohesion_Score.Original Cohesion_Score.AI_Revised Cohesion_Score.Author_Refined
  /WSFACTOR=Stage 3 Polynomial
  /EMMEANS=TABLES(Stage) COMPARE ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE ETASQ.

GLM SBERT_Similarity.Original SBERT_Similarity.AI_Revised SBERT_Similarity.Author_Refined
  /WSFACTOR=Stage 3 Polynomial
  /EMMEANS=TABLES(Stage) COMPARE ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE ETASQ.

* ---------- Nonparametric alternative: Friedman test ----------.
NPAR TESTS
  /FRIEDMAN = MTLD.Original MTLD.AI_Revised MTLD.Author_Refined
  /FRIEDMAN = MLU.Original MLU.AI_Revised MLU.Author_Refined
  /FRIEDMAN = Cohesion_Score.Original Cohesion_Score.AI_Revised Cohesion_Score.Author_Refined
  /FRIEDMAN = SBERT_Similarity.Original SBERT_Similarity.AI_Revised SBERT_Similarity.Author_Refined
  /MISSING LISTWISE.

RESTORE.
