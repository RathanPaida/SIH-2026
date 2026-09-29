import requests

res = requests.post("http://localhost:8000/api/analyses", data={"text": "This is a test tender document with sufficient length so it doesn't complain about being too short. It must be more than 50 characters long to pass the validation check in the endpoint.", "domain_hint": "construction"})
print(res.status_code)
print(res.text)
