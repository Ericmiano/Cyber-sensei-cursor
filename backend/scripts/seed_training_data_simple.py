"""
Simple seed script for training data
Uses synchronous SQLAlchemy for easier debugging
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.training import TrainingModule, Lesson, Achievement
from app.core.database import Base
import uuid

# Convert async URL to sync URL
sync_db_url = settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
engine = create_engine(sync_db_url)


def seed_data():
    """Seed training data."""
    print("Seeding training data...")
    
    with Session(engine) as session:
        try:
            # Check if data already exists
            existing_modules = session.execute(select(TrainingModule)).scalars().all()
            
            if existing_modules:
                print("✅ Training modules already exist. Skipping seed.")
                return

            print("Creating training modules...")
            
            # Module 1: Cybersecurity Fundamentals
            module1 = TrainingModule(
                id=uuid.UUID('00000000-0000-0000-0000-000000000001'),
                title="Cybersecurity Fundamentals",
                description="Master the core concepts of information security, threat landscapes, and defense strategies.",
                category="fundamentals",
                difficulty="beginner",
                icon="Shield",
                order_index=1,
                duration_minutes=180,
                total_lessons=12,
            )
            session.add(module1)
            
            # Module 2: Network Security
            module2 = TrainingModule(
                id=uuid.UUID('00000000-0000-0000-0000-000000000002'),
                title="Network Security",
                description="Learn to protect networks from intrusions, monitor traffic, and implement firewalls.",
                category="networking",
                difficulty="intermediate",
                icon="Network",
                order_index=2,
                duration_minutes=240,
                total_lessons=15,
            )
            session.add(module2)
            
            # Module 3: Cryptography
            module3 = TrainingModule(
                id=uuid.UUID('00000000-0000-0000-0000-000000000003'),
                title="Cryptography Essentials",
                description="Understand encryption, hashing, digital signatures, and key management.",
                category="fundamentals",
                difficulty="intermediate",
                icon="Lock",
                order_index=3,
                duration_minutes=150,
                total_lessons=10,
            )
            session.add(module3)
            
            # Module 4: Ethical Hacking
            module4 = TrainingModule(
                id=uuid.UUID('00000000-0000-0000-0000-000000000004'),
                title="Ethical Hacking",
                description="Learn penetration testing, vulnerability assessment, and ethical hacking methodologies.",
                category="offensive",
                difficulty="advanced",
                icon="Bug",
                order_index=4,
                duration_minutes=360,
                total_lessons=20,
            )
            session.add(module4)
            
            # Module 5: Secure Coding
            module5 = TrainingModule(
                id=uuid.UUID('00000000-0000-0000-0000-000000000005'),
                title="Secure Coding Practices",
                description="Write secure code, prevent common vulnerabilities, and follow security best practices.",
                category="development",
                difficulty="intermediate",
                icon="Code",
                order_index=5,
                duration_minutes=210,
                total_lessons=14,
            )
            session.add(module5)
            
            # Module 6: Incident Response
            module6 = TrainingModule(
                id=uuid.UUID('00000000-0000-0000-0000-000000000006'),
                title="Incident Response",
                description="Handle security incidents, perform forensic analysis, and implement recovery procedures.",
                category="operations",
                difficulty="advanced",
                icon="AlertTriangle",
                order_index=6,
                duration_minutes=270,
                total_lessons=16,
            )
            session.add(module6)
            
            # Module 7: Cloud Security
            module7 = TrainingModule(
                id=uuid.UUID('00000000-0000-0000-0000-000000000007'),
                title="Cloud Security",
                description="Secure cloud infrastructure, manage identities, and protect cloud-native applications.",
                category="infrastructure",
                difficulty="advanced",
                icon="Server",
                order_index=7,
                duration_minutes=300,
                total_lessons=18,
            )
            session.add(module7)
            
            print("✅ Created 7 training modules")
            
            # Create lessons for Module 1
            print("Creating lessons for Module 1...")
            lessons = [
                ("Introduction to Cybersecurity", "Learn the basics of cybersecurity and why it matters."),
                ("The CIA Triad", "Understand Confidentiality, Integrity, and Availability."),
                ("Types of Cyber Threats", "Explore malware, phishing, and other common threats."),
                ("Authentication & Access Control", "Learn about passwords, MFA, and access management."),
                ("Security Policies and Procedures", "Understand organizational security frameworks."),
                ("Risk Management", "Learn to identify, assess, and mitigate risks."),
                ("Security Frameworks", "Explore NIST, ISO 27001, and other frameworks."),
                ("Compliance and Regulations", "Understand GDPR, HIPAA, and compliance requirements."),
                ("Security Awareness", "Learn about social engineering and user training."),
                ("Physical Security", "Understand the importance of physical access controls."),
                ("Security Tools Overview", "Get familiar with common security tools."),
                ("Career Paths in Cybersecurity", "Explore different roles in cybersecurity."),
            ]
            
            for i, (title, content) in enumerate(lessons, 1):
                lesson = Lesson(
                    id=uuid.uuid4(),
                    module_id=module1.id,
                    title=title,
                    content=content,
                    order_index=i,
                    duration_minutes=15,
                    xp_reward=50,
                    difficulty="beginner",
                )
                session.add(lesson)
            
            print(f"✅ Created {len(lessons)} lessons for Module 1")
            
            # Create achievements
            print("Creating achievements...")
            achievements = [
                ("first_steps", "First Steps", "Complete your first lesson", "🎯", "lessons", 1, 25),
                ("quick_learner", "Quick Learner", "Complete 5 lessons", "⚡", "lessons", 5, 50),
                ("dedicated", "Dedicated", "Complete 10 lessons", "📚", "lessons", 10, 100),
                ("streak_starter", "Streak Starter", "Maintain a 3-day streak", "🔥", "streak", 3, 50),
                ("streak_master", "Streak Master", "Maintain a 7-day streak", "🔥", "streak", 7, 100),
                ("streak_legend", "Streak Legend", "Maintain a 30-day streak", "⭐", "streak", 30, 500),
                ("quiz_novice", "Quiz Novice", "Pass 5 quizzes", "✅", "quizzes", 5, 75),
                ("quiz_master", "Quiz Master", "Pass 25 quizzes", "🏆", "quizzes", 25, 250),
                ("hands_on", "Hands-On", "Complete 5 exercises", "🛠️", "exercises", 5, 75),
                ("practitioner", "Practitioner", "Complete 15 exercises", "💪", "exercises", 15, 200),
                ("xp_hunter", "XP Hunter", "Earn 1000 XP", "💎", "xp", 1000, 100),
                ("xp_legend", "XP Legend", "Earn 5000 XP", "👑", "xp", 5000, 500),
                ("module_complete", "Module Master", "Complete a full module", "🎓", "modules", 1, 200),
                ("curious_mind", "Curious Mind", "Send 50 chat messages", "🧠", "chat", 50, 100),
            ]
            
            for key, title, desc, icon, req_type, req_val, xp in achievements:
                achievement = Achievement(
                    id=uuid.uuid4(),
                    achievement_key=key,
                    title=title,
                    description=desc,
                    icon=icon,
                    requirement_type=req_type,
                    requirement_value=req_val,
                    xp_reward=xp,
                )
                session.add(achievement)
            
            print(f"✅ Created {len(achievements)} achievements")
            
            session.commit()
            print("\n🎉 Training data seeded successfully!")
            print("\nSummary:")
            print("  - 7 training modules")
            print("  - 12 lessons for Module 1: Cybersecurity Fundamentals")
            print("  - 14 achievements")
            
        except Exception as e:
            print(f"\n❌ Error seeding data: {e}")
            session.rollback()
            raise


if __name__ == "__main__":
    seed_data()
