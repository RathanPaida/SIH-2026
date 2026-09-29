"""Lifecycle and edition verification service.

Deterministic checks (not LLM):
  - Is the cited standard current, superseded, or withdrawn?
  - Is the cited edition the latest?
  - How many amendments exist?
  - What is the supersession chain?
"""

from database import SessionLocal
from models import Standard, Amendment, StandardRelation


def verify_lifecycle(is_number: str) -> dict:
    """
    Verify lifecycle status of a standard.
    Returns verification dict with status, edition check, amendments, and supersession info.
    """
    db = SessionLocal()
    try:
        standard = db.query(Standard).filter(Standard.is_number == is_number).first()
        if not standard:
            return {
                "is_number": is_number,
                "found": False,
                "lifecycle_ok": False,
                "edition_ok": False,
                "status": "not_found",
                "message": f"Standard {is_number} not found in catalogue — unverified citation",
                "amendments": [],
                "supersession_chain": [],
            }

        # Check amendments
        amendments = db.query(Amendment).filter(
            Amendment.standard_id == standard.id
        ).order_by(Amendment.amendment_no).all()

        amendments_list = [
            {
                "amendment_no": a.amendment_no,
                "date": a.date,
                "summary": a.summary,
            }
            for a in amendments
        ]

        # Check if this is the latest edition
        # Extract base IS number (without year)
        base_num = is_number.split(":")[0].strip() if ":" in is_number else is_number
        edition_ok = True
        latest_edition = is_number
        supersession_chain = []

        if standard.status == "superseded":
            # Find what supersedes this
            superseding = db.query(StandardRelation).filter(
                StandardRelation.to_standard_id == standard.id,
                StandardRelation.relation_type == "SUPERSEDES",
            ).first()

            if superseding:
                newer = db.query(Standard).filter(Standard.id == superseding.from_standard_id).first()
                if newer:
                    latest_edition = newer.is_number
                    supersession_chain = [is_number, newer.is_number]

            edition_ok = False

        elif standard.latest_edition_year and standard.year:
            if standard.year < standard.latest_edition_year:
                edition_ok = False

        lifecycle_ok = standard.status in ("current", "amended")

        status_messages = {
            "current": f"{is_number} is current",
            "amended": f"{is_number} is current with {len(amendments_list)} amendment(s)",
            "superseded": f"{is_number} is SUPERSEDED — use {latest_edition} instead",
            "withdrawn": f"{is_number} has been WITHDRAWN",
            "under_revision": f"{is_number} is under revision — check for updates",
        }

        return {
            "is_number": is_number,
            "found": True,
            "lifecycle_ok": lifecycle_ok,
            "edition_ok": edition_ok,
            "status": standard.status,
            "message": status_messages.get(standard.status, f"Status: {standard.status}"),
            "latest_edition": latest_edition,
            "year": standard.year,
            "latest_edition_year": standard.latest_edition_year,
            "amendments": amendments_list,
            "amendment_count": len(amendments_list),
            "supersession_chain": supersession_chain,
        }
    finally:
        db.close()


def verify_standard_for_recommendation(standard_id: int) -> dict:
    """Verify a standard's lifecycle for use in recommendations."""
    db = SessionLocal()
    try:
        standard = db.query(Standard).filter(Standard.id == standard_id).first()
        if not standard:
            return {"lifecycle_ok": False, "edition_ok": False, "status": "not_found"}

        return verify_lifecycle(standard.is_number)
    finally:
        db.close()


def check_cited_standards(text: str) -> list[dict]:
    """
    Find IS number citations in text and verify each one.
    Detects patterns like: IS 269, IS:269-2015, IS 1786 (Part 1), IS 456:2000
    """
    import re
    patterns = [
        r'IS\s*:?\s*(\d{2,5})\s*(?:[-:]\s*(\d{4}))?',
        r'IS\s+(\d{2,5})\s*\(Part\s+\d+\)\s*(?:[-:]\s*(\d{4}))?',
    ]

    found_citations = set()
    results = []

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            num = match.group(1)
            year = match.group(2) if len(match.groups()) > 1 else None
            citation = f"IS {num}" + (f":{year}" if year else "")

            if citation not in found_citations:
                found_citations.add(citation)
                # Try to find the exact match or base match
                verification = _find_and_verify(num, year)
                verification["cited_as"] = match.group(0).strip()
                results.append(verification)

    return results


def _find_and_verify(is_num: str, year: str = None) -> dict:
    """Find a standard by number (with optional year) and verify it."""
    db = SessionLocal()
    try:
        # Try exact match with year
        if year:
            exact = f"IS {is_num}:{year}"
            standard = db.query(Standard).filter(Standard.is_number == exact).first()
            if standard:
                result = verify_lifecycle(exact)
                return result

        # Try to find any edition
        like_pattern = f"IS {is_num}%"
        standards = db.query(Standard).filter(
            Standard.is_number.like(like_pattern)
        ).order_by(Standard.year.desc()).all()

        if standards:
            # Found standards with this number — use the latest
            latest = standards[0]
            result = verify_lifecycle(latest.is_number)

            if year and latest.year and int(year) < latest.year:
                result["edition_ok"] = False
                result["message"] = f"Cited edition ({year}) is outdated — latest is {latest.is_number}"
                result["suggested_replacement"] = latest.is_number

            return result

        return {
            "is_number": f"IS {is_num}" + (f":{year}" if year else ""),
            "found": False,
            "lifecycle_ok": False,
            "edition_ok": False,
            "status": "not_found",
            "message": f"IS {is_num} not found in catalogue",
            "amendments": [],
            "supersession_chain": [],
        }
    finally:
        db.close()
