"""Seed the database with standards data from the JSON file."""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from database import engine, SessionLocal, init_db
from models import Standard


def seed_standards():
    """Load standards from JSON and insert into database."""
    init_db()

    seed_file = Path(__file__).parent / "seed" / "standards_data.json"
    with open(seed_file, "r", encoding="utf-8") as f:
        standards_data = json.load(f)

    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(Standard).count()
        if existing > 0:
            print(f"Database already has {existing} standards. Skipping seed.")
            return

        for item in standards_data:
            standard = Standard(
                is_number=item["is_number"],
                title=item["title"],
                year=item.get("year"),
                scope=item.get("scope", ""),
                keywords=json.dumps(item.get("keywords", [])),
                sector=item.get("sector", ""),
            )
            db.add(standard)

        db.commit()
        print(f"Successfully seeded {len(standards_data)} Indian Standards.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_standards()
