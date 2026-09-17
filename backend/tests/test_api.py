"""Integration and unit tests for Manak Mitra FastAPI backend endpoints."""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from services import stubs


@pytest.fixture(scope="module")
def client():
    """Create test client with lifespan startup executed."""
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "Manak Mitra"


def test_list_standards(client):
    """Test standards listing and filtering."""
    # List all
    response = client.get("/api/standards")
    assert response.status_code == 200
    standards = response.json()
    assert len(standards) > 0

    # Test search
    response_search = client.get("/api/standards?search=cement")
    assert response_search.status_code == 200
    cement_stds = response_search.json()
    assert any("cement" in s["title"].lower() or "cement" in (s["keywords"] or "").lower() for s in cement_stds)

    # Test single standard retrieval
    std_id = standards[0]["id"]
    response_single = client.get(f"/api/standards/{std_id}")
    assert response_single.status_code == 200
    single_std = response_single.json()
    assert single_std["id"] == std_id
    assert "is_number" in single_std


def test_standards_sectors(client):
    """Test listing sectors."""
    response = client.get("/api/standards/sectors")
    assert response.status_code == 200
    sectors = response.json()
    assert isinstance(sectors, list)
    assert len(sectors) > 0


def test_sample_tenders(client):
    """Test fetching sample tender documents."""
    response = client.get("/api/sample-tenders")
    assert response.status_code == 200
    samples = response.json()
    assert len(samples) >= 3
    for sample in samples:
        assert "filename" in sample
        assert "title" in sample
        assert len(sample["text"]) > 50


def test_full_pipeline_flow(client):
    """Test full pipeline: Extract -> Recommend -> Review -> Export."""
    # 1. Extract requirements
    tender_text = (
        "Notice Inviting Tender for Civil Construction Works. "
        "Scope includes supply of Ordinary Portland Cement Grade 43 or Grade 53 conforming to standards. "
        "High-yield strength deformed (TMT) steel bars Fe 500D for RCC structures. "
        "Electrical wiring with FRLS copper cables and fire alarm detection systems. "
        "All materials must be tested and certified prior to installation on site."
    )

    extract_resp = client.post("/api/extract", data={"text": tender_text})
    assert extract_resp.status_code == 200
    extract_data = extract_resp.json()
    tender_id = extract_data["tender_id"]
    assert tender_id is not None
    assert len(extract_data["requirements"]) > 0

    # 2. Get recommendations
    rec_resp = client.post("/api/recommend", json={"tender_id": tender_id})
    assert rec_resp.status_code == 200
    rec_data = rec_resp.json()
    assert rec_data["tender_id"] == tender_id
    assert len(rec_data["requirements"]) > 0

    # Collect a recommendation ID to test review
    rec_id = None
    for req in rec_data["requirements"]:
        if req["recommendations"]:
            rec_id = req["recommendations"][0]["id"]
            break

    assert rec_id is not None, "At least one recommendation should have been generated"

    # 3. Review recommendation (accept)
    review_resp = client.put(
        f"/api/review/{rec_id}",
        json={"decision": "accept", "officer_notes": "Approved for tender specs"}
    )
    assert review_resp.status_code == 200
    review_data = review_resp.json()
    assert review_data["decision"] == "accept"
    assert review_data["officer_notes"] == "Approved for tender specs"

    # Check tender review summary
    tender_review_resp = client.get(f"/api/tenders/{tender_id}/review")
    assert tender_review_resp.status_code == 200
    review_summary = tender_review_resp.json()
    assert review_summary["tender_id"] == tender_id

    # 4. Export PDF
    pdf_resp = client.post("/api/export", json={"tender_id": tender_id, "format": "pdf"})
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 100

    # 5. Export DOCX
    docx_resp = client.post("/api/export", json={"tender_id": tender_id, "format": "docx"})
    assert docx_resp.status_code == 200
    assert "application/vnd.openxmlformats" in docx_resp.headers["content-type"]
    assert len(docx_resp.content) > 100


def test_stubs():
    """Verify future work stub methods work and return expected placeholder types."""
    assert stubs.get_related_standards(1) == []
    assert "current" in stubs.get_standard_lineage("IS 269")
    assert stubs.translate_text("hello") == "hello"
    assert stubs.detect_language("text") == "en"
    assert stubs.search_bis_catalog("cement") == []
    assert stubs.check_standard_status("IS 269")["status"] == "current"
    assert stubs.search_gem_products("cables") == []
    assert stubs.fetch_cppp_tenders("steel") == []
    assert stubs.get_amendments("IS 269") == []
    assert stubs.check_for_updates("IS 269")["up_to_date"] is True
