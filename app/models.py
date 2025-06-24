from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class PatternType(str, Enum):
    KEYWORD = "keyword"
    REGEX = "regex"
    PHRASE = "phrase"

class Action(str, Enum):
    FLAG = "flag"
    REVIEW = "review"
    BLOCK = "block"

class Rule(BaseModel):
    """Model for content moderation rules"""
    pattern: str = Field(..., description="Pattern to match (keyword, regex, or phrase)")
    pattern_type: PatternType = Field(..., description="Type of pattern matching")
    category: str = Field(..., description="Category of violation (profanity, scam, fraud, etc.)")
    severity: int = Field(..., ge=1, le=3, description="Severity level (1=mild, 2=moderate, 3=severe)")
    action: Action = Field(..., description="Action to take when rule matches")
    description: Optional[str] = Field(None, description="Human-readable description of the rule")
    is_active: bool = Field(True, description="Whether the rule is active")

    @validator('pattern')
    def validate_pattern(cls, v):
        if not v.strip():
            raise ValueError("Pattern cannot be empty")
        return v.strip()

class RuleCreate(Rule):
    """Model for creating new rules"""
    pass

class RuleResponse(Rule):
    """Model for rule responses (includes database fields)"""
    id: int
    created_at: datetime

class MatchedRule(BaseModel):
    """Model for matched rules in content analysis"""
    rule_id: int
    pattern: str
    category: str
    severity: int
    action: Action
    description: Optional[str]
    match_count: int = Field(1, description="Number of times this rule matched")

class ModerationResult(BaseModel):
    """Model for content moderation results"""
    post_id: str = Field(..., description="Unique identifier for the post")
    content: str = Field(..., description="Original content that was analyzed")
    score: float = Field(..., ge=0, le=3, description="Final severity score (0-3)")
    action: Action = Field(..., description="Recommended action based on score")
    matched_rules: List[MatchedRule] = Field(default_factory=list, description="List of matched rules")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    explanation: str = Field(..., description="Human-readable explanation of the decision")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the analysis was performed")

    @validator('action')
    def determine_action(cls, v, values):
        """Automatically determine action based on score if not provided"""
        if 'score' in values:
            score = values['score']
            if score == 0:
                return Action.REVIEW  # Default for safe content
            elif score < 1:
                return Action.REVIEW
            elif score < 2:
                return Action.FLAG
            else:
                return Action.BLOCK
        return v

class ContentAnalysisRequest(BaseModel):
    """Model for content analysis requests"""
    post_id: str = Field(..., description="Unique identifier for the post")
    content: str = Field(..., description="Content to analyze")
    user_id: Optional[str] = Field(None, description="Optional user identifier")

class DatabaseConfig(BaseModel):
    """Model for database configuration"""
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    
    @property
    def connection_string(self) -> str:
        """Generate PostgreSQL connection string"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

class ModerationStats(BaseModel):
    """Model for moderation statistics"""
    total_posts: int
    average_score: float
    action_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    average_processing_time_ms: float
    time_period: str 