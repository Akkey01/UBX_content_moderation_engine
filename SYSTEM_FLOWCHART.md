# GuardianAI - System Flowchart & Process Flow

## 🎯 **High-Level System Overview**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GUARDIANAI CONTENT MODERATION ENGINE              │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   CONTENT   │    │   RULE-     │    │   MACHINE   │    │   API &     │  │
│  │ GENERATION  │───▶│   BASED     │───▶│   LEARNING  │───▶│  INTEGRATION│  │
│  │   (DAY 1)   │    │  FILTERING  │    │   (DAY 3+)  │    │  (DAY 8+)   │  │
│  │             │    │   (DAY 2)   │    │             │    │             │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                   │                   │                   │      │
│         ▼                   ▼                   ▼                   ▼      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   LLM APIs  │    │ PostgreSQL  │    │ scikit-learn│    │ FastAPI     │  │
│  │   Gemini    │    │   Database  │    │ Transformers│    │ REST API    │  │
│  │   OpenAI    │    │ Full-Text   │    │   BERT      │    │ WebSocket   │  │
│  │ HuggingFace │    │   Search    │    │   Models    │    │ Auth/RL     │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 **Detailed Process Flow**

### **Phase 1: Content Generation Pipeline**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CONTENT GENERATION FLOW                           │
└─────────────────────────────────────────────────────────────────────────────┘

User Input: python scripts/generate_posts.py --use-llm --count 200
     │
     ▼
┌─────────────────┐
│  LLM Generator  │ ◄─── Initialize API providers (API-first priority)
│   Initialization│     1. Gemini API (Recommended)
└─────────────────┘     2. OpenAI API (Reliable)
     │                  3. HuggingFace API (Free tier)
     ▼                  4. Ollama (Local fallback)
┌─────────────────┐
│  Provider Test  │ ◄─── Check API availability
│   & Selection   │     - Test API connectivity
└─────────────────┘     - Validate API keys
     │                   - Select best available provider
     ▼
┌─────────────────┐
│  Content Types  │ ◄─── Define content categories
│   & Categories  │     - Safe: Professional finance content
└─────────────────┘     - Mild Violation: Subtle promotional language
     │                   - Moderate Violation: Obvious scam indicators
     ▼                   - Severe Violation: Illegal/fraudulent content
┌─────────────────┐
│  Prompt Engine  │ ◄─── Generate context-aware prompts
│   & Generation  │     - Finance-specific prompts
└─────────────────┘     - Category-appropriate language
     │                   - Realistic content patterns
     ▼
┌─────────────────┐
│  LLM API Calls  │ ◄─── Make API requests
│   & Fallback    │     - Parallel provider attempts
└─────────────────┘     - Automatic fallback chain
     │                   - Error handling & retries
     ▼
┌─────────────────┐
│  Content Store  │ ◄─── Save generated content
│   & Metadata    │     - Database storage (PostgreSQL)
└─────────────────┘     - File output (CSV/JSON)
     │                   - Generation metadata tracking
     ▼
┌─────────────────┐
│  Output Files   │ ◄─── Generate structured datasets
│   & Statistics  │     - CSV: Tabular data for analysis
└─────────────────┘     - JSON: Detailed metadata
                        - Statistics: Generation metrics
```

**Key Files Involved:**
- `scripts/generate_posts.py` - Main generation script
- `app/llm_generator.py` - LLM provider management
- `app/guardian_ai.py` - Orchestration controller
- `app/database.py` - Database operations
- `app/models.py` - Data structures

---

### **Phase 2: Rule-Based Filtering Pipeline**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RULE-BASED FILTERING FLOW                         │
└─────────────────────────────────────────────────────────────────────────────┘

Content from Database/File Input
     │
     ▼
┌─────────────────┐
│  Content Load   │ ◄─── Load posts from database or files
│   & Preprocess  │     - Text normalization
└─────────────────┘     - Tokenization
     │                   - Case handling
     ▼
┌─────────────────┐
│  Rule Engine    │ ◄─── Load filtering rules from database
│   Initialization│     - Keyword rules
└─────────────────┘     - Regex patterns
     │                   - Phrase matching rules
     ▼
┌─────────────────┐
│  Multi-Layer    │ ◄─── Apply filtering in sequence
│   Filtering     │     1. Keyword Matching
└─────────────────┘     2. Regex Pattern Matching
     │                  3. Phrase Context Matching
     ▼
┌─────────────────┐
│  Match Detection│ ◄─── Identify rule violations
│   & Scoring     │     - Extract matched text
└─────────────────┘     - Calculate confidence scores
     │                   - Apply rule severity weights
     ▼
┌─────────────────┐
│  Severity       │ ◄─── Calculate overall severity
│   Calculation   │     - Weighted scoring algorithm
└─────────────────┘     - Normalize to 0-1 scale
     │                   - Apply thresholds
     ▼
┌─────────────────┐
│  Result         │ ◄─── Generate filtering results
│   Generation    │     - Severity scores
└─────────────────┘     - Flagged content identification
     │                   - Match details for audit
     ▼
┌─────────────────┐
│  Database       │ ◄─── Store results and logs
│   Persistence   │     - Update posts with scores
└─────────────────┘     - Log all matches
     │                   - Maintain audit trail
     ▼
┌─────────────────┐
│  Output &       │ ◄─── Generate reports
│   Reporting     │     - Filtering statistics
└─────────────────┘     - Performance metrics
                        - Compliance reports
```

