"""
Academic Project Report DOCX Generator.
Compiles the comprehensive B.Tech CSE Project Report into a native Microsoft Word (.docx) document.
Run: pip install python-docx
     python project_report/generate_docx.py
"""

import os
import sys

try:
    import docx
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
except ImportError:
    print("Notice: 'python-docx' library is not yet installed in this environment.")
    print("To generate the native .docx file, run:")
    print("    pip install python-docx")
    print("    python project_report/generate_docx.py")
    print("\nIn the meantime, an editable Word document 'Academic_Project_Report.doc' and a print-ready 'Academic_Project_Report.html' have already been generated in this directory and can be opened directly in Microsoft Word and web browsers!")
    sys.exit(0)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def generate_report():
    doc = docx.Document()
    
    # Configure 1-inch margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Title Page
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("ACADEMIA–INDUSTRY SKILL MAPPING AND PLACEMENT PORTAL\n")
    run_title.bold = True
    run_title.font.size = Pt(20)
    run_title.font.color.rgb = RGBColor(12, 74, 110)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("A Capstone Project Report Submitted in Partial Fulfillment of the Requirements for the Degree of\nBachelor of Technology in Computer Science and Engineering\n\n")
    r_sub.font.size = Pt(13)
    r_sub.font.italic = True

    p_by = doc.add_paragraph()
    p_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_by = p_by.add_run("Submitted by:\nShivam Chandel (Reg. No.: 12522547 | Roll No.: RK3P25ORA20)\nNayneet Kumar (Reg. No.: 12518540 | Roll No.: RK3P25ORB37)\n\nGroup Number: G29 · Academic Year: 2025–2026\n\n")
    r_by.font.size = Pt(12)
    r_by.bold = True

    p_guide = doc.add_paragraph()
    p_guide.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_guide = p_guide.add_run("Under the Guidance of:\n[Guide Name Placeholder]\nAssistant Professor, Department of Computer Science & Engineering\n\n")
    r_guide.font.size = Pt(11)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("Department of Computer Science and Engineering\nSchool of Computer Science and Engineering\nLovely Professional University, Phagwara, Punjab, India\nIn Association With: Smart India Hackathon 2026 · Problem ID: SIH26044 (Ministry of Ayush)")
    r_inst.font.size = Pt(12)
    r_inst.bold = True

    doc.add_page_break()

    # Certificate
    h_cert = doc.add_heading("CERTIFICATE", level=1)
    p_cert = doc.add_paragraph(
        "This is to certify that the capstone project entitled \"Academia–Industry Skill Mapping and Placement Portal\", "
        "submitted by Shivam Chandel (Reg. No. 12522547 / Roll No. RK3P25ORA20) and Nayneet Kumar (Reg. No. 12518540 / Roll No. RK3P25ORB37) "
        "of Group G29, in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Computer Science and Engineering "
        "from Lovely Professional University, is a bona fide record of work carried out by them under my supervision and guidance."
    )
    p_cert.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_paragraph("\n\n___________________________________\t\t___________________________________")
    doc.add_paragraph("[Guide Name Placeholder]\t\t\t\t[Head of Department Placeholder]\nProject Supervisor, Assistant Professor\t\t\tHead of Department, School of CSE\nLovely Professional University\t\t\t\tLovely Professional University\n\n")
    doc.add_paragraph("___________________________________\n[External Examiner Placeholder]\nExternal Examiner")

    doc.add_page_break()

    # Declaration
    doc.add_heading("DECLARATION", level=1)
    doc.add_paragraph(
        "We, Shivam Chandel (Reg. No. 12522547, Roll No. RK3P25ORA20) and Nayneet Kumar (Reg. No. 12518540, Roll No. RK3P25ORB37), "
        "students of Bachelor of Technology in Computer Science and Engineering at Lovely Professional University, hereby declare that the capstone project report entitled "
        "\"Academia–Industry Skill Mapping and Placement Portal\" is an authentic record of our original work.\n\n"
        "We have adhered to academic ethics and have not copied or fabricated any test results, model accuracy metrics, or survey outputs. "
        "All sources of information and literature reviewed have been duly cited and acknowledged.\n\n"
        "This work was developed for the Smart India Hackathon 2026 under Problem Statement ID: SIH26044 (\"Portal for Academia–Industry Collaboration for Skill Mapping, Internships and Placement\"), "
        "listed under the Ministry of Ayush.\n\n"
        "Date: 20th October 2026\nPlace: Phagwara, Punjab\n\n\n"
        "___________________________________\t\t___________________________________\n"
        "Shivam Chandel\t\t\t\t\tNayneet Kumar\n"
        "Reg. No.: 12522547\t\t\t\tReg. No.: 12518540\n"
        "Roll No.: RK3P25ORA20\t\t\t\tRoll No.: RK3P25ORB37"
    )

    doc.add_page_break()

    # Abstract
    doc.add_heading("ABSTRACT", level=1)
    doc.add_paragraph(
        "The rapid evolution of industrial technologies has widened the structural gap between university curricula and contemporary job role expectations. "
        "Graduating students often struggle to identify the exact technical competencies demanded by employers, while institutions lack automated visibility into curriculum deficiencies, "
        "and placement officers face substantial friction in assessing cohort-wide placement readiness.\n\n"
        "To resolve these challenges, this project presents the Academia–Industry Skill Mapping and Placement Portal, an intelligent full-stack software system developed for "
        "Smart India Hackathon 2026 (Problem Statement ID: SIH26044). The system is architected as a modular 4-tier platform comprising a Presentation Layer (React.js, Tailwind CSS, Vite), "
        "an Application Layer (Python FastAPI REST APIs), a Skill Intelligence Layer (contextual token-boundary Natural Language Processing, canonical synonym taxonomy normalization, and TF-IDF cosine semantic matching), "
        "and a Data Layer (relational PostgreSQL/SQLAlchemy database with 16 entity tables).\n\n"
        "The platform introduces a strict operational separation between academic curriculum coverage (what is taught) and verified student competency (what an individual student can demonstrate through coursework, projects, and certifications). "
        "It calculates placement readiness using both unweighted and importance-weighted coverage formulas (wi in [1, 5], ci in {1.0, 0.5, 0.0}). For missing competencies, the engine generates prioritized, gap-targeted learning pathways linking students to verified educational resources across NPTEL, Coursera, edX, and FreeCodeCamp.\n\n"
        "To evaluate system efficacy without fabricated claims, an empirical benchmark suite was executed on a manually validated ground-truth dataset comprising authentic university syllabi and industry job descriptions. "
        "The proposed contextual NLP pipeline achieved a Precision of 0.9630 (96.3%), Recall of 0.8667 (86.7%), and an F1 Score of 0.9123 (91.2%), significantly outperforming a naive keyword-matching baseline which scored an F1 of 0.7059 (70.6%), representing a +20.6% absolute F1 performance gain. "
        "The platform also features role-based access control (RBAC) across five user roles, interactive shortage heatmaps, audit logging, and downloadable CSV/PDF placement readiness reports.\n\n"
        "Keywords: Academia–Industry Skill Mapping, Natural Language Processing (NLP), Skill-Gap Analysis, Weighted Coverage Metric, Placement Readiness, Smart India Hackathon 2026, FastAPI, React.js."
    )

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Academic_Project_Report.docx")
    doc.save(output_path)
    print(f"Successfully generated native Word report at: {output_path}")

if __name__ == "__main__":
    generate_report()
