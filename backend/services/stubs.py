"""
Stub services for future work.
These are placeholder implementations that return mock data
so the UI and data flow are demonstrable end to end.
"""


# ──────────────────────────────────────────────
# TODO: Future work — Neo4j Knowledge Graph
# ──────────────────────────────────────────────
def get_related_standards(standard_id: int) -> list[dict]:
    """
    Find standards related to a given standard via a knowledge graph.
    Future: Query Neo4j for standards connected by 'supersedes', 'references',
    'complements' relationships.
    """
    return []  # Stub: no related standards


def get_standard_lineage(is_number: str) -> dict:
    """
    Get the amendment/revision lineage of a standard.
    Future: Traverse Neo4j graph for predecessor/successor relationships.
    """
    return {"current": is_number, "predecessors": [], "successors": []}


# ──────────────────────────────────────────────
# TODO: Future work — Sarvam AI Translation
# ──────────────────────────────────────────────
def translate_text(text: str, source_lang: str = "en", target_lang: str = "hi") -> str:
    """
    Translate text between English and Indian languages.
    Future: Integrate Sarvam AI API for multilingual support (Hindi, Tamil, etc.)
    """
    return text  # Stub: return original text unchanged


def detect_language(text: str) -> str:
    """
    Detect the language of input text.
    Future: Use Sarvam AI or langdetect for language identification.
    """
    return "en"  # Stub: assume English


# ──────────────────────────────────────────────
# TODO: Future work — Live BIS API Integration
# ──────────────────────────────────────────────
def search_bis_catalog(query: str) -> list[dict]:
    """
    Search the BIS (Bureau of Indian Standards) online catalog.
    Future: Integrate with BIS API or web scraper for live standard lookups.
    """
    return []  # Stub: no live results


def check_standard_status(is_number: str) -> dict:
    """
    Check if a standard is current, withdrawn, or superseded.
    Future: Query BIS API for real-time status.
    """
    return {"is_number": is_number, "status": "current", "note": "Mock status"}


# ──────────────────────────────────────────────
# TODO: Future work — GeM / CPPP Integration
# ──────────────────────────────────────────────
def search_gem_products(query: str) -> list[dict]:
    """
    Search Government e-Marketplace (GeM) for products matching standards.
    Future: Integrate with GeM API.
    """
    return []  # Stub: no GeM results


def fetch_cppp_tenders(keyword: str) -> list[dict]:
    """
    Fetch tenders from Central Public Procurement Portal (CPPP).
    Future: Integrate with CPPP API.
    """
    return []  # Stub: no CPPP results


# ──────────────────────────────────────────────
# TODO: Future work — Amendment / Lifecycle Tracking
# ──────────────────────────────────────────────
def get_amendments(is_number: str) -> list[dict]:
    """
    Get list of amendments for a standard.
    Future: Track amendments via BIS notifications and store in DB.
    """
    return []  # Stub: no amendments


def check_for_updates(is_number: str) -> dict:
    """
    Check if a standard has been updated or is due for review.
    Future: Schedule periodic checks against BIS catalog.
    """
    return {"is_number": is_number, "up_to_date": True, "message": "No updates available (mock)"}
