import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("Manak Mitra Live Pipeline Verification")
print("=" * 60)

# 1. Fetch sample tender
sample_resp = urllib.request.urlopen(f"{BASE_URL}/api/sample-tenders")
samples = json.loads(sample_resp.read())
sample = samples[0]
print(f"[1/6] Loaded sample tender: '{sample['title']}' ({len(sample['text'])} chars)")

# 2. Extract requirements
form_data = urllib.parse.urlencode({"text": sample["text"]}).encode("utf-8")
extract_req = urllib.request.Request(f"{BASE_URL}/api/extract", data=form_data)
extract_resp = urllib.request.urlopen(extract_req)
extracted = json.loads(extract_resp.read())
tender_id = extracted["tender_id"]
req_count = len(extracted["requirements"])
print(f"[2/6] Extraction successful -> Tender ID: {tender_id}, Requirements: {req_count}")

# 3. Generate recommendations
rec_body = json.dumps({"tender_id": tender_id}).encode("utf-8")
rec_req = urllib.request.Request(
    f"{BASE_URL}/api/recommend",
    data=rec_body,
    headers={"Content-Type": "application/json"}
)
rec_resp = urllib.request.urlopen(rec_req)
rec_res = json.loads(rec_resp.read())
total_recs = sum(len(r["recommendations"]) for r in rec_res["requirements"])
print(f"[3/6] Recommendation successful -> {total_recs} candidate standards recommended")

# 4. Review decision
first_rec = rec_res["requirements"][0]["recommendations"][0]
rec_id = first_rec["id"]
is_num = first_rec["is_number"]
review_body = json.dumps({
    "decision": "accept",
    "officer_notes": "Meets tender safety specifications"
}).encode("utf-8")
review_req = urllib.request.Request(
    f"{BASE_URL}/api/review/{rec_id}",
    data=review_body,
    headers={"Content-Type": "application/json"},
    method="PUT"
)
review_resp = urllib.request.urlopen(review_req)
review_data = json.loads(review_resp.read())
print(f"[4/6] Officer Review decision recorded -> Standard: {is_num}, Decision: {review_data['decision']}")

# 5. Export PDF
pdf_body = json.dumps({"tender_id": tender_id, "format": "pdf"}).encode("utf-8")
pdf_req = urllib.request.Request(
    f"{BASE_URL}/api/export",
    data=pdf_body,
    headers={"Content-Type": "application/json"}
)
pdf_resp = urllib.request.urlopen(pdf_req)
pdf_bytes = pdf_resp.read()
print(f"[5/6] PDF Report Export -> Content-Type: {pdf_resp.headers.get('Content-Type')}, Size: {len(pdf_bytes)} bytes")

# 6. Export DOCX
docx_body = json.dumps({"tender_id": tender_id, "format": "docx"}).encode("utf-8")
docx_req = urllib.request.Request(
    f"{BASE_URL}/api/export",
    data=docx_body,
    headers={"Content-Type": "application/json"}
)
docx_resp = urllib.request.urlopen(docx_req)
docx_bytes = docx_resp.read()
print(f"[6/6] DOCX Report Export -> Content-Type: {docx_resp.headers.get('Content-Type')}, Size: {len(docx_bytes)} bytes")

print("=" * 60)
print("ALL LIVE END-TO-END PIPELINE CHECKS PASSED SUCCESSFULLY!")
print("=" * 60)
