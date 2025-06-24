#!/usr/bin/env python3
"""
Test script for GuardianAI content moderation system.
Tests the system with sample content and demonstrates functionality.
"""

import argparse
import logging
import sys
import os
import json
import pandas as pd
from typing import List, Dict

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.models import DatabaseConfig
from app.guardian_ai import GuardianAI

def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level),
        format='[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def load_test_posts(data_file: str) -> List[Dict]:
    """Load test posts from CSV or JSON file"""
    if data_file.endswith('.csv'):
        df = pd.read_csv(data_file)
        return df.to_dict('records')
    elif data_file.endswith('.json'):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        raise ValueError("Unsupported file format. Use .csv or .json")

def get_sample_test_content() -> List[Dict]:
    """Get sample test content for demonstration"""
    return [
        {
            "id": "test_1",
            "content": "This is a great investment opportunity! I love this community.",
            "expected_category": "safe"
        },
        {
            "id": "test_2", 
            "content": "Fuck this company! They are so stupid and incompetent.",
            "expected_category": "profanity"
        },
        {
            "id": "test_3",
            "content": "Guaranteed 100% returns! No risk, all reward. Contact me now!",
            "expected_category": "scam"
        },
        {
            "id": "test_4",
            "content": "Insider tip: Buy AAPL now before the earnings announcement!",
            "expected_category": "fraud"
        },
        {
            "id": "test_5",
            "content": "Pump and dump group! Let's coordinate buying to drive up the price!",
            "expected_category": "manipulation"
        },
        {
            "id": "test_6",
            "content": "Click here for free money! Limited time offer!",
            "expected_category": "spam"
        }
    ]

def print_moderation_result(result, expected_category: str = None):
    """Print formatted moderation result"""
    print(f"\n📝 Post ID: {result.post_id}")
    print(f"📄 Content: {result.content[:100]}{'...' if len(result.content) > 100 else ''}")
    print(f"🎯 Score: {result.score:.2f}/3.0")
    print(f"⚡ Action: {result.action.value.upper()}")
    print(f"⏱️  Processing Time: {result.processing_time_ms}ms")
    
    if result.matched_rules:
        print(f"🚨 Matched Rules ({len(result.matched_rules)}):")
        for rule in result.matched_rules:
            print(f"   • {rule['category']}: {rule['description'] or rule['pattern']}")
    else:
        print("✅ No violations detected")
    
    print(f"💡 Explanation: {result.explanation}")
    
    if expected_category:
        matched = any(rule['category'] == expected_category for rule in result.matched_rules)
        status = "✅" if matched else "❌"
        print(f"{status} Expected category '{expected_category}': {'MATCHED' if matched else 'NOT MATCHED'}")

def run_single_tests(guardian: GuardianAI):
    """Run single content tests"""
    print("\n" + "="*60)
    print("🧪 RUNNING SINGLE CONTENT TESTS")
    print("="*60)
    
    test_content = get_sample_test_content()
    
    for test in test_content:
        print(f"\n--- Testing: {test['expected_category']} ---")
        result = guardian.moderate_content(
            post_id=test['id'],
            content=test['content']
        )
        print_moderation_result(result, test['expected_category'])

def run_batch_tests(guardian: GuardianAI, data_file: str = None):
    """Run batch tests with generated content"""
    print("\n" + "="*60)
    print("📊 RUNNING BATCH TESTS")
    print("="*60)
    
    if data_file and os.path.exists(data_file):
        print(f"Loading test data from: {data_file}")
        posts = load_test_posts(data_file)
        # Limit to first 10 posts for demonstration
        posts = posts[:10]
    else:
        print("Using sample test content")
        posts = get_sample_test_content()
    
    print(f"Testing {len(posts)} posts...")
    
    # Run batch moderation
    results = guardian.batch_moderate(posts)
    
    # Analyze results
    total_posts = len(results)
    action_counts = {}
    score_ranges = {'0-1': 0, '1-2': 0, '2-3': 0}
    avg_processing_time = 0
    
    for result in results:
        # Count actions
        action = result.action.value
        action_counts[action] = action_counts.get(action, 0) + 1
        
        # Count score ranges
        if result.score < 1:
            score_ranges['0-1'] += 1
        elif result.score < 2:
            score_ranges['1-2'] += 1
        else:
            score_ranges['2-3'] += 1
        
        avg_processing_time += result.processing_time_ms
    
    avg_processing_time /= total_posts
    
    # Print summary
    print(f"\n📈 BATCH TEST RESULTS:")
    print(f"   Total Posts: {total_posts}")
    print(f"   Average Processing Time: {avg_processing_time:.1f}ms")
    print(f"   Action Distribution:")
    for action, count in action_counts.items():
        percentage = (count / total_posts) * 100
        print(f"     • {action.upper()}: {count} ({percentage:.1f}%)")
    print(f"   Score Distribution:")
    for range_name, count in score_ranges.items():
        percentage = (count / total_posts) * 100
        print(f"     • {range_name}: {count} ({percentage:.1f}%)")

