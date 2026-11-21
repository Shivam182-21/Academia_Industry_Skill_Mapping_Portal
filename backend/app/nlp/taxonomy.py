"""
Canonical Skill Taxonomy and Synonym Mappings for Academia-Industry Mapping.
Defines normalized skill representations, categories, and recognized alias tokens.
"""

CANONICAL_SKILLS = [
    {
        "canonical_name": "Python",
        "category": "Programming Languages",
        "aliases": ["python", "python3", "python 3", "py"],
        "description": "High-level programming language widely used in backend, data science, and automation."
    },
    {
        "canonical_name": "JavaScript",
        "category": "Programming Languages",
        "aliases": ["javascript", "js", "ecmascript", "es6", "es2020"],
        "description": "Dynamic web programming language used across frontend and backend application stacks."
    },
    {
        "canonical_name": "SQL & Relational Databases",
        "category": "Databases & Storage",
        "aliases": ["sql", "rdbms", "relational database", "mysql", "postgresql", "postgres", "sqlite"],
        "description": "Structured Query Language for querying and managing relational databases."
    },
    {
        "canonical_name": "Data Structures & Algorithms",
        "category": "Computer Science Core",
        "aliases": ["dsa", "data structures", "algorithms", "data structures and algorithms", "binary trees", "graphs", "sorting algorithms"],
        "description": "Fundamental organization, management, and storage formats for efficient computational execution."
    },
    {
        "canonical_name": "RESTful APIs & Web Services",
        "category": "Web & Backend Development",
        "aliases": ["rest", "restful api", "rest api", "rest apis", "web services", "http api", "api development"],
        "description": "Architectural style for network-based hypermedia and distributed API design."
    },
    {
        "canonical_name": "FastAPI",
        "category": "Web & Backend Development",
        "aliases": ["fastapi", "fast api", "asgi", "starlette", "pydantic"],
        "description": "Modern, high-performance Python web framework for building APIs."
    },
    {
        "canonical_name": "React.js",
        "category": "Frontend Development",
        "aliases": ["react", "react.js", "reactjs", "react js"],
        "description": "Component-based JavaScript library for building responsive user interfaces."
    },
    {
        "canonical_name": "Docker & Containerization",
        "category": "DevOps & Cloud",
        "aliases": ["docker", "containerization", "containers", "dockerfile", "docker compose"],
        "description": "Platform for automating deployment of applications in isolated software containers."
    },
    {
        "canonical_name": "Git & Version Control",
        "category": "Software Engineering Tools",
        "aliases": ["git", "github", "gitlab", "version control", "vcs", "source code management"],
        "description": "Distributed version control system for tracking changes in source code during development."
    },
    {
        "canonical_name": "Machine Learning",
        "category": "Artificial Intelligence & Data",
        "aliases": ["machine learning", "ml", "supervised learning", "unsupervised learning", "scikit-learn", "model training"],
        "description": "Algorithmic systems that learn patterns from empirical data without explicit hardcoded rules."
    },
    {
        "canonical_name": "Natural Language Processing (NLP)",
        "category": "Artificial Intelligence & Data",
        "aliases": ["nlp", "natural language processing", "text processing", "text mining", "spacy", "nltk", "information extraction"],
        "description": "Computational processing and extraction of structured semantics from human textual language."
    },
    {
        "canonical_name": "Health Informatics & EHR Standards",
        "category": "Domain Specific / Healthcare",
        "aliases": ["health informatics", "medical informatics", "ehr", "emr", "fhir", "hl7", "ayush informatics", "clinical data"],
        "description": "Application of information engineering and data management in healthcare and Ayush clinical systems."
    },
    {
        "canonical_name": "HTML5 & Modern CSS",
        "category": "Frontend Development",
        "aliases": ["html", "html5", "css", "css3", "tailwind", "responsive design", "web design"],
        "description": "Core structural and presentation technologies of the World Wide Web."
    },
    {
        "canonical_name": "Object-Oriented Programming (OOP)",
        "category": "Computer Science Core",
        "aliases": ["oop", "object-oriented programming", "classes", "inheritance", "polymorphism", "encapsulation"],
        "description": "Programming paradigm based on the concept of objects containing data and code."
    },
    {
        "canonical_name": "Linux & Shell Scripting",
        "category": "DevOps & Infrastructure",
        "aliases": ["linux", "bash", "shell scripting", "unix", "cli", "terminal"],
        "description": "Operating system utilities, terminal navigation, and automated shell command scripting."
    },
    {
        "canonical_name": "Software Testing & QA",
        "category": "Software Engineering Core",
        "aliases": ["testing", "unit testing", "pytest", "qa", "quality assurance", "test automation", "integration testing"],
        "description": "Verification and validation techniques to ensure software correctness and reliability."
    },
    {
        "canonical_name": "Cloud Computing (AWS/GCP/Azure)",
        "category": "DevOps & Cloud",
        "aliases": ["cloud", "cloud computing", "aws", "amazon web services", "gcp", "azure", "cloud deployment"],
        "description": "On-demand availability of computer system resources, data storage, and compute power."
    },
    {
        "canonical_name": "Continuous Integration & Deployment (CI/CD)",
        "category": "DevOps & Cloud",
        "aliases": ["ci/cd", "cicd", "continuous integration", "github actions", "jenkins", "pipeline deployment"],
        "description": "Automated build, test, and deployment workflows for rapid software delivery."
    },
    {
        "canonical_name": "Agile & Scrum Methodologies",
        "category": "Project & Professional Skills",
        "aliases": ["agile", "scrum", "sprint planning", "kanban", "jira"],
        "description": "Iterative project management and software development lifecycle practices."
    },
    {
        "canonical_name": "Communication & Technical Documentation",
        "category": "Soft & Professional Skills",
        "aliases": ["communication", "technical writing", "documentation", "presentation skills", "team collaboration"],
        "description": "Clear articulation of architectural decisions, user documentation, and cross-team communication."
    }
]

def get_canonical_skill_by_name(name: str):
    target = name.strip().lower()
    for item in CANONICAL_SKILLS:
        if item["canonical_name"].lower() == target:
            return item
        for alias in item["aliases"]:
            if alias.lower() == target:
                return item
    return None
