"""
NLP preprocessing utilities.

Deliberately avoids heavyweight NLP model downloads (e.g. spaCy language models)
so the service stays lightweight and fast to deploy. Uses regex + a curated
skills taxonomy for entity/skill extraction, which is fast, transparent, and
easy to extend -- and directly supports the "explainable insights" requirement.
"""
import re
from typing import List, Optional, Set

# A reasonably broad, extensible skills taxonomy. In production this would
# typically be loaded from a database or an external taxonomy (e.g. ESCO, LinkedIn Skills).
SKILLS_TAXONOMY: Set[str] = {
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql", "bash", "shell",
    # Web / frameworks
    "react", "angular", "vue", "django", "flask", "fastapi", "spring", "spring boot",
    "node.js", "nodejs", "express", "next.js", "html", "css", "tailwind", "bootstrap",
    # Data / ML
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "pytorch", "tensorflow", "keras", "scikit-learn", "pandas",
    "numpy", "data analysis", "data science", "data engineering", "statistics",
    "transformers", "llm", "large language models", "generative ai", "mlops",
    # Cloud / DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
    "ci/cd", "jenkins", "git", "github", "gitlab", "linux", "devops",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "oracle", "sqlite",
    "cassandra", "dynamodb",
    # Product / soft / management
    "project management", "agile", "scrum", "kanban", "jira", "leadership",
    "communication", "teamwork", "problem solving", "stakeholder management",
    "product management", "business analysis",
    # Design
    "figma", "ui/ux", "user research", "adobe photoshop", "adobe illustrator",
    # Other common domains
    "rest api", "graphql", "microservices", "system design", "cybersecurity",
    "network security", "penetration testing", "blockchain", "salesforce",
    "excel", "power bi", "tableau", "sap",
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}")
EXPERIENCE_RE = re.compile(
    r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs|year)\s*(?:of)?\s*(?:experience|exp)?",
    re.IGNORECASE,
)


def clean_text(text: str) -> str:
    """Lowercase, normalize whitespace, and strip non-informative characters."""
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)          # URLs
    text = re.sub(r"[^a-z0-9\s.,+#/-]", " ", text)          # keep tokens like c++, c#, node.js
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_email(text: str) -> Optional[str]:
    match = EMAIL_RE.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    match = PHONE_RE.search(text)
    return match.group(0).strip() if match else None


def extract_candidate_name(raw_text: str) -> Optional[str]:
    """
    Heuristic: the candidate's name is usually the first non-empty line
    that isn't an email/phone/header keyword.
    """
    skip_keywords = {"resume", "curriculum vitae", "cv", "profile", "contact"}
    for line in raw_text.splitlines():
        line = line.strip()
        if not line or len(line) > 60:
            continue
        if EMAIL_RE.search(line) or PHONE_RE.search(line):
            continue
        if line.lower() in skip_keywords:
            continue
        # Looks like a plausible name: 2-4 words, mostly alphabetic
        words = line.split()
        if 1 <= len(words) <= 4 and all(w.replace(".", "").isalpha() for w in words):
            return line.title()
    return None


def extract_skills(cleaned_text: str) -> List[str]:
    """Match known skills against the cleaned text using word-boundary search."""
    found = set()
    for skill in SKILLS_TAXONOMY:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, cleaned_text):
            found.add(skill)
    return sorted(found)


def extract_experience_years(text: str) -> Optional[float]:
    """Find the maximum stated years-of-experience figure in the text."""
    matches = EXPERIENCE_RE.findall(text)
    years = [float(m) for m in matches if m]
    return max(years) if years else None


def preprocess_document(raw_text: str) -> dict:
    """Run the full preprocessing pipeline and return structured fields."""
    cleaned = clean_text(raw_text)
    return {
        "cleaned_text": cleaned,
        "skills": extract_skills(cleaned),
        "email": extract_email(raw_text),
        "phone": extract_phone(raw_text),
        "experience_years": extract_experience_years(raw_text),
    }