**Key Files Involved:**
- `scripts/test_filter.py` - Filter testing script
- `app/rule_filter.py` - Rule-based filtering engine
- `app/database.py` - Database operations
- `app/models.py` - Data structures

---

### **Phase 3: Database Operations Flow**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATABASE OPERATIONS FLOW                          │
└─────────────────────────────────────────────────────────────────────────────┘

Database Connection & Setup
     │
     ▼
┌─────────────────┐
│  Schema         │ ◄─── Create database tables
│   Creation      │     - posts: Content storage
└─────────────────┘     - rules: Filtering rules
     │                   - filtering_logs: Audit trail
     ▼
┌─────────────────┐
│  Index          │ ◄─── Create performance indexes
│   Setup         │     - Full-text search indexes
└─────────────────┘     - Primary key indexes
     │                   - Foreign key indexes
     ▼
┌─────────────────┐
│  Sample Data    │ ◄─── Insert initial data
│   Population    │     - Default filtering rules
└─────────────────┘     - Test content (optional)
     │                   - Configuration data
     ▼
┌─────────────────┐
│  Connection     │ ◄─── Manage database connections
│   Pooling       │     - Connection pooling
└─────────────────┘     - Transaction management
     │                   - Error handling
     ▼
┌─────────────────┐
│  CRUD           │ ◄─── Database operations
│   Operations    │     - Create: Insert new posts/rules
└─────────────────┘     - Read: Query content and results
     │                   - Update: Modify existing records
     ▼                   - Delete: Remove old data
┌─────────────────┐
│  Full-Text      │ ◄─── Advanced search capabilities
│   Search        │     - Content search
└─────────────────┘     - Pattern matching
     │                   - Relevance scoring
     ▼
┌─────────────────┐
│  Audit &        │ ◄─── Maintain data integrity
│   Logging       │     - Transaction logs
└─────────────────┘     - Error logs
                        - Performance metrics
```

**Key Files Involved:**
- `scripts/init_db.py` - Database initialization
- `app/database.py` - Database manager
- `app/models.py` - Data models

---

### **Phase 4: Complete Integration Flow**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           COMPLETE SYSTEM INTEGRATION                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │    │   Configuration │    │   Environment   │
│   & Commands    │    │   & Settings    │    │   Variables     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GUARDIANAI CONTROLLER                             │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │  Content        │    │  Rule-Based     │    │  Database       │          │
│  │  Generation     │    │  Filtering      │    │  Management     │          │
│  │  Orchestrator   │    │  Engine         │    │  & Persistence  │          │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘          │
│         │                       │                       │                   │
│         ▼                       ▼                       ▼                   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │  LLM Provider   │    │  Multi-Layer    │    │  PostgreSQL     │          │
│  │  Management     │    │  Filtering      │    │  Database       │          │
│  │  (API-First)    │    │  (Keyword/Regex)│    │  (Full-Text)    │          │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Generated      │    │  Filtered       │    │  Stored Data    │
│  Content        │    │  Results        │    │  & Logs         │
│  (CSV/JSON)     │    │  (Scores/Flags) │    │  (Audit Trail)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           OUTPUT & REPORTING                                │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │  Content        │    │  Filtering      │    │  Performance    │          │
│  │  Datasets       │    │  Reports        │    │  Metrics        │          │
│  │  (Structured)   │    │  (Compliance)   │    │  (Monitoring)   │          │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 **File Navigation Guide**

### **Core Application Files (`app/`)**

```
app/
├── __init__.py              # Package initialization
├── models.py                # Data models & schemas
│   ├── Post                 # Content structure
│   ├── Rule                 # Filtering rule definition
│   ├── FilterResult         # Filtering outcomes
│   └── ContentGenerationConfig  # Generation parameters
├── database.py              # Database management
│   ├── DatabaseManager      # PostgreSQL operations
│   ├── create_tables()      # Schema creation
│   ├── insert_post()        # Content storage
│   └── get_posts()          # Content retrieval
├── rule_filter.py           # Rule-based filtering
│   ├── RuleFilter           # Main filtering engine
│   ├── analyze_content()    # Content analysis
│   ├── apply_keyword_rules() # Keyword matching
│   ├── apply_regex_rules()  # Pattern matching
│   └── calculate_severity() # Scoring algorithm
├── llm_generator.py         # Content generation
│   ├── LLMContentGenerator  # Main generator
│   ├── GeminiProvider       # Google Gemini API
│   ├── OpenAIProvider       # OpenAI API
│   ├── HuggingFaceProvider  # HuggingFace API
│   └── OllamaProvider       # Local fallback
└── guardian_ai.py           # Main controller
    ├── GuardianAI           # Orchestration class
    ├── generate_content()   # Content generation
    ├── analyze_content()    # Content analysis
    └── get_statistics()     # System metrics
