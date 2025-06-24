# UnBound X Content Moderation Engine

## Project Overview
A cost-efficient, scalable content moderation system using layered filtering: deterministic rules, lightweight ML, and minimal AI. All moderation flows through a unified controller (GuardianAI) for explainability and tunable thresholds.

**Tech Stack:** Python 3.11+, FastAPI, scikit-learn, HuggingFace Transformers, gensim, SQLite (dev), PostgreSQL (prod)

---

## Day 1: Feed Generation
- **Goal:** Generate a synthetic dataset of user posts by mixing good and malicious phrases.
- **Deliverables:**
  - `scripts/generate_posts.py`: Script to generate posts
  - `data/finance_content_dataset_<timestamp>.csv` and `.json`: 100–200 generated posts

---

## Setup Instructions

### 1. Create and Activate a Virtual Environment (Windows)
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run the Feed Generator
#### Default usage (200 posts, both formats, data/ dir):
```powershell
python scripts/generate_posts.py
```
#### Custom usage examples:
```powershell
# Generate 500 posts, only CSV, custom output dir, custom seed, debug logging
python scripts/generate_posts.py --total-posts 500 --formats csv --outdir mydata --seed 123 --loglevel DEBUG

# Overwrite existing files if present
python scripts/generate_posts.py --overwrite
```

#### Key Features
- **Flexible output:** Choose CSV, JSON, or both with `--formats`.
- **Overwrite protection:** Warns if output files exist unless `--overwrite` is used.
- **Customizable:** Control post count, ratios, output dir, random seed, and logging level.

---

## Next Steps
- Day 2: Implement rule-based filtering with database-backed profanity and severity lookup.