def run_performance_tests(guardian: GuardianAI):
    """Run performance tests"""
    print("\n" + "="*60)
    print("⚡ PERFORMANCE TESTS")
    print("="*60)
    
    # Test with various content lengths
    test_contents = [
        "Short test",
        "This is a medium length test content with some words",
        "This is a longer test content that contains multiple sentences and should test the performance of the moderation system with more complex content that might trigger various rules and patterns.",
        "Fuck this is a very long test content with profanity and other violations that should trigger multiple rules and test the performance of the moderation system with complex content that contains various types of violations including profanity scams fraud manipulation spam and other problematic content patterns"
    ]
    
    for i, content in enumerate(test_contents, 1):
        print(f"\n--- Performance Test {i} (Length: {len(content)} chars) ---")
        result = guardian.moderate_content(f"perf_test_{i}", content)
        print(f"Processing Time: {result.processing_time_ms}ms")
        print(f"Score: {result.score:.2f}")
        print(f"Action: {result.action.value}")

def main():
    parser = argparse.ArgumentParser(description="Test GuardianAI content moderation system")
    parser.add_argument('--host', default='localhost', help='PostgreSQL host (default: localhost)')
    parser.add_argument('--port', type=int, default=5432, help='PostgreSQL port (default: 5432)')
    parser.add_argument('--database', required=True, help='Database name')
    parser.add_argument('--username', required=True, help='Database username')
    parser.add_argument('--password', required=True, help='Database password')
    parser.add_argument('--data-file', help='Path to test data file (CSV or JSON)')
    parser.add_argument('--loglevel', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       help='Logging level (default: INFO)')
    parser.add_argument('--skip-single', action='store_true', help='Skip single content tests')
    parser.add_argument('--skip-batch', action='store_true', help='Skip batch tests')
    parser.add_argument('--skip-performance', action='store_true', help='Skip performance tests')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.loglevel)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting GuardianAI tests...")
        
        # Create database configuration
        db_config = DatabaseConfig(
            host=args.host,
            port=args.port,
            database=args.database,
            username=args.username,
            password=args.password
        )
        
        # Initialize GuardianAI
        guardian = GuardianAI(db_config)
        
        # Health check
        health = guardian.health_check()
        if health['status'] != 'healthy':
            logger.error(f"System health check failed: {health}")
            return 1
        
        print("✅ GuardianAI system ready for testing")
        
        # Run tests
        if not args.skip_single:
            run_single_tests(guardian)
        
        if not args.skip_batch:
            run_batch_tests(guardian, args.data_file)
        
        if not args.skip_performance:
            run_performance_tests(guardian)
        
        # System statistics
        print("\n" + "="*60)
        print("📊 SYSTEM STATISTICS")
        print("="*60)
        
        stats = guardian.get_system_stats()
        if 'error' not in stats:
            rule_stats = stats.get('rule_stats', {})
            mod_stats = stats.get('moderation_stats', {})
            
            print(f"Active Rules: {rule_stats.get('total_rules', 0)}")
            print(f"Categories: {list(rule_stats.get('category_distribution', {}).keys())}")
            print(f"Recent Posts Processed: {mod_stats.get('total_posts', 0)}")
            print(f"Average Score: {mod_stats.get('average_score', 0):.2f}")
            print(f"Average Processing Time: {mod_stats.get('average_processing_time_ms', 0):.1f}ms")
        
        print("\n🎉 All tests completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 