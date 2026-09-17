"""LLM service for requirement extraction and relevance justification.

Uses OpenAI-compatible API when OPENAI_API_KEY is set.
Falls back to keyword-based mock extraction for demo mode.
"""

import json
import re
from typing import Optional

from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, USE_MOCK_LLM


# ──────────────────────────────────────────────
# Prompt Templates
# ──────────────────────────────────────────────

EXTRACTION_PROMPT = """You are an expert in Indian government procurement and Bureau of Indian Standards (BIS).
Analyze the following tender document text and extract all technical, performance, and safety requirements.

For each requirement, output:
- "req_type": one of "technical", "performance", "safety", "quality", "material"
- "description": a concise description of the requirement (1-2 sentences)
- "keywords": an array of 3-6 relevant keywords for searching Indian Standards

Also extract a short title for the tender (max 10 words).

Return ONLY valid JSON in this exact format:
{
  "title": "Short tender title",
  "requirements": [
    {
      "req_type": "technical",
      "description": "Description of the requirement",
      "keywords": ["keyword1", "keyword2", "keyword3"]
    }
  ]
}

TENDER TEXT:
"""

JUSTIFICATION_PROMPT = """You are an expert in Indian Standards (IS/BIS).
Given a procurement requirement and a candidate Indian Standard, explain in 1-2 sentences why this standard is relevant to the requirement.

Requirement: {requirement}

Standard: {standard_number} - {standard_title}
Scope: {standard_scope}

Provide a concise justification (1-2 sentences) explaining the relevance. Return ONLY the justification text, no JSON."""


# ──────────────────────────────────────────────
# Real LLM (OpenAI-compatible)
# ──────────────────────────────────────────────

def _get_openai_client():
    """Lazy-initialize OpenAI client."""
    from openai import OpenAI
    return OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)


def _llm_extract_requirements(text: str) -> dict:
    """Use LLM to extract requirements from tender text."""
    client = _get_openai_client()
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert procurement analyst. Always respond with valid JSON only."},
            {"role": "user", "content": EXTRACTION_PROMPT + text[:8000]},  # Limit input length
        ],
        temperature=0.2,
        max_tokens=4000,
    )
    content = response.choices[0].message.content.strip()
    # Try to extract JSON from the response
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return json.loads(content)


def _llm_generate_justification(requirement: str, std_number: str, std_title: str, std_scope: str) -> str:
    """Use LLM to generate relevance justification."""
    client = _get_openai_client()
    prompt = JUSTIFICATION_PROMPT.format(
        requirement=requirement,
        standard_number=std_number,
        standard_title=std_title,
        standard_scope=std_scope,
    )
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert in Indian Standards (BIS). Be concise."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


# ──────────────────────────────────────────────
# Mock LLM (keyword-based fallback for demo)
# ──────────────────────────────────────────────

# Keyword patterns for requirement classification
REQ_PATTERNS = {
    "safety": [
        r"fire\s+safety", r"fire\s+detect", r"fire\s+extinguish", r"fire\s+alarm",
        r"safety\s+helmet", r"safety\s+shoe", r"eye\s+protect", r"PPE",
        r"earthquake", r"seismic", r"escape\s+route", r"emergency\s+exit",
    ],
    "technical": [
        r"concrete", r"cement", r"steel\s+(bar|reinforcement|TMT)", r"wiring",
        r"earthing", r"grounding", r"plumbing", r"water\s+supply", r"pipe",
        r"LED\s+lumin", r"UPS\s+system", r"network\s+switch", r"router",
        r"structured\s+cabling", r"LCD\s+monitor", r"computer", r"transformer",
        r"canned\s+food", r"edible\s+oil", r"packaged\s+water",
    ],
    "quality": [
        r"drinking\s+water\s+quality", r"water\s+quality", r"cube\s+test",
        r"compressive\s+strength", r"quality\s+assur", r"ISI\s+mark", r"BIS\s+cert",
        r"HACCP", r"food\s+hygiene", r"NABL",
    ],
    "material": [
        r"OPC", r"portland\s+cement", r"43\s+grade", r"53\s+grade",
        r"M\d+\s+grade", r"Fe\s*500", r"TMT\s+bar", r"aggregate",
        r"fly\s+ash", r"PVC\s+(cable|pipe|insul)", r"CPVC", r"uPVC",
    ],
    "performance": [
        r"KVA", r"battery\s+backup", r"EMC", r"electromagnetic",
        r"voltage", r"1100\s*V", r"load\s+design", r"wind\s+load",
    ],
}


