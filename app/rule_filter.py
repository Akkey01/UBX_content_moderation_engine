import time
import logging
from typing import Dict, List, Tuple
from .database import DatabaseManager
from .models import ModerationResult, MatchedRule, Action

class RuleFilter:
    """Content moderation rule filtering engine"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        
    def analyze_content(self, content: str) -> Dict:
        """
        Analyze content and return moderation result
        
        Args:
            content: Text content to analyze
            
        Returns:
            Dict containing score, action, matched_rules, processing_time_ms, and explanation
        """
        start_time = time.time()
        
        try:
            # Get matching rules from database
            matched_rules = self.db.search_content(content)
            
            # Calculate severity score
            final_score = self._calculate_severity(matched_rules)
            
            # Determine action based on score
            action = self._determine_action(final_score)
            
            # Generate explanation
            explanation = self._generate_explanation(matched_rules, final_score, action)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                "score": final_score,
                "action": action,
                "matched_rules": matched_rules,
                "processing_time_ms": processing_time,
                "explanation": explanation
            }
            
        except Exception as e:
            self.logger.error(f"Content analysis failed: {e}")
            processing_time = int((time.time() - start_time) * 1000)
            return {
                "score": 0,
                "action": Action.REVIEW,
                "matched_rules": [],
                "processing_time_ms": processing_time,
                "explanation": f"Analysis failed: {str(e)}"
            }
    
    def _calculate_severity(self, matched_rules: List[Dict]) -> float:
        """
        Calculate final severity score based on matched rules
        
        Scoring algorithm:
        - Base score = highest severity among matched rules
        - Context bonus = +0.5 for multiple rule matches
        - Frequency penalty = +0.2 per additional occurrence of same rule
        - Final score = min(base_score + bonuses, 3.0)
        """
        if not matched_rules:
            return 0.0
        
        # Get base score (highest severity)
        base_score = max(rule['severity'] for rule in matched_rules)
        
        # Context bonus for multiple rule matches
        context_bonus = 0.5 if len(matched_rules) > 1 else 0.0
        
        # Frequency penalty for repeated matches
        frequency_penalty = sum(
            (rule.get('match_count', 1) - 1) * 0.2 
            for rule in matched_rules
        )
        
        # Calculate final score
        final_score = base_score + context_bonus + frequency_penalty
        
        # Cap at maximum severity
        return min(final_score, 3.0)
    
    def _determine_action(self, score: float) -> Action:
        """
        Determine action based on severity score
        
        Args:
            score: Severity score (0-3)
            
        Returns:
            Recommended action
        """
        if score == 0:
            return Action.REVIEW  # Safe content
        elif score < 1:
            return Action.REVIEW  # Mild violations
        elif score < 2:
            return Action.FLAG    # Moderate violations
        else:
            return Action.BLOCK   # Severe violations
    
    def _generate_explanation(self, matched_rules: List[Dict], score: float, action: Action) -> str:
        """
        Generate human-readable explanation of the moderation decision
        
        Args:
            matched_rules: List of matched rules
            score: Final severity score
            action: Recommended action
            
        Returns:
            Human-readable explanation
        """
        if not matched_rules:
            return "Content appears to be safe and follows community guidelines."
        
        # Group rules by category
        categories = {}
        for rule in matched_rules:
            category = rule['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(rule)
        
        # Build explanation
        explanation_parts = []
        
        if len(categories) == 1:
            category = list(categories.keys())[0]
            rules = categories[category]
            if len(rules) == 1:
                rule = rules[0]
                explanation_parts.append(
                    f"Content flagged for {category}: {rule['description'] or rule['pattern']}"
                )
            else:
                explanation_parts.append(
                    f"Content flagged for multiple {category} violations ({len(rules)} rules matched)"
                )
        else:
            explanation_parts.append(
                f"Content flagged for multiple violation categories: {', '.join(categories.keys())}"
            )
        
        # Add severity context
        if score >= 2.5:
            explanation_parts.append("This represents a severe violation requiring immediate action.")
        elif score >= 1.5:
            explanation_parts.append("This represents a moderate violation requiring review.")
        else:
            explanation_parts.append("This represents a mild violation that may need attention.")
        
        # Add action explanation
        if action == Action.BLOCK:
            explanation_parts.append("Content has been blocked due to policy violations.")
        elif action == Action.FLAG:
            explanation_parts.append("Content has been flagged for moderator review.")
        else:
            explanation_parts.append("Content has been marked for review.")
        
        return " ".join(explanation_parts)
    
    def get_rule_statistics(self) -> Dict:
        """
        Get statistics about available rules
        
        Returns:
            Dict containing rule statistics
        """
        try:
            all_rules = self.db.get_all_active_rules()
            
            # Count by category
            category_counts = {}
            severity_counts = {1: 0, 2: 0, 3: 0}
            pattern_type_counts = {'keyword': 0, 'regex': 0, 'phrase': 0}
            
            for rule in all_rules:
                # Category counts
                category = rule['category']
                category_counts[category] = category_counts.get(category, 0) + 1
                
                # Severity counts
                severity = rule['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                # Pattern type counts
                pattern_type = rule['pattern_type']
                pattern_type_counts[pattern_type] = pattern_type_counts.get(pattern_type, 0) + 1
            
            return {
                'total_rules': len(all_rules),
                'category_distribution': category_counts,
                'severity_distribution': severity_counts,
                'pattern_type_distribution': pattern_type_counts
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get rule statistics: {e}")
            return {
                'total_rules': 0,
                'category_distribution': {},
                'severity_distribution': {},
                'pattern_type_distribution': {}
            }
    
    def test_rule_matching(self, test_content: str) -> Dict:
        """
        Test rule matching for debugging purposes
        
        Args:
            test_content: Content to test
            
        Returns:
            Detailed matching information
        """
        try:
            matched_rules = self.db.search_content(test_content)
            
            # Get all rules for comparison
            all_rules = self.db.get_all_active_rules()
            
            return {
                'test_content': test_content,
                'total_rules': len(all_rules),
                'matched_rules': len(matched_rules),
                'match_percentage': len(matched_rules) / len(all_rules) * 100 if all_rules else 0,
                'matched_details': matched_rules,
                'all_rules': all_rules
            }
            
        except Exception as e:
            self.logger.error(f"Rule matching test failed: {e}")
            return {
                'test_content': test_content,
                'error': str(e)
            } 