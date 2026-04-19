#!/usr/bin/env python3
"""
Quick database setup script
Initializes database tables and seeds with sample data
"""

from app import create_app, db
from app.models import SubCategory, Question

def setup_database():
    """Initialize database and seed with sample data."""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("📦 LogicBoost Database Setup")
        print("=" * 60)
        
        # Step 1: Create all tables
        print("\n1️⃣  Creating database tables...")
        try:
            db.create_all()
            print("   ✓ Tables created successfully")
        except Exception as e:
            print(f"   ❌ Error creating tables: {e}")
            return False
        
        # Step 2: Create sub-categories
        print("\n2️⃣  Setting up categories...")
        categories = [
            {'name': 'finance', 'display_name': '💰 Finance', 'description': 'Personal finance, investments, loans'},
            {'name': 'career', 'display_name': '📈 Career', 'description': 'Career decisions, job negotiations, skills'},
            {'name': 'business', 'display_name': '🏢 Business', 'description': 'Business strategies, management, entrepreneurship'},
        ]
        
        for cat_data in categories:
            existing = SubCategory.query.filter_by(name=cat_data['name']).first()
            if not existing:
                cat = SubCategory(**cat_data)
                db.session.add(cat)
                print(f"   ✓ Created: {cat_data['display_name']}")
            else:
                print(f"   - Already exists: {cat_data['display_name']}")
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"   ❌ Error creating categories: {e}")
            return False
        
        # Step 3: Create sample questions
        print("\n3️⃣  Creating sample questions...")
        
        finance_cat = SubCategory.query.filter_by(name='finance').first()
        
        sample_questions = [
            # Mini Game
            {
                'title': 'Quick Mental Math',
                'question': 'What is $25 \\times 4$?',
                'explanation': 'Simply multiply: $25 \\times 4 = 100$',
                'answer': '100',
                'mode': 'mini_game',
                'difficulty': 1,
                'time_limit': 30,
            },
            {
                'title': 'Percentage Calculation',
                'question': 'What is **20% of 150**?',
                'explanation': 'Calculate: $150 \\times 0.20 = 30$',
                'answer': '30',
                'mode': 'mini_game',
                'difficulty': 1,
                'time_limit': 45,
            },
            # Daily Challenge
            {
                'title': 'Investment Returns',
                'question': 'You invest 10,000,000 VNĐ at 6% annual interest for 3 years. How much total?',
                'explanation': 'Using compound interest: FV = 10,000,000 × (1.06)³ ≈ 11,910,160 VNĐ',
                'answer': '11910160',
                'mode': 'daily_challenge',
                'difficulty': 3,
            },
            # Real-world
            {
                'title': 'Loan Interest Calculation',
                'question': 'Borrow 100,000,000 VNĐ at 5% per year for 5 years. Calculate total interest.',
                'explanation': 'Interest = 100,000,000 × 0.05 × 5 = 25,000,000 VNĐ',
                'answer': '25000000',
                'mode': 'real_world',
                'sub_category_id': finance_cat.id if finance_cat else None,
                'difficulty': 3,
            },
        ]
        
        created_count = 0
        for q_data in sample_questions:
            if not Question.query.filter_by(title=q_data['title']).first():
                q = Question(**q_data)
                db.session.add(q)
                created_count += 1
                print(f"   ✓ {q_data['title']}")
        
        try:
            db.session.commit()
            print(f"\n   Created {created_count} new questions")
        except Exception as e:
            db.session.rollback()
            print(f"   ❌ Error creating questions: {e}")
            return False
        
        # Summary
        print("\n" + "=" * 60)
        total_qs = Question.query.count()
        print(f"✅ Database setup complete!")
        print(f"   Total questions: {total_qs}")
        print(f"   - Mini Game: {Question.query.filter_by(mode='mini_game').count()}")
        print(f"   - Daily Challenge: {Question.query.filter_by(mode='daily_challenge').count()}")
        print(f"   - Real-world: {Question.query.filter_by(mode='real_world').count()}")
        print("=" * 60)
        
        return True

if __name__ == '__main__':
    success = setup_database()
    exit(0 if success else 1)
