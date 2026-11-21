# Academia–Industry Skill Mapping & Placement Portal
## System Architecture & Technical Diagrams
**Smart India Hackathon 2026 · Group G29**
- **Problem Statement ID:** SIH26044
- **Team Members:** Shivam Chandel (12522547) & Nayneet Kumar (12518540)

---

## 1. 4-Tier System Architecture Diagram

```
+----------------------------------------------------------------------------------------------------+
|                                         PRESENTATION LAYER                                         |
|                                    React 18 + Tailwind CSS + Vite                                  |
|  +--------------------+  +--------------------+  +---------------------+  +----------------------+ |
|  | Student Dashboard  |  | Faculty Dashboard  |  | Placement Dashboard |  | Employer / Partner   | |
|  | - Role Selection   |  | - Syllabus Upload  |  | - Readiness Tiers   |  | - JD Upload & Weight | |
|  | - Gap Gauges (w_i) |  | - Extraction Audit |  | - Shortage Heatmap  |  | - Skill Requirements| |
|  | - Ranked Pathways  |  | - Curriculum Matrix|  | - CSV/PDF Export    |  |                      | |
|  +--------------------+  +--------------------+  +---------------------+  +----------------------+ |
|  +--------------------------------------------+  +-----------------------------------------------+ |
|  | Skill-Mapping Workspace                    |  | Model Evaluation Lab & Admin Governance       | |
|  | - Dual-Pane Curriculum vs Industry Compare  |  | - Precision/Recall/F1 vs Baseline Comparator  | |
|  | - Exact & Semantic Match Linkages          |  | - Inspectable Error Samples & Audit Trail     | |
|  +--------------------------------------------+  +-----------------------------------------------+ |
+-------------------------------------------------+--------------------------------------------------+
                                                  | JSON / JWT REST APIs (HTTP / HTTPS)
+-------------------------------------------------v--------------------------------------------------+
|                                          APPLICATION LAYER                                         |
|                               Python FastAPI (REST API Service & Routers)                          |
|  +--------------------+  +--------------------+  +---------------------+  +----------------------+ |
|  | /api/v1/auth       |  | /api/v1/curriculum |  | /api/v1/jobs        |  | /api/v1/mapping      | |
|  | - JWT Tokens / RBAC|  | - Syllabi Ingestion|  | - JD Parser & Weight|  | - Exact & Semantic   | |
|  | - Password Hashing |  | - Course Registry  |  | - Experience Levels |  | - Coverage Stats     | |
|  +--------------------+  +--------------------+  +---------------------+  +----------------------+ |
|  +--------------------+  +--------------------+  +---------------------+  +----------------------+ |
|  | /api/v1/gap-analysis|  | /recommendations   |  | /api/v1/analytics   |  | /evaluation & admin  | |
|  | - Weighted Coverage|  | - Gap-Targeted Rank|  | - Cohort Aggregation|  | - Benchmark Runner   | |
|  | - Demonstrated Evi |  | - Resource Catalog |  | - Streaming CSV Exp |  | - Audit Log Store    | |
|  +--------------------+  +--------------------+  +---------------------+  +----------------------+ |
+------------------------+---------------------------------+-----------------------------------------+
                         |                                 |
+------------------------v---------------+  +--------------v-----------------------------------------+
|        SKILL INTELLIGENCE LAYER        |  |                       DATA LAYER                       |
|  - Text Preprocessing & Cleaning       |  | Relational Database (PostgreSQL / SQLite Engine)       |
|  - Word Boundary Regex & Token Matcher |  |  1. users               9. job_skills                  |
|  - Canonical Taxonomy Normalization    |  |  2. students           10. student_skills              |
|  - TF-IDF Vector & Cosine Similarity   |  |  3. cohorts            11. skill_mappings              |
|  - Weighted Scoring Engine (wi · ci)   |  |  4. courses            12. learning_resources          |
|  - Empirical Benchmark Suite (P, R, F1)|  |  5. curriculum_content 13. recommendations             |
|  - Naive Keyword Baseline Comparator   |  |  6. skills             14. gap_results                 |
|                                        |  |  7. course_skills      15. evaluation_records          |
|                                        |  |  8. job_roles          16. audit_logs                  |
+----------------------------------------+  +--------------------------------------------------------+
```

