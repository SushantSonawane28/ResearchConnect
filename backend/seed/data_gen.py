"""Create a SYNTHETIC research dataset (100 researchers, 40 projects).

!! This data is fake and must be labelled 'synthetic' in your report. !!
Use it to build and test the system. For your real evaluation, replace it with
real/anonymised profiles (e.g. OpenAlex authors) and faculty-judged labels.

Run from the backend folder:   python -m seed.data_gen
Creates: data/researchers.json, data/projects.json, data/labels_synthetic.csv
"""
import csv
import json
import random
from pathlib import Path

SEED = 42
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Some skills have a common acronym; the generator randomly uses it, to make
# the data realistic (people write ML, not "machine learning").
ALIASES = {
    "machine learning": "ML", "natural language processing": "NLP", "deep learning": "DL",
    "computer vision": "CV", "internet of things": "IoT", "large language models": "LLM",
    "optical character recognition": "OCR", "artificial intelligence": "AI",
}

DOMAINS = {
    "Healthcare AI": {
        "skills": ["machine learning", "natural language processing", "medical imaging", "clinical data",
                   "optical character recognition", "deep learning", "python", "health informatics"],
        "interests": ["healthcare ai", "medical document analysis", "disease prediction", "clinical decision support"]},
    "Cybersecurity": {
        "skills": ["network security", "cryptography", "malware analysis", "intrusion detection",
                   "penetration testing", "machine learning", "python", "blockchain"],
        "interests": ["threat detection", "secure systems", "digital forensics", "privacy"]},
    "Data Science": {
        "skills": ["data mining", "statistics", "python", "sql", "data visualization",
                   "machine learning", "big data", "time series"],
        "interests": ["predictive analytics", "data driven decisions", "business intelligence", "forecasting"]},
    "IoT and Embedded": {
        "skills": ["internet of things", "embedded systems", "sensors", "microcontrollers",
                   "edge computing", "wireless networks", "c programming", "python"],
        "interests": ["smart agriculture", "smart cities", "industrial monitoring", "low power devices"]},
    "Computer Vision": {
        "skills": ["computer vision", "deep learning", "image segmentation", "object detection",
                   "opencv", "pytorch", "medical imaging", "robotics"],
        "interests": ["visual inspection", "autonomous vehicles", "face analysis", "satellite imagery"]},
    "NLP and LLMs": {
        "skills": ["natural language processing", "large language models", "text mining", "transformers",
                   "machine translation", "deep learning", "python", "information retrieval"],
        "interests": ["conversational ai", "document intelligence", "indian languages", "question answering"]},
    "Renewable Energy": {
        "skills": ["solar energy", "smart grid", "power electronics", "energy storage",
                   "battery management", "matlab", "optimization", "sustainability"],
        "interests": ["clean energy", "grid stability", "electric vehicles", "energy efficiency"]},
    "Structural Engineering": {
        "skills": ["structural analysis", "finite element analysis", "concrete technology",
                   "earthquake engineering", "materials testing", "sustainability", "civil engineering", "matlab"],
        "interests": ["green buildings", "bridge health monitoring", "disaster resilience", "low cost housing"]},
}
GENERIC = ["python", "statistics", "technical writing", "project management", "matlab", "data analysis"]
DEPARTMENTS = {"Healthcare AI": "Computer Engineering", "Cybersecurity": "Information Technology",
               "Data Science": "Computer Engineering", "IoT and Embedded": "Electronics",
               "Computer Vision": "Computer Engineering", "NLP and LLMs": "Information Technology",
               "Renewable Energy": "Electrical", "Structural Engineering": "Civil"}
ORGS = [("Alpha Institute of Technology", "college"), ("Beta College of Engineering", "college"),
        ("Gamma University", "university"), ("Delta Engineering College", "college"),
        ("NovaTech Labs", "company"), ("MediSense Pvt Ltd", "company")]
FIRST = ["Aarav", "Meera", "Rohan", "Sneha", "Kunal", "Priya", "Arjun", "Isha", "Vikram", "Anita",
         "Rahul", "Neha", "Sanjay", "Pooja", "Amit", "Divya", "Karan", "Riya", "Manish", "Tanvi"]
LAST = ["Sharma", "Patil", "Kulkarni", "Deshmukh", "Joshi", "Iyer", "Nair", "Gupta", "Mehta", "Rao"]


def skill_label(rng, skill):
    return ALIASES[skill] if skill in ALIASES and rng.random() < 0.4 else skill


def make_researcher(rng, rid):
    primary = rng.choice(list(DOMAINS))
    secondary = rng.choice([d for d in DOMAINS if d != primary]) if rng.random() < 0.3 else None
    p, sk = DOMAINS[primary], []
    sk += rng.sample(p["skills"], rng.randint(3, 5))
    if secondary:
        sk += rng.sample(DOMAINS[secondary]["skills"], 2)
    sk += rng.sample(GENERIC, 1)
    interests = rng.sample(p["interests"], rng.randint(2, 3))
    if secondary:
        interests.append(rng.choice(DOMAINS[secondary]["interests"]))
    sk = list(dict.fromkeys(sk))
    bio = (f"Works on {sk[0]} and {sk[1]} with applications in {interests[0]}. "
           f"Interested in {interests[-1]} and {rng.choice(p['skills'])}.")
    org_name, org_type = rng.choice(ORGS)
    return {"id": rid, "name": f"{rng.choice(FIRST)} {rng.choice(LAST)} {rid}",
            "organization": org_name, "org_type": org_type,
            "department": DEPARTMENTS[primary], "primary_domain": primary, "secondary_domain": secondary,
            "skills": [skill_label(rng, s) for s in sk], "interests": interests,
            "expertise": [skill_label(rng, sk[0])], "bio": bio, "synthetic": True}


def make_project(rng, pid, owner_ids):
    dom = rng.choice(list(DOMAINS))
    skills = rng.sample(DOMAINS[dom]["skills"], rng.randint(3, 4))
    interest = rng.choice(DOMAINS[dom]["interests"])
    return {"id": pid, "owner_id": rng.choice(owner_ids), "domain": dom,
            "title": f"{interest.title()} using {skills[0]}",
            "description": f"A project on {interest} that uses {skills[0]} and {skills[1]}.",
            "tags": [skill_label(rng, s) for s in skills], "synthetic": True}


def relevant(a, b):
    """Synthetic ground truth: same primary domain, or one's primary is the other's secondary."""
    return (a["primary_domain"] == b["primary_domain"]
            or a["primary_domain"] == b["secondary_domain"]
            or b["primary_domain"] == a["secondary_domain"])


def main(n_researchers=100, n_projects=40):
    rng = random.Random(SEED)
    DATA_DIR.mkdir(exist_ok=True)
    researchers = [make_researcher(rng, i) for i in range(1, n_researchers + 1)]
    projects = [make_project(rng, i, [r["id"] for r in researchers]) for i in range(1, n_projects + 1)]
    (DATA_DIR / "researchers.json").write_text(json.dumps(researchers, indent=1))
    (DATA_DIR / "projects.json").write_text(json.dumps(projects, indent=1))
    with open(DATA_DIR / "labels_synthetic.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["researcher_a", "researcher_b", "relevant"])
        for a in researchers:
            for b in researchers:
                if a["id"] < b["id"]:
                    w.writerow([a["id"], b["id"], int(relevant(a, b))])
    print(f"Wrote {len(researchers)} researchers, {len(projects)} projects to {DATA_DIR}")


if __name__ == "__main__":
    main()
