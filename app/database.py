import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.extensions import connection, cursor
from typing import List, Dict, Optional, Any
import logging
from contextlib import contextmanager
from .models import Rule, RuleCreate, DatabaseConfig, ModerationResult
import json
from datetime import datetime

class DatabaseManager:
    """PostgreSQL database manager for content moderation rules and logs"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password
            )
            yield conn
        except Exception as e:
            self.logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def init_database(self):
        """Initialize database schema and indexes"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Create rules table with full-text search
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS rules (
                        id SERIAL PRIMARY KEY,
                        pattern TEXT NOT NULL,
                        pattern_type VARCHAR(20) NOT NULL CHECK (pattern_type IN ('keyword', 'regex', 'phrase')),
                        category VARCHAR(50) NOT NULL,
                        severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 3),
                        action VARCHAR(20) NOT NULL CHECK (action IN ('flag', 'review', 'block')),
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', pattern)) STORED
                    );
                """)
                
                # Create moderation logs table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS moderation_logs (
                        id SERIAL PRIMARY KEY,
                        post_id VARCHAR(50),
                        content TEXT,
                        matched_rules JSONB,
                        final_score DECIMAL(3,2),
                        action VARCHAR(20),
                        processing_time_ms INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Create indexes for performance
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_rules_search_vector 
                    ON rules USING GIN(search_vector);
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_rules_category 
                    ON rules(category);
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_rules_severity 
                    ON rules(severity);
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_rules_active 
                    ON rules(is_active);
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_moderation_logs_post_id 
                    ON moderation_logs(post_id);
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_moderation_logs_created_at 
                    ON moderation_logs(created_at);
                """)
                
                conn.commit()
                self.logger.info("Database schema initialized successfully")
    
    def add_rule(self, rule: RuleCreate) -> int:
        """Add a new rule to the database"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO rules (pattern, pattern_type, category, severity, action, description, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    rule.pattern,
                    rule.pattern_type.value,
                    rule.category,
                    rule.severity,
                    rule.action.value,
                    rule.description,
                    rule.is_active
                ))
                rule_id = cur.fetchone()[0]
                conn.commit()
                self.logger.info(f"Added rule {rule_id}: {rule.pattern}")
                return rule_id
    
    def get_rules_by_category(self, category: str) -> List[Dict]:
        """Get active rules by category"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM rules 
                    WHERE category = %s AND is_active = TRUE
                    ORDER BY severity DESC, created_at DESC
                """, (category,))
                return cur.fetchall()
    
    def get_all_active_rules(self) -> List[Dict]:
        """Get all active rules"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM rules 
                    WHERE is_active = TRUE
                    ORDER BY category, severity DESC
                """)
                return cur.fetchall()
    
    def search_content(self, content: str) -> List[Dict]:
        """Search content against all active rules using PostgreSQL full-text search"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # First, try full-text search for keywords and phrases
                cur.execute("""
                    SELECT id, pattern, pattern_type, category, severity, action, description
                    FROM rules 
                    WHERE is_active = TRUE 
                    AND pattern_type IN ('keyword', 'phrase')
                    AND search_vector @@ plainto_tsquery('english', %s)
                """, (content,))
                
                keyword_matches = cur.fetchall()
                
                # Then check regex patterns
                cur.execute("""
                    SELECT id, pattern, pattern_type, category, severity, action, description
                    FROM rules 
                    WHERE is_active = TRUE 
                    AND pattern_type = 'regex'
                """)
                
                regex_rules = cur.fetchall()
                
                # Filter regex matches in Python (PostgreSQL regex is more complex)
                regex_matches = []
                for rule in regex_rules:
                    try:
                        if re.search(rule['pattern'], content, re.IGNORECASE):
                            regex_matches.append(rule)
                    except re.error:
                        self.logger.warning(f"Invalid regex pattern: {rule['pattern']}")
                
                # Combine and deduplicate matches
                all_matches = keyword_matches + regex_matches
                unique_matches = {}
                
                for match in all_matches:
                    rule_id = match['id']
                    if rule_id not in unique_matches:
                        unique_matches[rule_id] = match
                        unique_matches[rule_id]['match_count'] = 1
                    else:
                        unique_matches[rule_id]['match_count'] += 1
                
                return list(unique_matches.values())
    
    def log_moderation(self, post_id: str, content: str, result: Dict):
        """Log moderation result to database"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO moderation_logs 
                    (post_id, content, matched_rules, final_score, action, processing_time_ms)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    post_id,
                    content,
                    json.dumps(result.get('matched_rules', [])),
                    result.get('score', 0),
                    result.get('action', 'review'),
                    result.get('processing_time_ms', 0)
                ))
                conn.commit()
    
    def get_moderation_stats(self, hours: int = 24) -> Dict:
        """Get moderation statistics for the last N hours"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_posts,
                        AVG(final_score) as average_score,
                        AVG(processing_time_ms) as average_processing_time,
                        action,
                        COUNT(*) as action_count
                    FROM moderation_logs 
                    WHERE created_at >= NOW() - INTERVAL '%s hours'
                    GROUP BY action
                """, (hours,))
                
                action_stats = cur.fetchall()
                
                # Get category distribution from matched rules
                cur.execute("""
                    SELECT 
                        jsonb_array_elements(matched_rules)->>'category' as category,
                        COUNT(*) as category_count
                    FROM moderation_logs 
                    WHERE created_at >= NOW() - INTERVAL '%s hours'
                    AND matched_rules != '[]'::jsonb
                    GROUP BY category
                """, (hours,))
                
                category_stats = cur.fetchall()
                
                return {
                    'total_posts': sum(row['total_posts'] for row in action_stats),
                    'average_score': float(action_stats[0]['average_score']) if action_stats else 0,
                    'average_processing_time_ms': float(action_stats[0]['average_processing_time']) if action_stats else 0,
                    'action_distribution': {row['action']: row['action_count'] for row in action_stats},
                    'category_distribution': {row['category']: row['category_count'] for row in category_stats}
                }
    
    def populate_sample_rules(self):
        """Populate database with sample finance-specific rules"""
        sample_rules = [
            # Profanity and offensive language
            RuleCreate(
                pattern="fuck|shit|bitch|asshole",
                pattern_type="regex",
                category="profanity",
                severity=2,
                action="flag",
                description="Profane language detected"
            ),
            RuleCreate(
                pattern="stupid|idiot|moron",
                pattern_type="regex",
                category="offensive",
                severity=1,
                action="review",
                description="Potentially offensive language"
            ),
            
            # Financial scams and fraud
            RuleCreate(
                pattern="guaranteed.*return|no risk.*reward",
                pattern_type="regex",
                category="scam",
                severity=3,
                action="block",
                description="Scam indicators detected"
            ),
            RuleCreate(
                pattern="insider.*tip|leaked.*information",
                pattern_type="regex",
                category="fraud",
                severity=3,
                action="block",
                description="Potential insider trading"
            ),
            RuleCreate(
                pattern="get rich quick",
                pattern_type="phrase",
                category="scam",
                severity=2,
                action="flag",
                description="Suspicious financial promises"
            ),
            
            # Market manipulation
            RuleCreate(
                pattern="pump.*dump|coordinate.*buying",
                pattern_type="regex",
                category="manipulation",
                severity=3,
                action="block",
                description="Market manipulation indicators"
            ),
            RuleCreate(
                pattern="artificial.*price",
                pattern_type="phrase",
                category="manipulation",
                severity=2,
                action="flag",
                description="Suspicious trading activity"
            ),
            
            # Spam and promotional content
            RuleCreate(
                pattern="buy now|limited time|act fast",
                pattern_type="regex",
                category="spam",
                severity=1,
                action="review",
                description="Promotional spam indicators"
            ),
            RuleCreate(
                pattern="click here|free money",
                pattern_type="phrase",
                category="spam",
                severity=1,
                action="review",
                description="Spam link indicators"
            )
        ]
        
        for rule in sample_rules:
            try:
                self.add_rule(rule)
            except Exception as e:
                self.logger.warning(f"Failed to add sample rule {rule.pattern}: {e}")
        
        self.logger.info(f"Populated {len(sample_rules)} sample rules")

# Import re for regex matching
import re 