def _extract_keywords_from_text(text: str) -> list[str]:
    """Extract keywords from text using simple NLP-like heuristics."""
    # Common construction/procurement keywords
    keyword_pool = [
        "cement", "concrete", "steel", "reinforcement", "TMT", "OPC",
        "electrical", "wiring", "earthing", "cable", "PVC", "LED",
        "plumbing", "water supply", "pipe", "CPVC", "uPVC",
        "fire safety", "fire detection", "fire extinguisher", "alarm",
        "safety helmet", "safety shoes", "PPE", "eye protection",
        "UPS", "monitor", "LCD", "computer", "IT equipment", "network",
        "switch", "router", "cabling", "data centre",
        "drinking water", "packaged water", "food hygiene", "HACCP",
        "canned food", "edible oil", "packaging",
        "earthquake", "seismic", "structural", "design loads",
        "aggregate", "mix design", "fly ash", "transformer",
        "soil", "foundation", "geotechnical",
    ]
    text_lower = text.lower()
    found = [kw for kw in keyword_pool if kw.lower() in text_lower]
    return found[:6] if found else ["general", "procurement"]


def _classify_requirement(text: str) -> str:
    """Classify a requirement by type using regex patterns."""
    text_lower = text.lower()
    for req_type, patterns in REQ_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return req_type
    return "technical"


def _mock_extract_requirements(text: str) -> dict:
    """Extract requirements using keyword/regex parsing (no LLM needed)."""
    # Split text into sections/paragraphs
    lines = text.split("\n")
    requirements = []
    current_section = ""

    # Try to extract a title
    title = "Tender Document"
    for line in lines[:10]:
        line = line.strip()
        if line.lower().startswith("subject:"):
            title = line.split(":", 1)[1].strip()[:80]
            break
        elif len(line) > 20 and len(line) < 100 and not line[0].isdigit():
            title = line[:80]

    # Extract requirement-like paragraphs
    for line in lines:
        line = line.strip()
        if not line or len(line) < 20:
            continue

        # Skip headers/titles that are too short
        if line.startswith(("TENDER", "Subject:", "Tender Ref")):
            continue

        # Look for lines that describe specifications
        if any(kw in line.lower() for kw in [
            "shall", "must", "conform", "comply", "as per", "requirement",
            "specification", "standard", "grade", "rated", "type",
        ]):
            req_type = _classify_requirement(line)
            keywords = _extract_keywords_from_text(line)
            if keywords:
                requirements.append({
                    "req_type": req_type,
                    "description": line[:300],
                    "keywords": keywords,
                })

    # Deduplicate similar requirements
    seen_descriptions = set()
    unique_reqs = []
    for req in requirements:
        desc_key = req["description"][:50].lower()
        if desc_key not in seen_descriptions:
            seen_descriptions.add(desc_key)
            unique_reqs.append(req)

    return {
        "title": title,
        "requirements": unique_reqs[:20],  # Limit to 20 requirements
    }


def _mock_generate_justification(requirement: str, std_number: str, std_title: str, std_scope: str) -> str:
    """Generate a template-based justification (no LLM needed)."""
    return (
        f"{std_number} ({std_title}) is relevant because it provides specifications and "
        f"requirements that directly address this procurement need. {std_scope[:150]}"
    )


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def extract_requirements(text: str) -> dict:
    """Extract requirements from tender text. Uses LLM if available, else mock."""
    if USE_MOCK_LLM:
        print("[LLM Service] Using MOCK extraction (no API key set)")
        return _mock_extract_requirements(text)
    else:
        print("[LLM Service] Using OpenAI-compatible LLM for extraction")
        return _llm_extract_requirements(text)


def generate_justification(
    requirement: str,
    std_number: str,
    std_title: str,
    std_scope: str,
) -> str:
    """Generate relevance justification. Uses LLM if available, else mock."""
    if USE_MOCK_LLM:
        return _mock_generate_justification(requirement, std_number, std_title, std_scope)
    else:
        return _llm_generate_justification(requirement, std_number, std_title, std_scope)
