"""Unified analysis pipeline — orchestrates all stages of the recommendation workflow.

Stages:
  1. Document processing
  2. Language detection/translation
  3. Requirement extraction
  4. Standards retrieval (lexical + semantic + graph)
  5. Fusion & ranking (RRF)
  6. Allied-standards expansion
  7. Lifecycle/edition check
  8. QCO/certification check
  9. Coverage-gap analysis
  10. Conflict detection
  11. Risk assessment
  12. Ready for officer review
"""

import json
import time
import datetime
import traceback
from database import SessionLocal
from models import (
    Analysis, Document, Requirement, Recommendation, Finding, AuditLog,
    Standard, Tender
)
from services.llm_service import extract_requirements, generate_justification
from services.search_service import hybrid_search, is_index_ready
from services.graph_store import graph_search, is_graph_ready, get_neighbors
from services.lifecycle_service import verify_lifecycle, check_cited_standards
from services.qco_service import verify_qco, check_tender_qco_compliance
from services.audit_engine import (
    compute_coverage_matrix, detect_gaps, detect_conflicts,
    compute_risk_score, _auto_detect_domain
)
from config import TOP_K_RESULTS


PIPELINE_STAGES = [
    "Document processing",
    "Language detection",
    "Requirement extraction",
    "Standards retrieval",
    "Fusion & ranking",
    "Allied-standards expansion",
    "Lifecycle check",
    "QCO check",
    "Coverage-gap analysis",
    "Conflict detection",
    "Risk assessment",
    "Ready for review",
]


