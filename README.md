# Academia–Industry Skill Mapping and Placement Portal
### Smart India Hackathon 2026 · Problem Statement ID: SIH26044 · Group G29

---

### Team Information
- **Shivam Chandel** (Roll No.: RK3P25ORA20 · Reg. No.: 12522547)
- **Navneet Kumar** (Roll No.: RK3P25ORB37 · Reg. No.: 12518540)
- **Section:** K3P25OR
- **Group:** G29
- **Organization / Ministry:** Ministry of Ayush / Smart India Hackathon 2026

---

## 1. Problem Statement & Objectives
Students struggle to identify the exact skills required for their target industry roles, while employers face significant hurdles finding candidates with proven competencies. Academic institutions lack automated, real-time insights into where their curriculum diverges from market demands.

This portal establishes an end-to-end intelligence platform that:
1. **Extracts technical skills** from university course syllabi and industry job descriptions using NLP and canonical taxonomy normalization.
2. **Maps academia to industry** identifying exact matches, semantic related matches, and unmet requirements with confidence scores.
3. **Computes student placement readiness** using both unweighted and importance-weighted coverage formulas ($w_i \in [1, 5], c_i \in \{1.0, 0.5, 0.0\}$).
4. **Delivers ranked learning recommendations** connecting students directly to verified courses addressing their specific gaps.
5. **Provides cohort-level analytics** for faculty and placement officers with aggregate skill shortage heatmaps and downloadable CSV reports.
6. **Evaluates model performance empirically** reporting Precision, Recall, and F1 score against a labeled ground-truth benchmark and comparing them directly with a naive keyword baseline.

---

## 2. Technology Stack

- **Backend:** Python FastAPI, Pydantic, SQLAlchemy, Uvicorn, Python-Jose (JWT), Passlib (Bcrypt).
- **Database:** Relational schema (PostgreSQL ready, SQLite default out-of-the-box for instant zero-config evaluation).
- **Skill Intelligence / NLP:** Contextual token boundary regex matcher, canonical taxonomy normalizer, TF-IDF cosine similarity embedder, empirical model evaluation suite.
- **Frontend:** React 18, Tailwind CSS, Lucide Icons, SVG circular gauges, Vite build tool.
- **Testing:** Pytest, HTTPX, FastAPI TestClient (TC-01 through TC-12 automated test suite).

---

## 3. Quick Start & Execution

### Prerequisites
- Python 3.9+ installed
- Node.js 18+ and npm installed

### 3.1 Backend Setup & Execution
1. Open a terminal in the project directory:
```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server (starts on http://127.0.0.1:8000)
python run.py
```
> [!NOTE]
> On startup, the backend automatically creates all 16 database tables and seeds rich demonstration data (students, courses, job roles, learning resources, and benchmark metrics).

- **Interactive API Documentation (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc UI:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 3.2 Frontend Setup & Execution
1. Open a second terminal in the project directory:
```bash
# Navigate to frontend
cd frontend

# Install frontend dependencies
npm install

# Start Vite development server (starts on http://localhost:5173)
npm run dev
```
2. Open your browser to [http://localhost:5173](http://localhost:5173).

---

## 4. Evaluator Demo Credentials (All 5 Roles)

The login screen features **one-click evaluator access cards** for instant testing:

| Role | Name | Email | Password | Primary Capabilities in Portal |
| :--- | :--- | :--- | :--- | :--- |
| **Student (Team Lead)** | Shivam Chandel | `shivam.student@portal.edu` | `student123` | Target role selector, radial gauges, demonstrated vs missing skills, ranked recommendations, submit skill evidence. |
| **Student (Team Member)** | Navneet Kumar | `nayneet.student@portal.edu` | `student123` | Machine learning & Ayush health informatics student profile. |
| **Faculty Member** | Dr. Rajesh Sharma | `faculty@portal.edu` | `faculty123` | Upload syllabus text, trigger NLP skill extraction, review/approve skills ($1.0$ vs $0.5$). |
| **Placement Officer** | Prof. Sunita Verma | `placement@portal.edu` | `placement123` | Cohort readiness tiers, aggregate shortage heatmap, export placement reports (CSV). |
| **Industry Partner** | TechCorp Recruiter | `partner@techcorp.com` | `partner123` | Upload job descriptions, adjust skill importance weights ($w_i$), configure required proficiency. |
| **System Administrator** | System Admin | `admin@portal.edu` | `admin123` | User governance, audit logs (FR-08), run live model evaluation benchmark (FR-09). |

---

## 5. Functional Verification (TC-01 to TC-12)

Run the automated backend test suite:
```bash
pytest backend/tests/ -v
```

All 12 test scenarios from the SRS pass:
- **TC-01:** Valid login authentication and JWT token issuance.
- **TC-02:** Denial of invalid credentials with 401 error.
- **TC-03:** Course listing and syllabus extraction verification.
- **TC-04 & TC-05:** Job role and requirement ingestion.
- **TC-06:** Academia-industry exact and semantic skill mapping.
- **TC-07 & TC-08:** Student skill-gap analysis with unweighted and weighted formulas and ranked recommendations.
- **TC-09:** Cohort placement readiness distribution and shortage heatmaps.
- **TC-10:** Exporting downloadable placement report (CSV).
- **TC-11:** Role-based access control protecting restricted administrative endpoints.
- **TC-12:** Empirical model evaluation measuring Precision, Recall, and F1 against keyword baseline.

---

## 6. Project Architecture & Diagrams
For detailed architecture flowcharts, ER diagrams, Use Case diagrams, and DFDs, see:
- [docs/architecture_diagrams.md](file:///c:/Users/Shivam/OneDrive/Desktop/Documents/Academia_Industry_Skill_Mapping_Portal/docs/architecture_diagrams.md)
- [docs/SRS.md](file:///c:/Users/Shivam/OneDrive/Desktop/Documents/Academia_Industry_Skill_Mapping_Portal/docs/SRS.md)
