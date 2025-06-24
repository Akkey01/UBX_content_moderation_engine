import random
import json
import csv
import pandas as pd
from datetime import datetime, timedelta
import uuid
import os
import argparse
import logging
from collections import Counter
from typing import List, Dict, Optional

class FinanceContentGenerator:
    """
    Generates synthetic finance-related posts for content moderation testing.
    """
    def __init__(self):
        self.finance_topics = {
            "trading": [
                "stock analysis", "market trends", "technical indicators", "portfolio diversification",
                "risk management", "day trading", "swing trading", "options trading", "forex trading"
            ],
            "accounting": [
                "financial statements", "cash flow analysis", "balance sheet review", "income statement",
                "budgeting", "expense tracking", "tax preparation", "financial reporting", "audit procedures"
            ],
            "loans": [
                "mortgage rates", "personal loans", "business loans", "student loans", "loan refinancing",
                "credit scores", "loan applications", "debt consolidation", "interest rates"
            ],
            "investment": [
                "mutual funds", "ETFs", "bonds", "retirement planning", "401k strategies", "IRA contributions",
                "dividend investing", "value investing", "growth stocks", "index funds"
            ],
            "cash_flow": [
                "monthly budgets", "expense management", "savings goals", "emergency funds", "income tracking",
                "financial planning", "debt payments", "investment allocations", "cash reserves"
            ]
        }
        self.safe_templates = [
            "Just completed my {topic} analysis for {detail}. The {metric} looks promising this quarter.",
            "Looking for advice on {topic}. Has anyone tried {detail} strategies?",
            "Monthly {topic} update: {detail} improved by {percentage}% compared to last month.",
            "Sharing my {topic} experience with {detail}. Key lesson: {insight}.",
            "Question about {topic}: How do you approach {detail} in volatile markets?",
            "Finally understood {detail} in {topic}. The {concept} principle really clicked!",
            "Weekly {topic} review: {detail} performance exceeded expectations.",
            "Beginner's guide to {topic}: Start with {detail} before moving to advanced strategies.",
            "Market analysis: {topic} sector showing strength in {detail} metrics.",
            "Personal finance win: Improved my {topic} by focusing on {detail}.",
            "Professional insight: {topic} trends suggest {detail} will be crucial next quarter.",
            "Educational content: Understanding {detail} is essential for {topic} success."
        ]
        self.financial_metrics = [
            "15.2", "8.7", "23.5", "12.1", "6.8", "18.9", "4.3", "11.7", "9.4", "22.1"
        ]
        self.financial_insights = [
            "diversification reduces risk", "compound interest works best long-term",
            "cash flow timing matters", "debt-to-equity ratios indicate stability",
            "market volatility creates opportunities", "consistent investing beats timing",
            "emergency funds provide security", "tax efficiency maximizes returns"
        ]
        self.financial_concepts = [
            "risk-reward", "time value of money", "asset allocation", "dollar-cost averaging",
            "compound growth", "liquidity management", "market efficiency", "diversification"
        ]
        self.mild_violations = [
            "This {service} is a complete scam. {company} stole my money and disappeared.",
            "URGENT: {service} rates are skyrocketing! Act now or lose thousands!",
            "Insider tip: {stock} is about to explode! Buy before it's too late!",
            "Secret {strategy} that banks don't want you to know! DM me for details.",
            "WARNING: {company} is hiding massive losses. Sell everything NOW!",
            "I made ${amount} in one day using this {method}. It's so easy!",
            "Financial advisors hate this one trick! {strategy} guaranteed returns!",
            "BREAKING: {service} bankruptcy imminent. Withdraw funds immediately!",
            "Exclusive {opportunity} available for next 24 hours only! Don't miss out!",
            "Proven {system} beats the market 99% of the time. Limited spots available!"
        ]
        self.moderate_violations = [
            "Selling guaranteed {return}% monthly returns. No risk, all reward. Contact me privately.",
            "Ponzi scheme that actually works! Join my {program} before it's too late.",
            "Leaked {document} from {institution}. Download before they remove it.",
            "Bypass {regulation} with this offshore {service}. Completely legal loophole.",
            "Fake {credential} certificates available. Pass any {exam} guaranteed.",
            "Pump and dump {stock} group. Coordinate buying to drive up price.",
            "Tax evasion strategies that work. Reduce your {tax_type} to zero legally.",
            "Insider trading network. Get tips before major {event} announcements.",
            "Money laundering service. Clean your {currency} through {method}.",
            "Identity theft for {service}. Create new credit profile instantly."
        ]
        self.severe_violations = [
            "Selling stolen {data_type} from {institution}. Verified accounts available.",
            "Counterfeit {currency} operation. High quality, undetectable bills.",
            "Hacking services for {platform}. Access any account for ${price}.",
            "Embezzlement scheme. Help me move ${amount} from {source}.",
            "Terrorist financing network. Contribute to {cause} anonymously.",
            "Drug money laundering. Turn dirty cash into clean {asset}.",
            "Human trafficking profits. Invest in our {operation} for high returns.",
            "Weapons trafficking finance. Fund our {operation} for profit sharing.",
            "Child exploitation revenue. Invest in our {network} for guaranteed returns.",
            "Ransomware profits. Share in our {attack} earnings."
        ]
        self.replacement_terms = {
            "service": ["loan service", "trading platform", "investment fund", "financial advisor", "crypto exchange"],
            "company": ["FinanceCorpXYZ", "TradingPlatformABC", "LoanServiceDEF", "InvestmentFirmGHI", "CryptoExchangeJKL"],
            "stock": ["AAPL", "GOOGL", "TSLA", "MSFT", "AMZN", "META", "NVDA"],
            "strategy": ["arbitrage strategy", "options strategy", "forex strategy", "crypto strategy"],
            "method": ["trading algorithm", "investment system", "financial model", "risk calculation"],
            "amount": ["5000", "10000", "25000", "50000", "100000"],
            "opportunity": ["investment opportunity", "trading opportunity", "loan opportunity"],
            "system": ["trading system", "investment system", "financial system"],
            "return": ["15", "25", "50", "100", "200"],
            "program": ["investment program", "trading program", "financial program"],
            "document": ["financial report", "audit document", "regulatory filing", "internal memo"],
            "institution": ["major bank", "investment firm", "regulatory agency", "financial institution"],
            "regulation": ["KYC requirements", "tax reporting", "financial regulations", "compliance rules"],
            "credential": ["CPA", "CFA", "financial advisor", "trading"],
            "exam": ["CPA exam", "CFA exam", "financial certification", "trading license"],
            "tax_type": ["income tax", "capital gains tax", "corporate tax"],
            "event": ["earnings", "merger", "acquisition", "regulatory"],
            "currency": ["bitcoin", "ethereum", "cash", "digital assets"],
            "data_type": ["credit reports", "bank statements", "financial records", "trading accounts"],
            "platform": ["trading platforms", "banking systems", "investment accounts"],
            "price": ["500", "1000", "2500", "5000"],
            "source": ["company accounts", "investment funds", "client deposits"],
            "cause": ["terrorist organization", "extremist group", "illegal operation"],
            "asset": ["real estate", "investments", "business assets"],
            "operation": ["trafficking operation", "criminal enterprise", "illegal business"],
            "network": ["criminal network", "illegal operation", "underground business"],
            "attack": ["ransomware attack", "cyber attack", "financial hack"]
        }
        self.user_personas = [
            {"username": "financial_advisor_pro", "style": "professional", "topics": ["investment", "accounting"]},
            {"username": "trading_enthusiast", "style": "enthusiastic", "topics": ["trading", "investment"]},
            {"username": "loan_specialist", "style": "helpful", "topics": ["loans", "cash_flow"]},
            {"username": "accounting_guru", "style": "analytical", "topics": ["accounting", "cash_flow"]},
            {"username": "investment_newbie", "style": "curious", "topics": ["investment", "cash_flow"]},
            {"username": "day_trader_mike", "style": "aggressive", "topics": ["trading"]},
            {"username": "financial_planner", "style": "methodical", "topics": ["investment", "cash_flow"]},
            {"username": "crypto_believer", "style": "enthusiastic", "topics": ["trading", "investment"]},
            {"username": "scammer_finance", "style": "deceptive", "topics": ["scam"]},
            {"username": "pump_dumper", "style": "manipulative", "topics": ["trading"]},
            {"username": "spam_loans", "style": "promotional", "topics": ["loans"]},
            {"username": "fake_advisor", "style": "deceptive", "topics": ["investment"]}
        ]
        self.categories = {
            "safe": {"severity": 0, "action": "approve"},
            "mild_violation": {"severity": 1, "action": "review"},
            "moderate_violation": {"severity": 2, "action": "flag"},
            "severe_violation": {"severity": 3, "action": "block"}
        }

    def generate_safe_post(self) -> Dict:
        topic = random.choice(list(self.finance_topics.keys()))
        detail = random.choice(self.finance_topics[topic])
        template = random.choice(self.safe_templates)
        safe_users = [u for u in self.user_personas if u["style"] not in ["deceptive", "manipulative", "promotional"]]
        user = random.choice(safe_users)
        metric = random.choice(self.financial_metrics)
        percentage = random.choice(self.financial_metrics)
        insight = random.choice(self.financial_insights)
        concept = random.choice(self.financial_concepts)
        content = template.format(
            topic=topic,
            detail=detail,
            metric=metric,
            percentage=percentage,
            insight=insight,
            concept=concept
        )
        return {
            "id": str(uuid.uuid4()),
            "username": user["username"],
            "content": content,
            "category": "safe",
            "severity": 0,
            "expected_action": "approve",
            "timestamp": self._random_timestamp()
        }

    def generate_mild_violation_post(self) -> Dict:
        template = random.choice(self.mild_violations)
        content = self._fill_template(template)
        problem_users = [u for u in self.user_personas if u["style"] in ["aggressive", "promotional"]]
        user = random.choice(problem_users)
        return {
            "id": str(uuid.uuid4()),
            "username": user["username"],
            "content": content,
            "category": "mild_violation",
            "severity": 1,
            "expected_action": "review",
            "timestamp": self._random_timestamp()
        }

    def generate_moderate_violation_post(self) -> Dict:
        template = random.choice(self.moderate_violations)
        content = self._fill_template(template)
        deceptive_users = [u for u in self.user_personas if u["style"] in ["deceptive", "manipulative"]]
        user = random.choice(deceptive_users)
        return {
            "id": str(uuid.uuid4()),
            "username": user["username"],
            "content": content,
            "category": "moderate_violation",
            "severity": 2,
            "expected_action": "flag",
            "timestamp": self._random_timestamp()
        }

    def generate_severe_violation_post(self) -> Dict:
        template = random.choice(self.severe_violations)
        content = self._fill_template(template)
        criminal_users = [u for u in self.user_personas if u["style"] == "deceptive"]
        user = random.choice(criminal_users)
        return {
            "id": str(uuid.uuid4()),
            "username": user["username"],
            "content": content,
            "category": "severe_violation",
            "severity": 3,
            "expected_action": "block",
            "timestamp": self._random_timestamp()
        }

    def _fill_template(self, template: str) -> str:
        content = template
        for placeholder, options in self.replacement_terms.items():
            if f"{{{placeholder}}}" in content:
                content = content.replace(f"{{{placeholder}}}", random.choice(options))
        return content

    def _random_timestamp(self) -> str:
        now = datetime.now()
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        return timestamp.isoformat()

    def generate_dataset(
        self,
        total_posts: int = 200,
        safe_ratio: float = 0.5,
        mild_ratio: float = 0.25,
        moderate_ratio: float = 0.15,
        severe_ratio: float = 0.1
    ) -> List[Dict]:
        if not abs(safe_ratio + mild_ratio + moderate_ratio + severe_ratio - 1.0) < 0.01:
            raise ValueError("Ratios must sum to 1.0")
        dataset = []
        safe_count = int(total_posts * safe_ratio)
        mild_count = int(total_posts * mild_ratio)
        moderate_count = int(total_posts * moderate_ratio)
        severe_count = total_posts - safe_count - mild_count - moderate_count
        for _ in range(safe_count):
            dataset.append(self.generate_safe_post())
        for _ in range(mild_count):
            dataset.append(self.generate_mild_violation_post())
        for _ in range(moderate_count):
            dataset.append(self.generate_moderate_violation_post())
        for _ in range(severe_count):
            dataset.append(self.generate_severe_violation_post())
        random.shuffle(dataset)
        return dataset

    def save_dataset(
        self,
        dataset: List[Dict],
        format_type: str = "json",
        outdir: str = "data",
        overwrite: bool = False
    ) -> Optional[str]:
        os.makedirs(outdir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if format_type.lower() == "json":
            filename = os.path.join(outdir, f"finance_content_dataset_{timestamp}.json")
        elif format_type.lower() == "csv":
            filename = os.path.join(outdir, f"finance_content_dataset_{timestamp}.csv")
        else:
            logging.error(f"Unknown format: {format_type}")
            return None
        if os.path.exists(filename) and not overwrite:
            logging.warning(f"File {filename} already exists. Use --overwrite to replace.")
            return None
        if format_type.lower() == "json":
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=2, ensure_ascii=False)
        elif format_type.lower() == "csv":
            df = pd.json_normalize(dataset)
            df.to_csv(filename, index=False, encoding='utf-8')
        logging.info(f"Dataset saved to: {filename}")
        return filename

    def generate_statistics(self, dataset: List[Dict]) -> Dict:
        stats = {
            "total_posts": len(dataset),
            "category_distribution": Counter(post["category"] for post in dataset),
            "severity_distribution": Counter(post["severity"] for post in dataset),
            "user_distribution": Counter(post["username"] for post in dataset)
        }
        return stats

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic finance content posts.")
    parser.add_argument('--total-posts', type=int, default=200, help='Total number of posts to generate (default: 200)')
    parser.add_argument('--safe-ratio', type=float, default=0.5, help='Ratio of safe posts (default: 0.5)')
    parser.add_argument('--mild-ratio', type=float, default=0.25, help='Ratio of mild violation posts (default: 0.25)')
    parser.add_argument('--moderate-ratio', type=float, default=0.15, help='Ratio of moderate violation posts (default: 0.15)')
    parser.add_argument('--severe-ratio', type=float, default=0.1, help='Ratio of severe violation posts (default: 0.1)')
    parser.add_argument('--outdir', type=str, default='data', help='Output directory (default: data)')
    parser.add_argument('--formats', type=str, nargs='+', default=['json', 'csv'], choices=['json', 'csv'], help='Output formats (default: json csv)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed (default: 42)')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite output files if they exist')
    parser.add_argument('--loglevel', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='Logging level (default: INFO)')
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.loglevel), format='[%(levelname)s] %(message)s')

    logging.info("SMART CONTENT MODERATION ENGINE - FINANCE FEED GENERATOR")
    random.seed(args.seed)
    generator = FinanceContentGenerator()
    logging.info(f"Generating {args.total_posts} posts (safe: {args.safe_ratio}, mild: {args.mild_ratio}, moderate: {args.moderate_ratio}, severe: {args.severe_ratio})")
    dataset = generator.generate_dataset(
        total_posts=args.total_posts,
        safe_ratio=args.safe_ratio,
        mild_ratio=args.mild_ratio,
        moderate_ratio=args.moderate_ratio,
        severe_ratio=args.severe_ratio
    )
    logging.info(f"Generated {len(dataset)} posts successfully!")
    for fmt in args.formats:
        generator.save_dataset(dataset, fmt, outdir=args.outdir, overwrite=args.overwrite)
    stats = generator.generate_statistics(dataset)
    logging.info(f"Dataset Statistics: Total Posts: {stats['total_posts']}, Categories: {dict(stats['category_distribution'])}, Severities: {dict(stats['severity_distribution'])}")
    logging.info("Dataset generation complete!")

if __name__ == "__main__":
    main() 