def run_analysis_pipeline(
    analysis_id: int,
    raw_text: str,
    filename: str = None,
    domain_hint: str = None,
    use_reranker: bool = False,
    include_allied: bool = True,
):
    """
    Run the complete analysis pipeline. Updates the Analysis record with
    progress, stage, and results at each step.
    """
    db = SessionLocal()
    start_time = time.time()

    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            return

        def update_progress(stage_idx: int, message: str = None):
            analysis.current_stage = PIPELINE_STAGES[stage_idx]
            analysis.progress = int((stage_idx / len(PIPELINE_STAGES)) * 100)
            if message:
                _log_audit(db, analysis_id, "system", PIPELINE_STAGES[stage_idx], message)
            db.commit()

        analysis.status = "processing"
        update_progress(0, "Starting document processing")

        # ── Stage 1: Document Processing ──
        doc = Document(
            analysis_id=analysis_id,
            filename=filename,
            mime_type="text/plain",
            pages=max(1, raw_text.count('\n\n') + 1),
            raw_text=raw_text[:50000],
        )
        db.add(doc)
        db.flush()

        # Also create a legacy Tender record for backward compat
        tender = Tender(
            filename=filename,
            raw_text=raw_text[:50000],
            analysis_id=analysis_id,
        )
        db.add(tender)
        db.flush()
        db.commit()

        update_progress(1, "Detecting language")

        # ── Stage 2: Language Detection ──
        detected_lang = _detect_language(raw_text)
        analysis.language = detected_lang
        analysis.detected_languages = json.dumps([detected_lang])
        db.commit()

        update_progress(2, "Extracting requirements")

        # ── Stage 3: Requirement Extraction ──
        extraction_result = extract_requirements(raw_text)
        title = extraction_result.get("title", "Untitled Analysis")
        extracted_reqs = extraction_result.get("requirements", [])

        analysis.name = title
        tender.title = title

        req_objects = []
        for i, req in enumerate(extracted_reqs):
            keywords = req.get("keywords", [])
            if isinstance(keywords, list):
                keywords = json.dumps(keywords)

            r = Requirement(
                tender_id=tender.id,
                analysis_id=analysis_id,
                code=f"REQ-{i+1:03d}",
                req_type=req.get("req_type", "technical"),
                description=req.get("description", ""),
                keywords=keywords,
                confidence=0.8,
            )
            db.add(r)
            req_objects.append(r)

        db.flush()
        analysis.requirements_count = len(req_objects)
        db.commit()

        update_progress(3, f"Searching standards for {len(req_objects)} requirements")

        # ── Stage 4-5: Hybrid Retrieval + RRF ──
        if not is_index_ready():
            _log_audit(db, analysis_id, "system", "Warning", "Search index not ready")

        all_recommendations = []
        all_standard_ids = set()

        for req in req_objects:
            keywords_list = _parse_json(req.keywords, [])
            search_query = req.description + " " + " ".join(keywords_list)

            # Lexical + Semantic search
            search_results = hybrid_search(search_query, top_k=TOP_K_RESULTS)

            # Graph search (expand from top hits)
            graph_results = []
            if is_graph_ready() and search_results:
                seed_ids = [r["standard_id"] for r in search_results[:3]]
                graph_results = graph_search(seed_ids, max_hops=2)

            # RRF fusion
            fused = _reciprocal_rank_fusion(search_results, graph_results)

            for rank, result in enumerate(fused[:TOP_K_RESULTS]):
                standard = db.query(Standard).filter(Standard.id == result["standard_id"]).first()
                if not standard:
                    continue

                justification = generate_justification(
                    requirement=req.description,
                    std_number=standard.is_number,
                    std_title=standard.title,
                    std_scope=standard.scope or "",
                )

                rec = Recommendation(
                    analysis_id=analysis_id,
                    requirement_id=req.id,
                    standard_id=standard.id,
                    relationship_type=result.get("relationship", "primary"),
                    relevance_score=result["score"],
                    confidence=result["score"] * 100,
                    score_breakdown_json=json.dumps(result.get("breakdown", {})),
                    status="pending",
                    justification=justification,
                    evidence_json=json.dumps(result.get("evidence", {})),
                )
                db.add(rec)
                all_recommendations.append(rec)
                all_standard_ids.add(standard.id)

        db.flush()
        db.commit()

        update_progress(5, "Expanding allied standards")

        # ── Stage 6: Allied Standards Expansion ──
        if include_allied and is_graph_ready():
            for std_id in list(all_standard_ids):
                neighbors = get_neighbors(std_id)
                for n in neighbors[:3]:
                    if n["id"] not in all_standard_ids:
                        # Check if already recommended
                        existing = db.query(Recommendation).filter(
                            Recommendation.analysis_id == analysis_id,
                            Recommendation.standard_id == n["id"],
                        ).first()
                        if not existing:
                            ally_std = db.query(Standard).filter(Standard.id == n["id"]).first()
                            if ally_std:
                                # Add as allied with lower score
                                ally_rec = Recommendation(
                                    analysis_id=analysis_id,
                                    requirement_id=req_objects[0].id if req_objects else None,
                                    standard_id=n["id"],
                                    relationship_type="allied",
                                    relevance_score=0.4,
                                    confidence=40,
                                    status="needs_review",
                                    justification=f"Allied standard — {n['relation_type']} relationship with {db.query(Standard).filter(Standard.id == std_id).first().is_number if db.query(Standard).filter(Standard.id == std_id).first() else 'related standard'}",
                                )
                                db.add(ally_rec)
                                all_standard_ids.add(n["id"])

            db.flush()
            db.commit()

        update_progress(6, "Verifying lifecycle and editions")

        # ── Stage 7: Lifecycle/Edition Check ──
        cited_checks = check_cited_standards(raw_text)
        for check in cited_checks:
            if not check.get("lifecycle_ok"):
                db.add(Finding(
                    analysis_id=analysis_id,
                    kind="outdated" if check.get("status") == "superseded" else "unverified",
                    severity="high" if check.get("status") == "superseded" else "medium",
                    title=f"{'Outdated' if check.get('status') == 'superseded' else 'Unverified'} citation: {check.get('cited_as', '')}",
                    description=check.get("message", ""),
                    proposed_fix=f"Replace with {check.get('suggested_replacement', check.get('latest_edition', 'latest edition'))}" if not check.get("edition_ok") else None,
                ))

        # Verify each recommended standard
        for rec in db.query(Recommendation).filter(Recommendation.analysis_id == analysis_id).all():
            std = db.query(Standard).filter(Standard.id == rec.standard_id).first()
            if std:
                lc = verify_lifecycle(std.is_number)
                qc = verify_qco(std.id)
                rec.verification_json = json.dumps({
                    "lifecycle": lc,
                    "qco": qc,
                })
                if lc.get("lifecycle_ok") and lc.get("edition_ok"):
                    rec.status = "verified"
                elif not lc.get("lifecycle_ok"):
                    rec.status = "needs_review"
                    rec.correction_json = json.dumps({
                        "type": "outdated_edition",
                        "message": lc.get("message"),
                        "suggested_replacement": lc.get("latest_edition"),
                    })

        db.flush()
        db.commit()

        update_progress(7, "Checking QCO compliance")

        # ── Stage 8: QCO Check ──
        qco_findings = check_tender_qco_compliance(raw_text, list(all_standard_ids))
        for qf in qco_findings:
            db.add(Finding(
                analysis_id=analysis_id,
                kind=qf["kind"],
                severity=qf["severity"],
                title=qf["title"],
                description=qf["description"],
                proposed_fix=qf.get("proposed_fix"),
            ))

        db.flush()
        db.commit()

        update_progress(8, "Analyzing coverage gaps")

        # ── Stage 9: Coverage Gap Analysis ──
        reqs_data = [{"id": r.id, "description": r.description, "req_type": r.req_type} for r in req_objects]
        recs_data = [
            {
                "requirement_id": r.requirement_id,
                "is_number": db.query(Standard).filter(Standard.id == r.standard_id).first().is_number if db.query(Standard).filter(Standard.id == r.standard_id).first() else "",
                "relevance_score": r.relevance_score,
            }
            for r in db.query(Recommendation).filter(Recommendation.analysis_id == analysis_id).all()
        ]

        domain = domain_hint or _auto_detect_domain(raw_text)
        coverage = compute_coverage_matrix(reqs_data, recs_data)
        gap_findings = detect_gaps(raw_text, domain, reqs_data, coverage)

        for gf in gap_findings:
            db.add(Finding(
                analysis_id=analysis_id,
                kind=gf["kind"],
                severity=gf["severity"],
                title=gf["title"],
                description=gf["description"],
                proposed_fix=gf.get("proposed_fix"),
            ))

        db.flush()
        db.commit()

        update_progress(9, "Detecting conflicts")

        # ── Stage 10: Conflict Detection ──
        conflict_findings = detect_conflicts(raw_text, reqs_data, recs_data)
        for cf in conflict_findings:
            db.add(Finding(
                analysis_id=analysis_id,
                kind=cf["kind"],
                severity=cf["severity"],
                title=cf["title"],
                description=cf["description"],
                proposed_fix=cf.get("proposed_fix"),
            ))

        db.flush()
        db.commit()

        update_progress(10, "Computing risk score")

        # ── Stage 11: Risk Assessment ──
        all_findings = db.query(Finding).filter(Finding.analysis_id == analysis_id).all()
        findings_data = [{"severity": f.severity, "kind": f.kind} for f in all_findings]
        recs_for_risk = [{"relevance_score": r.relevance_score} for r in
                         db.query(Recommendation).filter(Recommendation.analysis_id == analysis_id).all()]

        risk = compute_risk_score(findings_data, recs_for_risk)

        analysis.risk_score = risk["risk_score"]
        analysis.risk_level = risk["risk_level"]
        analysis.gaps_count = sum(1 for f in all_findings if f.kind == "gap")
        analysis.conflicts_count = sum(1 for f in all_findings if f.kind == "conflict")
        analysis.standards_count = len(all_standard_ids)
        analysis.pages_count = doc.pages

        # ── Stage 12: Complete ──
        elapsed_ms = int((time.time() - start_time) * 1000)
        analysis.processing_time_ms = elapsed_ms
        analysis.status = "completed"
        analysis.progress = 100
        analysis.current_stage = "Ready for review"
        analysis.completed_at = datetime.datetime.utcnow()
        analysis.domain_hint = domain

        _log_audit(db, analysis_id, "system", "Pipeline complete",
                   f"Completed in {elapsed_ms}ms — {analysis.requirements_count} requirements, "
                   f"{analysis.standards_count} standards, {len(all_findings)} findings, "
                   f"risk: {risk['risk_level']} ({risk['risk_score']})")

        db.commit()

        update_progress(11, "Analysis complete — ready for officer review")

    except Exception as e:
        traceback.print_exc()
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                analysis.status = "failed"
                analysis.error_message = str(e)[:500]
                db.commit()
        except:
            pass
    finally:
        db.close()