```

### **Operational Scripts (`scripts/`)**

```
scripts/
├── init_db.py               # Database setup
│   ├── create_database()    # Database creation
│   ├── create_tables()      # Schema setup
│   ├── insert_sample_rules() # Default rules
│   └── validate_setup()     # Setup verification
├── generate_posts.py        # Content generation
│   ├── main()               # Main execution
│   ├── parse_arguments()    # CLI argument parsing
│   ├── generate_content()   # Content generation
│   └── save_results()       # Output saving
├── setup_llm.py             # LLM configuration
│   ├── setup_gemini()       # Gemini API setup
│   ├── setup_openai()       # OpenAI API setup
│   ├── setup_huggingface()  # HuggingFace setup
│   ├── test_providers()     # Provider testing
│   └── run_comprehensive_test() # Full testing
├── test_filter.py           # Filter testing
│   ├── test_rules()         # Rule validation
│   ├── benchmark_performance() # Performance testing
│   ├── test_accuracy()      # Accuracy validation
│   └── generate_reports()   # Test reports
└── demo_api_vs_local.py     # Comparison demo
    ├── test_api_providers() # API testing
    ├── test_ollama()        # Local testing
    ├── print_comparison()   # Results comparison
    └── print_recommendations() # Recommendations
```

---

## 📊 **Data Flow Summary**

### **Input → Processing → Output**

```
1. USER COMMAND
   └── python scripts/generate_posts.py --use-llm --count 200
       │
       ▼
2. CONTENT GENERATION
   ├── LLM API calls (Gemini/OpenAI/HuggingFace)
   ├── Template fallback (if APIs unavailable)
   ├── Category-specific content creation
   └── Metadata tracking (provider, method, timestamp)
       │
       ▼
3. DATABASE STORAGE
   ├── PostgreSQL insertion with full-text search
   ├── Foreign key relationships
   ├── Index optimization
   └── Transaction logging
       │
       ▼
4. RULE-BASED FILTERING
   ├── Keyword matching (exact phrases)
   ├── Regex patterns (complex patterns)
   ├── Phrase matching (context-aware)
   ├── Severity scoring (0-1 scale)
   └── Match logging (audit trail)
       │
       ▼
5. RESULT PERSISTENCE
   ├── Update posts with filtering results
   ├── Store detailed match information
   ├── Generate performance metrics
   └── Create compliance reports
       │
       ▼
6. OUTPUT FILES
   ├── CSV: Structured data for analysis
   ├── JSON: Detailed metadata
   ├── Database: Persistent storage
   └── Logs: Audit trail and metrics
```

---

## 🎯 **Key Technical Decisions**

### **1. API-First Approach**
- **Why**: No large model downloads, instant setup, better performance
- **Priority**: Gemini → OpenAI → HuggingFace → Ollama (fallback)
- **Benefits**: Cost-effective, scalable, maintainable

### **2. PostgreSQL Database**
- **Why**: Full-text search, ACID compliance, scalability
- **Features**: Connection pooling, indexing, audit trails
- **Schema**: Normalized design with foreign keys

### **3. Modular Architecture**
- **Why**: Independent development, testing, and scaling
- **Components**: Generation, filtering, database, orchestration
- **Benefits**: Maintainable, testable, extensible

### **4. Rule-Based + ML Hybrid**
- **Why**: Explainable decisions + advanced pattern recognition
- **Current**: Rule-based filtering (Day 2)
- **Future**: ML integration (Day 3+)

This flowchart provides a comprehensive understanding of the GuardianAI system architecture and data flow for both technical and non-technical stakeholders. 