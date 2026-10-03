from app import app
import json

def test_routes():
    client = app.test_client()
    
    print("Testing GET routes...")
    routes = [
        ("/", 200),
        ("/dashboard", 200),
        ("/loan-request", 200),
        ("/auction", 200),
        ("/repayment", 200),
        ("/crowdfunding", 200),
        ("/gigs", 200),
        ("/gig-score", 200),
        ("/meal-drops", 200),
        ("/trust-profile", 200)
    ]
    for r, exp in routes:
        resp = client.get(r)
        assert resp.status_code == exp, f"Route {r} returned {resp.status_code}, expected {exp}"
        print(f"  [OK] GET {r} -> {resp.status_code}")

    print("\nTesting API endpoints...")
    # 1. Loan create
    r = client.post("/api/loans/create", json={"amount": 2500, "purpose": "Lab equipment", "repay_by": "Sep 20, 2026", "max_rate": 4.5, "message": "Physics lab prep"})
    assert r.status_code == 200
    loan_id = r.json["loan_id"]
    print(f"  [OK] POST /api/loans/create -> loan_id: {loan_id}")

    # 2. Auction bid
    r = client.post(f"/api/auction/{loan_id}/bid", json={"rate": 3.2, "lender_id": 1, "notes": "Disburse immediately"})
    assert r.status_code == 200
    print(f"  [OK] POST /api/auction/{loan_id}/bid -> {r.json}")

    # 3. Crowdfunding donation
    r = client.post("/api/crowdfunding/1/donate", json={"amount": 500, "donor_name": "Test Donor", "is_anonymous": False})
    assert r.status_code == 200
    print(f"  [OK] POST /api/crowdfunding/1/donate -> amount: {r.json['amount']}, trx: {r.json['trx_id']}")

    # 4. Crowdfunding expenditure impact API
    r = client.get("/api/crowdfunding/1/expenditure-impact?amount=1000")
    assert r.status_code == 200
    print(f"  [OK] GET /api/crowdfunding/1/expenditure-impact -> breakdown items: {len(r.json['breakdown'])}")

    # 5. Gigs post with gig_score
    r = client.post("/api/gigs/post", json={"title": "Test Algorithm Assistance", "category": "Tech & Code", "budget": 900, "due_info": "due in 1 day", "poster_id": 1})
    assert r.status_code == 200
    assert "gig_score" in r.json["gig"], "gig_score missing in posted gig response"
    print(f"  [OK] POST /api/gigs/post -> gig_score: {r.json['gig']['gig_score']}, tier: {r.json['gig']['gig_tier']}")

    # 6. Meals gift
    r = client.post("/api/meals/gift", json={"meals_count": 2, "donor_id": 1})
    assert r.status_code == 200
    print(f"  [OK] POST /api/meals/gift -> claim_code: {r.json['claim_code']}")

    # 7. Meals claim
    r = client.post("/api/meals/claim")
    assert r.status_code == 200
    print(f"  [OK] POST /api/meals/claim -> claim_code: {r.json['claim_code']}")

    # 8. Loan repayment
    r = client.post("/api/loans/1/repay", json={"amount": 552, "payment_method": "bKash"})
    assert r.status_code == 200
    print(f"  [OK] POST /api/loans/1/repay -> trx_id: {r.json['trx_id']}, new_score: {r.json['new_trust_score']}")

    print("\nALL BACKEND ROUTES AND API ENDPOINTS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_routes()
