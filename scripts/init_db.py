#!/usr/bin/env python3
"""
Database initialization script for GuardianAI content moderation system.
Sets up PostgreSQL database, creates tables, and populates sample rules.
"""

import argparse
import logging
import sys
import os

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

def main():
    parser = argparse.ArgumentParser(description="Initialize GuardianAI database")
    parser.add_argument('--host', default='localhost', help='PostgreSQL host (default: localhost)')
    parser.add_argument('--port', type=int, default=5432, help='PostgreSQL port (default: 5432)')
    parser.add_argument('--database', required=True, help='Database name')
    parser.add_argument('--username', required=True, help='Database username')
    parser.add_argument('--password', required=True, help='Database password')
    parser.add_argument('--loglevel', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       help='Logging level (default: INFO)')
    parser.add_argument('--skip-sample-data', action='store_true', 
                       help='Skip populating sample rules')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.loglevel)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Initializing GuardianAI database...")
        
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
        
        # Perform health check
        logger.info("Performing health check...")
        health = guardian.health_check()
        
        if health['status'] == 'healthy':
            logger.info("✅ Database connection successful")
        else:
            logger.error(f"❌ Database health check failed: {health}")
            return 1
        
        # Initialize sample data if requested
        if not args.skip_sample_data:
            logger.info("Populating sample rules...")
            guardian.initialize_sample_data()
            logger.info("✅ Sample rules populated successfully")
        else:
            logger.info("Skipping sample data population")
        
        # Get system statistics
        logger.info("Getting system statistics...")
        stats = guardian.get_system_stats()
        
        if 'error' not in stats:
            rule_stats = stats.get('rule_stats', {})
            logger.info(f"✅ System initialized successfully")
            logger.info(f"   - Total rules: {rule_stats.get('total_rules', 0)}")
            logger.info(f"   - Categories: {list(rule_stats.get('category_distribution', {}).keys())}")
        else:
            logger.error(f"❌ Failed to get system stats: {stats['error']}")
            return 1
        
        logger.info("🎉 Database initialization complete!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 