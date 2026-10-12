"""Compare the four matching methods.

Run from the backend folder:   python -m evaluation.run_experiments
Needs: data/researchers.json and data/labels_synthetic.csv  (run `python -m seed.data_gen` first)

For your REAL study: create data/labels_faculty.csv with the same 3 columns
(researcher_a, researcher_b, relevant) judged by faculty, then run with --labels faculty.
"""
import argparse
import csv
import json
import time
from pathlib import Path

from app.matching import METHODS, MatchingEngine, MatchProfile

DATA = Path(__file__).resolve().parent.parent / "data"


def load(labels_name):
    researchers = json.loads((DATA / "researchers.json").read_text())
    profiles = [MatchProfile(id=str(r["id"]), name=r["name"],
                             tags=r["skills"] + r["interests"] + r["expertise"],
                             text=r["bio"], domain=r["primary_domain"]) for r in researchers]
    relevant = {}
    with open(DATA / f"labels_{labels_name}.csv") as f:
        for row in csv.DictReader(f):
            if int(row["relevant"]):
                a, b = row["researcher_a"], row["researcher_b"]
                relevant.setdefault(a, set()).add(b)
                relevant.setdefault(b, set()).add(a)
    return profiles, relevant


def evaluate(profiles, relevant, k=10):
    engine = MatchingEngine(profiles)
    rows = []
    for method in METHODS:
        P, R, F, times = [], [], [], []
        for p in profiles:
            truth = relevant.get(p.id, set())
            if not truth:
                continue
            t0 = time.perf_counter()
            top = engine.rank(p.id, method=method, top_k=k)
            times.append((time.perf_counter() - t0) * 1000)
            hits = sum(1 for r in top if r["id"] in truth)
            prec, rec = hits / k, hits / len(truth)
            P.append(prec); R.append(rec)
            F.append(2 * prec * rec / (prec + rec) if prec + rec else 0.0)
        n = len(P)
        rows.append({"method": method, f"precision@{k}": round(sum(P) / n, 3),
                     f"recall@{k}": round(sum(R) / n, 3), "f1": round(sum(F) / n, 3),
                     "avg_ms_per_query": round(sum(times) / n, 2)})
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default="synthetic", help="synthetic or faculty")
    ap.add_argument("--k", type=int, default=10)
    a = ap.parse_args()
    profiles, relevant = load(a.labels)
    rows = evaluate(profiles, relevant, a.k)
    out = DATA / f"results_{a.labels}.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    print(f"Labels: {a.labels} | profiles: {len(profiles)} | k={a.k}")
    for r in rows:
        print(r)
    print("Saved:", out)
