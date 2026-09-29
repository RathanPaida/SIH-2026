"""Audit engine — gap detection, conflict detection, and risk assessment.

Validates the tender specification itself:
  - Coverage matrix: which requirements are covered by recommended standards
  - Gap detection: missing categories per domain checklist
  - Conflict detection: incompatible values, mismatched standards
  - Risk scoring: weighted composite of all findings
"""

import json
import re
from pathlib import Path
from typing import Optional


DATA_DIR = Path(__file__).parent.parent / "data"


def load_domain_checklists() -> dict:
    """Load domain checklists for gap detection."""
    checklist_file = DATA_DIR / "domain_checklists.json"
    if checklist_file.exists():
        with open(checklist_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def compute_coverage_matrix(requirements: list[dict], recommendations: list[dict]) -> list[dict]:
    """
    Build a coverage matrix: requirement × standards showing Covered/Partial/Missing.
    """
    matrix = []
    for req in requirements:
        req_id = req.get("id") or req.get("requirement_id")
        matching_recs = [
            r for r in recommendations
            if req_id in (r.get("requirement_ids", []) if isinstance(r.get("requirement_ids"), list)
                          else [r.get("requirement_id")])
        ]

        if len(matching_recs) >= 2:
            coverage = "covered"
        elif len(matching_recs) == 1:
            score = matching_recs[0].get("relevance_score", 0)
            coverage = "covered" if score > 0.6 else "partial"
        else:
            coverage = "missing"

        matrix.append({
            "requirement_id": req_id,
            "requirement_text": req.get("description", "")[:200],
            "requirement_type": req.get("req_type", ""),
            "coverage": coverage,
            "matching_standards": [
                {
                    "is_number": r.get("is_number", ""),
                    "score": r.get("relevance_score", 0),
                }
                for r in matching_recs
            ],
        })

    return matrix


def detect_gaps(text: str, domain: str, requirements: list[dict], coverage_matrix: list[dict]) -> list[dict]:
    """
    Detect specification gaps by comparing against the domain checklist.
    """
    findings = []
    checklists = load_domain_checklists()
    checklist = checklists.get(domain, {}).get("checklist", [])

    if not checklist:
        # Try auto-detect from text
        domain = _auto_detect_domain(text)
        checklist = checklists.get(domain, {}).get("checklist", [])

    text_lower = text.lower()
    req_texts = " ".join(r.get("description", "").lower() for r in requirements)
    all_text = text_lower + " " + req_texts

    # Check each checklist item
    checklist_keywords = {
        "Material specification": ["material", "grade", "composition", "specification"],
        "Testing and acceptance criteria": ["test", "acceptance", "testing", "cube test", "lab test"],
        "Sampling method reference": ["sampling", "sample", "lot size", "inspection"],
        "Marking and labelling requirements": ["marking", "label", "labelling", "marking"],
        "Packaging and storage requirements": ["packaging", "storage", "packing", "transport"],
        "Certification / ISI mark requirement": ["isi mark", "certification", "bis", "certified"],
        "Delivery and inspection clause": ["delivery", "inspection", "receipt", "site inspection"],
        "Warranty / guarantee period": ["warranty", "guarantee", "defect liability"],
        "Product specification standard": ["specification", "standard", "conform", "as per"],
        "Safety standard": ["safety", "protection", "hazard", "safe"],
        "Installation code of practice": ["installation", "code of practice", "erection"],
        "EMC requirements": ["emc", "electromagnetic", "interference", "compatibility"],
        "Energy efficiency rating": ["energy efficient", "star rating", "bee rating", "power consumption"],
        "Environmental compliance": ["rohs", "e-waste", "environment", "hazardous"],
        "Hygiene / HACCP requirements": ["hygiene", "haccp", "food safety", "sanitation"],
        "Microbiological limits": ["microbiological", "bacteria", "e.coli", "coliform"],
        "Fire resistance": ["fire", "flame", "fire resistance", "fire safety"],
    }

    for item in checklist:
        keywords = checklist_keywords.get(item, item.lower().split()[0:2])
        if isinstance(keywords, str):
            keywords = [keywords]
        found = any(kw in all_text for kw in keywords)

        if not found:
            findings.append({
                "kind": "gap",
                "severity": "medium",
                "title": f"Missing: {item}",
                "description": f"The tender specification does not appear to include {item.lower()}. "
                               f"This is typically required for {domain} procurement.",
                "proposed_fix": f"Add a clause addressing {item.lower()} with reference to applicable Indian Standard.",
            })

    # Check coverage matrix for uncovered requirements
    missing_reqs = [c for c in coverage_matrix if c["coverage"] == "missing"]
    if missing_reqs:
        for mr in missing_reqs[:5]:
            findings.append({
                "kind": "gap",
                "severity": "medium",
                "title": f"No standard found for requirement",
                "description": f"Requirement '{mr['requirement_text'][:100]}...' has no matching Indian Standard in the knowledge base.",
                "requirement_id": mr["requirement_id"],
                "proposed_fix": "Verify manually against BIS catalogue or expand the specification.",
            })

    return findings


def detect_conflicts(text: str, requirements: list[dict], recommendations: list[dict]) -> list[dict]:
    """
    Detect conflicts in the tender specification:
      - Conflicting values for the same property
      - Ambiguous references ("as per latest standard", "good quality")
      - Cited standards that don't match the product
    """
    findings = []
    text_lower = text.lower()

    # Check for ambiguous wording
    ambiguous_patterns = [
        (r"as per latest (?:indian )?standard", "Ambiguous reference to 'latest standard' without specifying IS number"),
        (r"good quality", "Vague quality requirement — 'good quality' without measurable criteria"),
        (r"best quality", "Vague quality requirement — 'best quality' without measurable criteria"),
        (r"of approved (?:make|brand|manufacturer)", "Unspecified approval criteria — which approved list?"),
        (r"relevant indian standards?", "Ambiguous — 'relevant Indian Standards' without specific IS number"),
        (r"or equivalent", "Ambiguous equivalence — specify acceptance criteria for 'equivalent'"),
    ]

    for pattern, desc in ambiguous_patterns:
        matches = list(re.finditer(pattern, text_lower))
        if matches:
            findings.append({
                "kind": "conflict",
                "severity": "medium",
                "title": "Ambiguous specification language",
                "description": desc + f" (found {len(matches)} occurrence(s))",
                "proposed_fix": "Replace with specific IS number and measurable criteria.",
            })

    # Check for conflicting grade/value specifications
    grade_pattern = r"(\d{2,3})\s*grade"
    grades_found = re.findall(grade_pattern, text_lower)
    if len(set(grades_found)) > 1:
        findings.append({
            "kind": "conflict",
            "severity": "high",
            "title": "Conflicting grade specifications",
            "description": f"Multiple cement/material grades specified: {', '.join(set(grades_found))} grade. "
                          f"Verify if different grades are intended for different items.",
            "proposed_fix": "Clearly assign each grade to its specific item/application.",
        })

    # Check for unit mismatches
    if "kg/sq cm" in text_lower and "mpa" in text_lower:
        findings.append({
            "kind": "conflict",
            "severity": "low",
            "title": "Mixed unit systems",
            "description": "Both kg/sq cm and MPa units found — ensure consistency or provide conversion.",
            "proposed_fix": "Use consistent SI units (MPa) throughout the specification.",
        })

    return findings


def compute_risk_score(findings: list[dict], recommendations: list[dict]) -> dict:
    """
    Compute a 0-100 risk score from weighted findings.
    """
    severity_weights = {
        "critical": 20,
        "high": 12,
        "medium": 5,
        "low": 2,
    }

    total_penalty = 0
    for f in findings:
        severity = f.get("severity", "medium")
        total_penalty += severity_weights.get(severity, 5)

    # Factor in low-confidence recommendations
    if recommendations:
        low_conf = sum(1 for r in recommendations if r.get("relevance_score", 0) < 0.55)
        total_penalty += low_conf * 3

    # Normalize to 0-100
    risk_score = min(100, total_penalty)

    if risk_score <= 20:
        level = "Low"
    elif risk_score <= 50:
        level = "Medium"
    else:
        level = "High"

    return {
        "risk_score": risk_score,
        "risk_level": level,
        "breakdown": {
            "finding_penalties": sum(severity_weights.get(f.get("severity", "medium"), 5) for f in findings),
            "low_confidence_penalties": sum(3 for r in (recommendations or []) if r.get("relevance_score", 0) < 0.55),
            "total_findings": len(findings),
        },
        "tooltip": f"Risk score {risk_score}/100 computed from {len(findings)} findings "
                   f"(weighted by severity: critical=20, high=12, medium=5, low=2) "
                   f"plus 3 points per low-confidence recommendation.",
    }


def _auto_detect_domain(text: str) -> str:
    """Auto-detect domain from text content."""
    text_lower = text.lower()
    domain_keywords = {
        "construction": ["cement", "concrete", "steel", "reinforcement", "building", "brick"],
        "electrical": ["cable", "wiring", "switch", "socket", "transformer", "earthing"],
        "it_hardware": ["laptop", "computer", "ups", "monitor", "server", "networking"],
        "water_plumbing": ["water supply", "pipe", "plumbing", "drinking water", "pvc pipe"],
        "food_beverages": ["food", "drinking water", "packaged water", "edible oil"],
        "steel": ["steel", "structural steel", "rebar", "TMT"],
        "furniture": ["furniture", "desk", "chair", "table", "cabinet"],
        "textiles": ["fabric", "textile", "cotton", "uniform"],
    }

    scores = {}
    for domain, keywords in domain_keywords.items():
        scores[domain] = sum(1 for kw in keywords if kw in text_lower)

    if scores:
        best = max(scores, key=scores.get)
        if scores[best] > 0:
            return best
    return "construction"
