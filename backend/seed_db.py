"""Seed database with standards, relations, QCOs, and amendments."""

import json
from pathlib import Path
from database import SessionLocal
from models import (
    Standard, StandardVersion, Amendment, QCO, QCOStandard,
    StandardRelation, User, Analysis
)


SEED_DIR = Path(__file__).parent / "seed"
DATA_DIR = Path(__file__).parent / "data"


def seed_standards():
    """Load standards from JSON and seed into the database."""
    db = SessionLocal()
    try:
        # Check if already seeded
        count = db.query(Standard).count()
        if count >= 40:
            print(f"[Seed] Standards already seeded ({count} records). Skipping.")
            _seed_relations(db)
            _seed_amendments(db)
            _seed_qcos(db)
            _seed_default_user(db)
            return

        # Load standards
        standards_file = SEED_DIR / "standards_data.json"
        if not standards_file.exists():
            print("[Seed] WARNING: standards_data.json not found!")
            return

        with open(standards_file, "r", encoding="utf-8") as f:
            standards_data = json.load(f)

        # Clear existing
        db.query(Standard).delete()
        db.commit()

        for s in standards_data:
            keywords = s.get("keywords", [])
            if isinstance(keywords, list):
                keywords = json.dumps(keywords)

            standard = Standard(
                is_number=s["is_number"],
                title=s["title"],
                year=s.get("year"),
                part=s.get("part"),
                scope=s.get("scope"),
                keywords=keywords,
                sector=s.get("sector"),
                domain=s.get("domain", s.get("sector")),
                ics_code=s.get("ics_code"),
                technical_committee=s.get("technical_committee"),
                status=s.get("status", "current"),
                latest_edition_year=s.get("latest_edition_year"),
                source_url=s.get("source_url"),
                source_note=s.get("source_note", "sample"),
            )
            db.add(standard)

        db.commit()
        print(f"[Seed] Loaded {len(standards_data)} standards.")

        _seed_relations(db)
        _seed_amendments(db)
        _seed_qcos(db)
        _seed_default_user(db)

    finally:
        db.close()


def _seed_relations(db):
    """Seed inter-standard relations."""
    count = db.query(StandardRelation).count()
    if count > 0:
        return

    rq_file = SEED_DIR / "relations_qcos.json"
    if not rq_file.exists():
        print("[Seed] No relations_qcos.json found. Skipping relations.")
        return

    with open(rq_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Build IS number → ID map
    standards = db.query(Standard).all()
    is_map = {s.is_number: s.id for s in standards}

    relations = data.get("relations", [])
    added = 0
    for rel in relations:
        from_id = is_map.get(rel["from"])
        to_id = is_map.get(rel["to"])
        if from_id and to_id:
            db.add(StandardRelation(
                from_standard_id=from_id,
                to_standard_id=to_id,
                relation_type=rel["type"],
            ))
            added += 1

    db.commit()
    print(f"[Seed] Loaded {added} relations.")


def _seed_amendments(db):
    """Seed amendments."""
    count = db.query(Amendment).count()
    if count > 0:
        return

    rq_file = SEED_DIR / "relations_qcos.json"
    if not rq_file.exists():
        return

    with open(rq_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    standards = db.query(Standard).all()
    is_map = {s.is_number: s.id for s in standards}

    amendments = data.get("amendments", [])
    added = 0
    for amd in amendments:
        std_id = is_map.get(amd["standard"])
        if std_id:
            db.add(Amendment(
                standard_id=std_id,
                amendment_no=amd["amendment_no"],
                date=amd.get("date"),
                summary=amd.get("summary"),
            ))
            added += 1

    db.commit()
    print(f"[Seed] Loaded {added} amendments.")


def _seed_qcos(db):
    """Seed QCOs and their standard linkages."""
    count = db.query(QCO).count()
    if count > 0:
        return

    rq_file = SEED_DIR / "relations_qcos.json"
    if not rq_file.exists():
        return

    with open(rq_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    standards = db.query(Standard).all()
    is_map = {s.is_number: s.id for s in standards}

    qcos = data.get("qcos", [])
    added = 0
    for q in qcos:
        qco = QCO(
            name=q["name"],
            product=q.get("product"),
            notification_ref=q.get("notification_ref"),
            effective_date=q.get("effective_date"),
            certification_scheme=q.get("certification_scheme"),
            notes=q.get("notes"),
        )
        db.add(qco)
        db.flush()

        for is_num in q.get("standards", []):
            std_id = is_map.get(is_num)
            if std_id:
                db.add(QCOStandard(qco_id=qco.id, standard_id=std_id))

        added += 1

    db.commit()
    print(f"[Seed] Loaded {added} QCOs.")


def _seed_default_user(db):
    """Seed a default procurement officer user."""
    count = db.query(User).count()
    if count > 0:
        return

    db.add(User(
        name="Procurement Officer",
        role="officer",
        language="en",
    ))
    db.add(User(
        name="Admin",
        role="admin",
        language="en",
    ))
    db.commit()
    print("[Seed] Created default users.")


if __name__ == "__main__":
    from database import init_db
    init_db()
    seed_standards()
