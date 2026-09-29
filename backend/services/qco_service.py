"""QCO and certification verification service.

Deterministic checks:
  - Does the standard/product fall under a Quality Control Order?
  - Is ISI mark / CRS certification required?
  - Does the tender text mention the required certification?
"""

from database import SessionLocal
from models import Standard, QCO, QCOStandard


def verify_qco(standard_id: int) -> dict:
    """
    Check if a standard is linked to any QCO.
    Returns QCO details if mandatory.
    """
    db = SessionLocal()
    try:
        links = db.query(QCOStandard).filter(QCOStandard.standard_id == standard_id).all()
        if not links:
            return {
                "standard_id": standard_id,
                "qco_mandatory": False,
                "qco_applicable": "not_applicable",
                "message": "No QCO applicable for this standard",
                "qcos": [],
            }

        qcos_list = []
        for link in links:
            qco = db.query(QCO).filter(QCO.id == link.qco_id).first()
            if qco:
                qcos_list.append({
                    "qco_id": qco.id,
                    "name": qco.name,
                    "product": qco.product,
                    "notification_ref": qco.notification_ref,
                    "effective_date": qco.effective_date,
                    "certification_scheme": qco.certification_scheme,
                    "notes": qco.notes,
                })

        return {
            "standard_id": standard_id,
            "qco_mandatory": True,
            "qco_applicable": "mandatory",
            "message": f"QCO mandatory — {qcos_list[0]['certification_scheme']} certification required",
            "certification_scheme": qcos_list[0]["certification_scheme"] if qcos_list else None,
            "qcos": qcos_list,
        }
    finally:
        db.close()


def check_tender_qco_compliance(text: str, recommended_standard_ids: list[int]) -> list[dict]:
    """
    Check if the tender text mentions required certifications for QCO-mandatory standards.
    Returns findings for missing QCO/certification requirements.
    """
    text_lower = text.lower()
    findings = []

    certification_keywords = {
        "ISI Mark": ["isi mark", "isi marked", "isi certification", "bis certification", "bis certified"],
        "CRS": ["crs", "compulsory registration", "registered under crs"],
        "ISI Mark (CM/L)": ["isi mark", "cm/l", "certification mark"],
    }

    db = SessionLocal()
    try:
        for std_id in recommended_standard_ids:
            qco_info = verify_qco(std_id)
            if not qco_info["qco_mandatory"]:
                continue

            standard = db.query(Standard).filter(Standard.id == std_id).first()
            if not standard:
                continue

            cert_scheme = qco_info.get("certification_scheme", "ISI Mark")
            keywords = certification_keywords.get(cert_scheme, ["isi mark", "certification"])

            # Check if tender mentions the required certification
            mentioned = any(kw in text_lower for kw in keywords)

            if not mentioned:
                findings.append({
                    "kind": "risk",
                    "severity": "high",
                    "title": f"Missing {cert_scheme} requirement for {standard.is_number}",
                    "description": (
                        f"Standard {standard.is_number} ({standard.title}) is under QCO — "
                        f"{cert_scheme} certification is mandatory, but the tender does not "
                        f"explicitly require {cert_scheme} for this product."
                    ),
                    "standard_id": std_id,
                    "is_number": standard.is_number,
                    "qco_name": qco_info["qcos"][0]["name"] if qco_info["qcos"] else "",
                    "proposed_fix": f"Add requirement: 'Product shall carry valid {cert_scheme} as per {standard.is_number}'",
                })
    finally:
        db.close()

    return findings


def get_all_qcos() -> list[dict]:
    """Get all QCOs with linked standards for the standards library."""
    db = SessionLocal()
    try:
        qcos = db.query(QCO).all()
        result = []
        for q in qcos:
            links = db.query(QCOStandard).filter(QCOStandard.qco_id == q.id).all()
            std_numbers = []
            for link in links:
                std = db.query(Standard).filter(Standard.id == link.standard_id).first()
                if std:
                    std_numbers.append(std.is_number)
            result.append({
                "id": q.id,
                "name": q.name,
                "product": q.product,
                "notification_ref": q.notification_ref,
                "effective_date": q.effective_date,
                "certification_scheme": q.certification_scheme,
                "notes": q.notes,
                "standards": std_numbers,
            })
        return result
    finally:
        db.close()
