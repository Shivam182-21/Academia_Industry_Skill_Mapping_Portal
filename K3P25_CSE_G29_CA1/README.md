# Academia–Industry Skill Mapping and Placement Portal (Group G29)

**Smart India Hackathon 2026** · Problem Statement ID: **SIH26044** (Ministry of Ayush)  
**Institution:** Lovely Professional University, Punjab  
**Course:** CSE498 – Capstone Project & AI Systems  
**Section:** RK3P25 (K3P25LH) | **Group Number:** G29  

## Group Members
1. **Shivam Chandel** (Project Lead) · Reg No: **12522547** · Roll No: **RK3P25ORA20**
2. **Nayneet Kumar** (Research & Data) · Reg No: **12518540** · Roll No: **RK3P25ORB37**

---

## 1. Project Overview
The **Academia–Industry Skill Mapping and Placement Portal** is an intelligent full-stack software application engineered to bridge the widening gap between higher education course syllabi and dynamic corporate recruitment prerequisites.

### Key Capabilities
- **Automated Skill Extraction & Normalization:** Parses unstructured course syllabi and employer job postings, mapping variations into standardized technical competencies using boundary-aware regex patterns and canonical taxonomy linking.
- **Bloom-Weighted Gap Engine:** Computes unweighted coverage and weighted placement readiness indices scaled by Bloom's Taxonomy cognitive depths (Levels 1–6).
- **Five Stakeholder Dashboards:** Dedicated interactive portals for Students, Faculty, Placement Officers, Recruiters, and Administrators.
- **Curated Remediation:** Recommends targeted learning pathways and practice resources for missing technical skills.

---

## 2. Empirical Benchmark Evaluation
Evaluated on a ground-truth dataset of 6 multi-page curriculum and recruitment documents containing 30 verified technical skills:

| Model / Pipeline | Precision | Recall | F1-Score | Mapping Precision | Gap Coverage |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline: Naive Keyword Matching** | 0.8571 | 0.6000 | 0.7059 | 0.7600 | 0.7500 |
| **Proposed: Rule-Enhanced NLP Pipeline** | **0.9630** | **0.8667** | **0.9123** | **0.9400** | **0.9200** |
| **Improvement (Absolute Gain)** | **+10.59%** | **+26.67%** | **+20.64%** | **+18.00%** | **+17.00%** |

---

## 3. Pre-configured Evaluator Credentials
| Role | Email Address | Password | Functionality |
| :--- | :--- | :--- | :--- |
| **Student** | `chandels0708@gmail.com` | `student123` | Radial readiness gauge, missing skill gaps, learning links |
| **Faculty** | `faculty@portal.edu` | `faculty123` | Syllabus extraction, Bloom's review, CO attainment |
| **Placement** | `placement@portal.edu` | `placement123` | Cohort distribution analytics, CSV export |
| **Employer** | `partner@techcorp.com` | `partner123` | Job description upload, candidate screening |
| **Admin** | `admin@portal.edu` | `admin123` | Audit event logs, system telemetry, database health |

---

## 4. How to Run the Application

### Option A: Instant Zero-Dependency Standalone Mode
Double-click `app/index.html` or `app/portal.html` in any web browser. The entire application runs offline with pre-seeded demonstration data, interactive radial gauges, and instant one-click login.

### Option B: Local Client-Server Setup
1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Start Backend Server:**
   ```bash
   python backend/run.py
   # FastAPI Swagger docs at: http://127.0.0.1:8000/docs
   ```
3. **Launch Frontend:**
   ```bash
   cd frontend && npm install && npm run dev
   # Open http://localhost:5173
   ```

---

## 5. Submission Folder Tree
```
K3P25_CSE_G29_CA1/
|-- README.md          how to install and run, dataset link, group members
|-- requirements.txt   Python packages with versions
|-- data/              curriculum and job description benchmark dataset
|-- notebooks/         EDA and experiment notebooks (.ipynb)
|-- src/               preprocessing, baseline, rule-enhanced NLP model, evaluator
|-- app/               interactive web portal application
|-- results/           saved evaluation metrics, benchmark comparison tables
|-- report/            official CA-1 report PDF & editable DOCX
`-- presentation/      official presentation slide deck (PPTX & HTML)
```