def _detect_language(text: str) -> str:
    """Simple language detection based on script detection."""
    # Check for Devanagari (Hindi/Marathi)
    devanagari = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    # Check for Gujarati
    gujarati = sum(1 for c in text if '\u0A80' <= c <= '\u0AFF')
    # Check for Tamil
    tamil = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
    # Check for Bengali
    bengali = sum(1 for c in text if '\u0980' <= c <= '\u09FF')

    total_chars = len(text)
    if total_chars == 0:
        return "en"

    if devanagari / total_chars > 0.1:
        return "hi"
    if gujarati / total_chars > 0.1:
        return "gu"
    if tamil / total_chars > 0.1:
        return "ta"
    if bengali / total_chars > 0.1:
        return "bn"
    return "en"


def _reciprocal_rank_fusion(lexical_semantic: list[dict], graph: list[dict], k: int = 60) -> list[dict]:
    """
    Fuse results from lexical+semantic search and graph search using RRF.
    RRF score = sum(1 / (k + rank_i)) for each retriever
    """
    scores = {}
    evidence = {}

    # Score from lexical+semantic
    for rank, result in enumerate(lexical_semantic):
        sid = result["standard_id"]
        rrf = 1.0 / (k + rank + 1)
        scores[sid] = scores.get(sid, 0) + rrf
        evidence[sid] = {
            "lexical_semantic_rank": rank + 1,
            "lexical_semantic_score": result.get("score", 0),
        }

    # Score from graph
    for rank, result in enumerate(graph):
        sid = result["standard_id"]
        rrf = 1.0 / (k + rank + 1)
        scores[sid] = scores.get(sid, 0) + rrf * 0.5  # Lower weight for graph
        if sid in evidence:
            evidence[sid]["graph_rank"] = rank + 1
            evidence[sid]["graph_score"] = result.get("score", 0)
            evidence[sid]["graph_path"] = result.get("path", [])
        else:
            evidence[sid] = {
                "graph_rank": rank + 1,
                "graph_score": result.get("score", 0),
                "graph_path": result.get("path", []),
            }

    # Build fused results
    all_results = {}
    for result in lexical_semantic + graph:
        sid = result["standard_id"]
        if sid not in all_results:
            all_results[sid] = result.copy()
    
    fused = []
    for sid, rrf_score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        if sid in all_results:
            item = all_results[sid]
            # Normalize score to 0-1 range
            max_rrf = 2.0 / (k + 1)  # Max possible RRF score
            normalized = min(1.0, rrf_score / max_rrf)
            item["score"] = round(normalized, 4)
            item["breakdown"] = evidence.get(sid, {})
            item["evidence"] = evidence.get(sid, {})
            fused.append(item)

    return fused


def _parse_json(text, default=None):
    if not text:
        return default or []
    try:
        return json.loads(text)
    except:
        return default or []


def _log_audit(db, analysis_id: int, actor: str, event: str, detail: str = None):
    db.add(AuditLog(
        analysis_id=analysis_id,
        actor=actor,
        event=event,
        detail=detail,
    ))
