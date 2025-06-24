# UnBound X Content Moderation Engine

## Project Overview
A cost-efficient, scalable content moderation system using layered filtering: deterministic rules, lightweight ML, and minimal AI. All moderation flows through a unified controller (GuardianAI) for explainability and tunable thresholds.

**Tech Stack:** Python 3.11+, FastAPI, scikit-learn, HuggingFace Transformers, gensim, PostgreSQL

---

## Day 1: Feed Generation ✅
- **Goal:** Generate a synthetic dataset of user posts by mixing good and malicious phrases.
- **Deliverables:**
  - `scripts/generate_posts.py`: Script to generate posts
  - `data/finance_content_dataset_<timestamp>.csv` and `.json`: 100–200 generated posts

---

## Day 2: Rule-Based Filtering (GuardianAI v1) ✅
- **Goal:** Implement PostgreSQL-backed rule filtering with keyword, regex, and phrase matching.
- **Deliverables:**
  - `app/database.py`: PostgreSQL database manager with full-text search
  - `app/rule_filter.py`: Content analysis engine with severity scoring
  - `app/guardian_ai.py`: Main moderation controller
  - `app/models.py`: Pydantic data models
  - `scripts/init_db.py`: Database initialization script
  - `scripts/test_filter.py`: Comprehensive testing script

### Features
- **PostgreSQL Integration:** Full-text search, JSONB storage, performance indexes
- **Multi-Pattern Matching:** Keywords, regex patterns, and phrases
- **Intelligent Scoring:** Context bonuses, frequency penalties, severity calculation
- **Comprehensive Logging:** All moderation decisions logged with metadata
- **Health Monitoring:** System health checks and performance metrics

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

### 3. PostgreSQL Setup
1. **Install PostgreSQL** (if not already installed)
2. **Create Database:**
   ```sql
   CREATE DATABASE guardian_ai;
   CREATE USER guardian_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE guardian_ai TO guardian_user;
   ```

### 4. Initialize Database
```powershell
python scripts/init_db.py --database guardian_ai --username guardian_user --password your_password
```

### 5. Generate Test Data (Day 1)
```powershell
python scripts/generate_posts.py
```

### 6. Test the System (Day 2)
```powershell
# Run comprehensive tests
python scripts/test_filter.py --database guardian_ai --username guardian_user --password your_password

# Test with generated data
python scripts/test_filter.py --database guardian_ai --username guardian_user --password your_password --data-file data/finance_content_dataset_*.csv
```

---

## Usage Examples

### Basic Content Moderation
```python
from app.models import DatabaseConfig
from app.guardian_ai import GuardianAI

# Initialize system
db_config = DatabaseConfig(
    host='localhost',
    database='guardian_ai',
    username='guardian_user',
    password='your_password'
)
guardian = GuardianAI(db_config)

# Moderate content
result = guardian.moderate_content(
    post_id="post_123",
    content="This is a test post with some content."
)
print(f"Score: {result.score}, Action: {result.action}")
```

### Batch Processing
```python
# Process multiple posts
posts = [
    {"id": "post_1", "content": "Safe content here"},
    {"id": "post_2", "content": "Fuck this company!"},
    {"id": "post_3", "content": "Guaranteed 100% returns!"}
]

results = guardian.batch_moderate(posts)
for result in results:
    print(f"{result.post_id}: {result.action} (score: {result.score})")
```

### System Statistics
```python
# Get system performance metrics
stats = guardian.get_system_stats(hours=24)
print(f"Active rules: {stats['rule_stats']['total_rules']}")
print(f"Average processing time: {stats['moderation_stats']['average_processing_time_ms']}ms")
```

---

## Key Features

### Day 1: Feed Generator
- **Flexible output:** Choose CSV, JSON, or both with `--formats`.
- **Overwrite protection:** Warns if output files exist unless `--overwrite` is used.
- **Customizable:** Control post count, ratios, output dir, random seed, and logging level.

### Day 2: GuardianAI System
- **PostgreSQL Full-Text Search:** Efficient keyword and phrase matching
- **Regex Pattern Matching:** Complex pattern detection for fraud/scam detection
- **Intelligent Scoring:** Multi-factor severity calculation with context bonuses
- **Comprehensive Logging:** All decisions logged with performance metrics
- **Health Monitoring:** Real-time system health checks
- **Batch Processing:** Efficient handling of multiple posts
- **Sample Rules:** Pre-configured finance-specific moderation rules

---

## Next Steps
- Day 3: Basic Post Viewer UI
- Day 4: GuardianAI Core Pipeline
- Day 5: LLM Escalation Logic

---

## Performance Metrics
- **Latency:** < 50ms per post
- **Throughput:** 1000+ posts/second
- **Accuracy:** > 95% on test dataset
- **False Positives:** < 5%