---

## 2. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o{ STUDENTS : "profile"
    USERS ||--o{ AUDIT_LOGS : "triggers"
    COHORTS ||--o{ STUDENTS : "enrolls"
    COHORTS ||--o{ COURSES : "contains"
    COURSES ||--|| CURRICULUM_CONTENT : "syllabus"
    COURSES ||--o{ COURSE_SKILLS : "teaches"
    SKILLS ||--o{ COURSE_SKILLS : "categorized"
    SKILLS ||--o{ JOB_SKILLS : "required"
    JOB_ROLES ||--o{ JOB_SKILLS : "specifies"
    STUDENTS ||--o{ STUDENT_SKILLS : "demonstrates"
    SKILLS ||--o{ STUDENT_SKILLS : "mastered"
    COURSES ||--o{ SKILL_MAPPINGS : "maps"
    JOB_SKILLS ||--o{ SKILL_MAPPINGS : "targeted"
    SKILLS ||--o{ LEARNING_RESOURCES : "addresses"
    STUDENTS ||--o{ RECOMMENDATIONS : "receives"
    LEARNING_RESOURCES ||--o{ RECOMMENDATIONS : "links"
    STUDENTS ||--o{ GAP_RESULTS : "analyzed"
    JOB_ROLES ||--o{ GAP_RESULTS : "benchmarked"
```

---

## 3. Use Case Diagram

```mermaid
flowchart LR
    subgraph Actors
        S["Student"]
        F["Faculty Member"]
        P["Placement Officer"]
        E["Industry Partner / Employer"]
        A["Administrator"]
    end

    subgraph Portal_Use_Cases ["Academia–Industry Skill Mapping Portal"]
        UC01["UC-01: Log In & RBAC Auth"]
        UC02["UC-02: Upload Course Syllabus"]
        UC03["UC-03: Post Job Description & Skill Weights"]
        UC04["UC-04: Map Academia to Industry Skills"]
        UC05["UC-05: Analyze Student Skill Gap (w_i · c_i)"]
        UC06["UC-06: Get Ranked Recommendations"]
        UC07["UC-07: View Cohort Analytics & Export CSV"]
        UC08["UC-08: Run Live Model Benchmark (P, R, F1)"]
        UC09["UC-09: Manage Users, Taxonomy & Audit Logs"]
    end

    S --> UC01
    S --> UC05
    S --> UC06

    F --> UC01
    F --> UC02
    F --> UC04

    P --> UC01
    P --> UC04
    P --> UC05
    P --> UC07

    E --> UC01
    E --> UC03

    A --> UC01
    A --> UC08
    A --> UC09
```

---

## 4. Data Flow Diagrams (DFD)

### DFD Level 0: Context Diagram

```mermaid
flowchart TD
    Student(["Student"])
    Faculty(["Faculty Member"])
    Placement(["Placement Officer"])
    Employer(["Employer / Partner"])
    Admin(["Administrator"])

    Portal[["Academia–Industry Skill Mapping & Placement Portal"]]

    Faculty -- "Course Syllabi & Outcomes" --> Portal
    Portal -- "Extracted Skills for Review" --> Faculty

    Employer -- "Job Descriptions & Skill Weights (w_i)" --> Portal
    Portal -- "Curriculum Alignment Analytics" --> Employer

    Student -- "Target Role Selection & Skill Evidence" --> Portal
    Portal -- "Skill Gaps, Coverage % & Ranked Recommendations" --> Student

    Placement -- "Cohort Query Parameters" --> Portal
    Portal -- "Placement Readiness Reports & Shortage Heatmaps" --> Placement

    Admin -- "Benchmark Execution & Role Updates" --> Portal
    Portal -- "Evaluation Metrics (P, R, F1) & Audit Logs" --> Admin
```

### DFD Level 1: System Decomposition

```mermaid
flowchart TD
    D1[(Curriculum Content Store)]
    D2[(Normalized Skills Taxonomy)]
    D3[(Job Roles & Requirements)]
    D4[(Student Evidence Store)]
    D5[(Gap & Recommendation Store)]

    P1["1.0 Curriculum Ingestion & NLP Extraction"]
    P2["2.0 Job Description Ingestion & Weighting"]
    P3["3.0 Academia-Industry Mapping Engine"]
    P4["4.0 Student Gap Analysis (Formula Calculator)"]
    P5["5.0 Learning Recommendation Ranker"]
    P6["6.0 Cohort Aggregation & CSV Export"]

    FacultyRaw["Faculty Syllabus"] --> P1
    P1 --> D1
    P1 <--> D2

    EmployerRaw["Job Description"] --> P2
    P2 --> D3
    P2 <--> D2

    D1 & D3 --> P3
    P3 --> MappingOutput["Curriculum Coverage Metrics"]

    D3 & D4 --> P4
    P4 --> D5
    P4 --> GapOutput["Coverage %, Gaps, Demonstrated Skills"]

    D5 & D2 --> P5
    P5 --> RecOutput["Ranked Pathways with Verified Links"]

    D5 --> P6
    P6 --> ReportOutput["Cohort Distribution & Downloadable CSV"]
```

---

## 5. Skill Extraction & Semantic Mapping Flowchart

```mermaid
flowchart TD
    InputText["Raw Syllabus / Job Description Text"] --> Clean["Text Preprocessing & Normalization"]
    Clean --> RegexNER["Multi-Token Word-Boundary Regex Matcher"]
    RegexNER --> TaxonLookup["Canonical Taxonomy & Alias Dictionary Lookup"]
    TaxonLookup --> SnippetExtract["Context Snippet & Confidence Scoring"]
    SnippetExtract --> HumanReview{"Human-in-the-Loop Review (Faculty / Placement)?"}
    HumanReview -- "Approved" --> ApprovedStore[("Verified Skills Store")]
    HumanReview -- "Adjusted (0.5 / 1.0)" --> ApprovedStore
    HumanReview -- "Rejected" --> Discard["Discard / Log in Error Analysis"]

    ApprovedStore --> SemanticMatcher["Semantic Similarity Matcher (TF-IDF Cosine Sim)"]
    SemanticMatcher --> CheckExact{"Exact Name Match?"}
    CheckExact -- "Yes" --> ExactMatch["Exact Match (Confidence = 1.0)"]
    CheckExact -- "No" --> CheckSim{"Cosine Similarity >= 0.50?"}
    CheckSim -- "Yes" --> RelatedMatch["Related Match (Confidence = Sim, Coverage = 0.5)"]
    CheckSim -- "No" --> Unmapped["Unmapped Requirement (Coverage = 0.0)"]
```

---

## 6. Student Skill-Gap Analysis Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Student as Student User
    participant UI as React Frontend
    participant API as FastAPI Gap Router
    participant Engine as SkillGapAnalyzer Engine
    participant DB as Relational Database
    participant Recs as Recommendation Ranker

    Student->>UI: Selects Target Job Role ("Full Stack Engineer")
    UI->>API: POST /api/v1/gap-analysis/student/analyze
    API->>DB: Query Job Skills with Weights (w_i in [1, 5])
    API->>DB: Query Student Verified Skill Evidence
    API->>Engine: analyze_student_gap(job_skills, student_skills)
    
    Note over Engine: Calculate Unweighted Coverage: (Covered / Total) * 100<br/>Calculate Weighted Coverage: Sum(w_i * c_i) / Sum(w_i) * 100<br/>where c_i in {1.0, 0.5, 0.0}

    Engine-->>API: Returns {weighted_coverage, demonstrated, partial, missing}
    API->>DB: Upsert into gap_results table
    API->>Recs: rank_recommendations(gap_analysis, catalog_resources)
    Recs-->>API: Ranked courses addressing missing skills
    API-->>UI: Complete JSON Payload
    UI-->>Student: Displays Radial Gauges, Categorized Cards & Recommendations
```
