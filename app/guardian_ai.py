import logging
from typing import Dict, List, Optional
from .database import DatabaseManager
from .rule_filter import RuleFilter
from .models import (
    ModerationResult, 
    ContentAnalysisRequest, 
    DatabaseConfig,
    Action,
    MatchedRule
)

class GuardianAI:
    """
    Main content moderation controller that orchestrates the filtering process.
    Combines database operations, rule filtering, and result logging.
    """
    
    def __init__(self, db_config: DatabaseConfig):
        """
        Initialize GuardianAI with database configuration
        
        Args:
            db_config: Database configuration object
        """
        self.logger = logging.getLogger(__name__)
        self.db_manager = DatabaseManager(db_config)
        self.rule_filter = RuleFilter(self.db_manager)
        
        self.logger.info("GuardianAI initialized successfully")
    
    def moderate_content(self, post_id: str, content: str, user_id: Optional[str] = None) -> ModerationResult:
        """
        Main entry point for content moderation
        
        Args:
            post_id: Unique identifier for the post
            content: Content to analyze
            user_id: Optional user identifier for tracking
            
        Returns:
            ModerationResult with analysis details
        """
        try:
            self.logger.info(f"Starting moderation for post {post_id}")
            
            # Analyze content using rule filter
            analysis_result = self.rule_filter.analyze_content(content)
            
            # Create moderation result
            result = ModerationResult(
                post_id=post_id,
                content=content,
                score=analysis_result['score'],
                action=analysis_result['action'],
                matched_rules=analysis_result['matched_rules'],
                processing_time_ms=analysis_result['processing_time_ms'],
                explanation=analysis_result['explanation']
            )
            
            # Log the moderation result
            self.db_manager.log_moderation(post_id, content, analysis_result)
            
            self.logger.info(
                f"Moderation complete for post {post_id}: "
                f"score={result.score}, action={result.action}, "
                f"processing_time={result.processing_time_ms}ms"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Moderation failed for post {post_id}: {e}")
            
            # Return error result
            return ModerationResult(
                post_id=post_id,
                content=content,
                score=0.0,
                action=Action.REVIEW,
                matched_rules=[],
                processing_time_ms=0,
                explanation=f"Moderation failed: {str(e)}"
            )
    
    def batch_moderate(self, posts: List[Dict]) -> List[ModerationResult]:
        """
        Process multiple posts in batch
        
        Args:
            posts: List of post dictionaries with 'id' and 'content' keys
            
        Returns:
            List of ModerationResult objects
        """
        results = []
        
        for post in posts:
            try:
                result = self.moderate_content(
                    post_id=post['id'],
                    content=post['content'],
                    user_id=post.get('user_id')
                )
                results.append(result)
            except Exception as e:
                self.logger.error(f"Batch moderation failed for post {post.get('id', 'unknown')}: {e}")
                # Add error result
                results.append(ModerationResult(
                    post_id=post.get('id', 'unknown'),
                    content=post.get('content', ''),
                    score=0.0,
                    action=Action.REVIEW,
                    matched_rules=[],
                    processing_time_ms=0,
                    explanation=f"Batch processing failed: {str(e)}"
                ))
        
        return results
    
    def get_system_stats(self, hours: int = 24) -> Dict:
        """
        Get system statistics and performance metrics
        
        Args:
            hours: Time period for statistics (default: 24 hours)
            
        Returns:
            Dictionary containing system statistics
        """
        try:
            # Get moderation statistics
            mod_stats = self.db_manager.get_moderation_stats(hours)
            
            # Get rule statistics
            rule_stats = self.rule_filter.get_rule_statistics()
            
            return {
                'moderation_stats': mod_stats,
                'rule_stats': rule_stats,
                'time_period_hours': hours
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system stats: {e}")
            return {
                'error': str(e),
                'time_period_hours': hours
            }
    
    def add_rule(self, rule_data: Dict) -> int:
        """
        Add a new moderation rule
        
        Args:
            rule_data: Dictionary containing rule information
            
        Returns:
            ID of the newly created rule
        """
        try:
            from .models import RuleCreate
            
            # Validate rule data
            rule = RuleCreate(**rule_data)
            
            # Add to database
            rule_id = self.db_manager.add_rule(rule)
            
            self.logger.info(f"Added new rule {rule_id}: {rule.pattern}")
            return rule_id
            
        except Exception as e:
            self.logger.error(f"Failed to add rule: {e}")
            raise
    
    def get_rules_by_category(self, category: str) -> List[Dict]:
        """
        Get rules by category
        
        Args:
            category: Category to filter by
            
        Returns:
            List of rules in the specified category
        """
        try:
            return self.db_manager.get_rules_by_category(category)
        except Exception as e:
            self.logger.error(f"Failed to get rules for category {category}: {e}")
            return []
    
    def test_content(self, test_content: str) -> Dict:
        """
        Test content analysis for debugging
        
        Args:
            test_content: Content to test
            
        Returns:
            Detailed analysis information
        """
        try:
            return self.rule_filter.test_rule_matching(test_content)
        except Exception as e:
            self.logger.error(f"Content test failed: {e}")
            return {
                'test_content': test_content,
                'error': str(e)
            }
    
    def initialize_sample_data(self):
        """
        Initialize the system with sample rules and test data
        """
        try:
            self.logger.info("Initializing sample data...")
            
            # Populate sample rules
            self.db_manager.populate_sample_rules()
            
            self.logger.info("Sample data initialization complete")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize sample data: {e}")
            raise
    
    def health_check(self) -> Dict:
        """
        Perform system health check
        
        Returns:
            Health status information
        """
        try:
            # Test database connection
            db_status = "healthy"
            try:
                rules = self.db_manager.get_all_active_rules()
                db_rule_count = len(rules)
            except Exception as e:
                db_status = f"error: {str(e)}"
                db_rule_count = 0
            
            # Test rule filter
            filter_status = "healthy"
            try:
                test_result = self.rule_filter.analyze_content("test content")
                filter_working = True
            except Exception as e:
                filter_status = f"error: {str(e)}"
                filter_working = False
            
            return {
                'status': 'healthy' if db_status == 'healthy' and filter_status == 'healthy' else 'degraded',
                'database': {
                    'status': db_status,
                    'active_rules': db_rule_count
                },
                'rule_filter': {
                    'status': filter_status,
                    'working': filter_working
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Import datetime for health check
from datetime import datetime 