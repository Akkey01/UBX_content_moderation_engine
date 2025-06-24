# UnBound X Content Moderation Engine

## Project Overview
A cost-efficient, scalable content moderation system using layered filtering: deterministic rules, lightweight ML, and minimal AI. All moderation flows through a unified controller (GuardianAI) for explainability and tunable thresholds.

**Tech Stack:** Python 3.11+, FastAPI, scikit-learn, HuggingFace Transformers, gensim, SQLite (dev), PostgreSQL (prod)

---

## Day 1: Feed Generation
- **Goal:** Generate a synthetic dataset of user posts by mixing good and malicious phrases.
- **Deliverables:**
  - `scripts/generate_posts.py`: Script to generate posts
  - `data/sample_posts.csv`: 100–200 generated posts

---

## Setup Instructions
1. Clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the feed generator:
   ```bash
   python scripts/generate_posts.py
   ```

---

## Next Steps
- Day 2: Implement rule-based filtering with database-backed profanity and severity lookup.
