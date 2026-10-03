import os
import sys
from app import app
import db

def run_workflow_audit():
    client = app.test_client()
    passed = 0
    failed = 0
    total_checks = 0

    def check(name, condition, details=""):
        nonlocal passed, failed, total_checks
        total_checks += 1
        if condition:
            passed += 1
            print(f"  [PASS] {name} {details}")
        else:
            failed += 1
            print(f"  [FAIL] {name} - FAILED! {details}")

    print("==================================================================")
    print("      UIU AID — FULL USER WORKFLOW & INTEGRITY AUDIT CHECK        ")
    print("==================================================================\n")

    # -------------------------------------------------------------
    # WORKFLOW 1: Authentication & Session Management
    # -------------------------------------------------------------
    print(">>> WORKFLOW 1: Authentication & Role-Based Access")
    r = client.get("/login")
    check("GET /login page", r.status_code == 200)

    # 1.1 Valid Student Login
    r = client.post("/api/auth/login", json={"student_id": "011211045", "role": "student"})
    check("Student Login (Nusrat Jahan)", r.status_code == 200 and r.json.get("role") == "student")

    # 1.2 Admin Login
    r = client.post("/api/auth/login", json={"student_id": "ADMIN001", "role": "admin"})
    check("Admin Login (ADMIN001)", r.status_code == 200 and r.json.get("redirect") == "/admin")

    # 1.3 Invalid Login Handled
    r = client.post("/api/auth/login", json={"student_id": "INVALID999", "role": "student"})
    check("Invalid Student ID rejected gracefully", r.status_code == 401)

    # 1.4 Registration (Unique ID check)
    import random
    new_id = f"01129{random.randint(1000, 9999)}"
    r = client.post("/api/auth/register", json={
        "name": "Audit Test Student",
        "student_id": new_id,
        "department": "CSE",
        "trimester": "3rd trimester"
    })
    check("Student Registration", r.status_code == 200, f"ID: {new_id}")

    r = client.get("/logout")
    check("GET /logout session cleanup", r.status_code == 302)

    # -------------------------------------------------------------
    # WORKFLOW 2: Student Dashboard & Community Stats
    # -------------------------------------------------------------
    print("\n>>> WORKFLOW 2: Student Dashboard & Community Analytics")
    r = client.get("/dashboard")
    check("GET /dashboard (Screen 1)", r.status_code == 200 and b"UIU Aid" in r.data)

    r = client.get("/api/stats")
    check("GET /api/stats API", r.status_code == 200 and "facilitated" in r.json and "repayment_rate" in r.json)

    # -------------------------------------------------------------
    # WORKFLOW 3: Loan Request & Live Reverse Auction
    # -------------------------------------------------------------
    print("\n>>> WORKFLOW 3: Loan Creation, Bidding & Reverse Auction")
    r = client.get("/loan-request")
    check("GET /loan-request (Screen 2)", r.status_code == 200)

    # 3.1 Create Loan Request
    r = client.post("/api/loans/create", json={
        "amount": 2800,
        "purpose": "Course registration top-up",
        "repay_by": "Oct 15, 2026",
        "max_rate": 5.0,
        "message": "Urgent lab fee clearance"
    })
    loan_id = r.json.get("loan_id") if r.status_code == 200 else None
    check("POST /api/loans/create", r.status_code == 200 and loan_id is not None, f"Created Loan ID: {loan_id}")

    # 3.2 View Reverse Auction for Created Loan
    r = client.get(f"/auction?id={loan_id}")
    check("GET /auction for new loan (Screen 3)", r.status_code == 200)

    # 3.3 Fetch bids via AJAX
    r = client.get(f"/api/auction/{loan_id}/bids")
    initial_bids_count = len(r.json) if r.status_code == 200 else 0
    check("GET /api/auction/<id>/bids", r.status_code == 200 and initial_bids_count >= 1, f"Found {initial_bids_count} bids")

    # 3.4 Place lower bid as a peer lender
    r = client.post(f"/api/auction/{loan_id}/bid", json={
        "rate": 2.8,
        "notes": "Fast bKash disbursement from campus"
    })
    check("POST /api/auction/<id>/bid (Lower Interest Bid)", r.status_code == 200)

    # 3.5 Accept the winning bid
    r = client.post(f"/api/auction/{loan_id}/accept")
    check("POST /api/auction/<id>/accept (Award Loan)", r.status_code == 200)

    # -------------------------------------------------------------
    # WORKFLOW 4: Loan Repayment & Grace Extension
    # -------------------------------------------------------------
    print("\n>>> WORKFLOW 4: Active Loan Repayment & Grace Extension")
    r = client.get("/repayment")
    check("GET /repayment (Screen 4)", r.status_code == 200)

    # 4.1 Request 7-day grace extension
    r = client.post(f"/api/loans/{loan_id}/extend")
    check("POST /api/loans/<id>/extend (7-Day Grace Extension)", r.status_code == 200)

    # 4.2 Submit a repayment
    r = client.post(f"/api/loans/{loan_id}/repay", json={
        "amount": 500,
        "payment_method": "bKash"
    })
    check("POST /api/loans/<id>/repay (Partial Repayment via bKash)", r.status_code == 200 and "trx_id" in r.json)

    # -------------------------------------------------------------
    # WORKFLOW 5: Campus Gig Board, Gig Score & Freelancer Dashboard
    # -------------------------------------------------------------
    print("\n>>> WORKFLOW 5: Campus Gig Board, Gig Score & Freelancer Dashboard")
    # 5.1 Gig Board with Gig Score & Statistics
    r = client.get("/gigs")
    check("GET /gigs (Screen 6)", r.status_code == 200 and b"Gig Score" in r.data and b"Micro-Economy Volume" in r.data)

    # 5.2 Post a Gig
    r = client.post("/api/gigs/post", json={
        "title": "Audit Test: Python Machine Learning Script",
        "category": "Tech & Code",
        "budget": 1200,
        "due_info": "due in 3 days"
    })
    posted_gig = r.json.get("gig", {})
    check("POST /api/gigs/post with Gig Score metadata", r.status_code == 200 and "gig_score" in posted_gig and "gig_tier" in posted_gig, f"Score: {posted_gig.get('gig_score')}, Tier: {posted_gig.get('gig_tier')}")

    # 5.3 Apply for the Gig
    gig_id = r.json.get("gig_id")
    r = client.post(f"/api/gigs/{gig_id}/apply")
    check("POST /api/gigs/<id>/apply", r.status_code == 200)

    # 5.4 Complete Gig and Sync Gig Score
    r = client.post(f"/api/gigs/{gig_id}/complete", json={
        "rating": 5.0,
        "review": "Completed gig with exceptional quality"
    })
    check("POST /api/gigs/<id>/complete (Dynamic Gig Score Sync)", r.status_code == 200 and "new_gig_score" in r.json, f"New Score: {r.json.get('new_gig_score')}")

    # 5.5 Delete Gig
    r = client.post(f"/api/gigs/{gig_id}/delete")
    check("POST /api/gigs/<id>/delete (Poster Gig Deletion)", r.status_code == 200)

    # 5.6 Dedicated Gig Score Dashboard
    r = client.get("/gig-score")
    check("GET /gig-score (Dedicated Gig Dashboard)", r.status_code == 200 and b"Task Fulfillment" in r.data and b"Progression Log" in r.data)

    r_alias = client.get("/gig-dashboard")
    check("GET /gig-dashboard alias route", r_alias.status_code == 200)

    # -------------------------------------------------------------
    # WORKFLOW 6: Crowdfunding, Statistics & Per-Donation Expenditure
    # -------------------------------------------------------------
    print("\n>>> WORKFLOW 6: Crowdfunding, Deep Data KPIs & Expenditure Transparency")
    # 6.1 Crowdfunding Screen
    r = client.get("/crowdfunding")
    check("GET /crowdfunding (Screen 5)", r.status_code == 200 and b"Verified Disbursement" in r.data and b"Your Donation's Direct Impact" in r.data)

    # 6.2 Student Creates New Crowdfunding Campaign
    r = client.post("/api/crowdfunding/create", json={
        "title": "Audit Test: Surgery Support for CSE Senior",
        "category": "Emergency Medical",
        "goal_amount": 35000,
        "story": "Urgent financial medical support for senior student undergoing appendix operation."
    })
    new_camp_id = r.json.get("campaign_id") if r.status_code == 200 else 1
    check("POST /api/crowdfunding/create (Student Initiated)", r.status_code == 200 and new_camp_id is not None, f"Created Campaign #{new_camp_id}")

    # 6.3 Admin Approves Crowdfunding Campaign
    r = client.post("/api/admin/campaign/approve", json={"campaign_id": new_camp_id})
    check("POST /api/admin/campaign/approve (Admin Verification)", r.status_code == 200)

    # 6.4 Admin Inputs Itemized Expenditure Receipt
    r = client.post("/api/admin/expenditure/add", json={
        "campaign_id": new_camp_id,
        "category": "Surgery & Operating Theater",
        "vendor": "Apollo Hospitals Dhaka",
        "invoice_no": "INV-AUDIT-99",
        "item_name": "Laparoscopic Surgical Pack",
        "quantity": "1 Kit",
        "amount": 18000
    })
    check("POST /api/admin/expenditure/add (Admin Input Itemized Invoice)", r.status_code == 200)

    # 6.5 Per-Donation Expenditure Impact API
    r = client.get(f"/api/crowdfunding/{new_camp_id}/expenditure-impact?amount=1500")
    breakdown = r.json.get("breakdown", [])
    check("GET /api/crowdfunding/<id>/expenditure-impact", r.status_code == 200 and len(breakdown) >= 1, f"Calculated {len(breakdown)} itemized categories for 1500 Tk")

    # 6.6 Submit Real Donation
    r = client.post(f"/api/crowdfunding/{new_camp_id}/donate", json={
        "amount": 750,
        "donor_name": "Audit Test Backer",
        "is_anonymous": False,
        "payment_method": "Nagad"
    })
    check("POST /api/crowdfunding/<id>/donate", r.status_code == 200 and "trx_id" in r.json, f"Amount: {r.json.get('amount')} Tk, Trx: {r.json.get('trx_id')}")

    # -------------------------------------------------------------
    # WORKFLOW 7: Anonymous Meal Drops
    # -------------------------------------------------------------
    print("\n>>> WORKFLOW 7: Anonymous Meal Drops (Gift & Claim)")
    r = client.get("/meal-drops")
    check("GET /meal-drops (Screen 7)", r.status_code == 200)

    # 7.1 Gift meal
    r = client.post("/api/meals/gift", json={"meals_count": 1})
    claim_code = r.json.get("claim_code")
    check("POST /api/meals/gift (Cafeteria Token)", r.status_code == 200 and claim_code is not None, f"Generated Code: {claim_code}")

    # 7.2 Claim meal
    r = client.post("/api/meals/claim")
    check("POST /api/meals/claim (Anonymous Token Claim)", r.status_code == 200 and "claim_code" in r.json)

    # -------------------------------------------------------------
    # WORKFLOW 8: Trust Profile & Reputation
    # -------------------------------------------------------------
    print("\n>>> WORKFLOW 8: Campus Trust Profile & Reputation")
    r = client.get("/trust-profile")
    check("GET /trust-profile (Screen 8)", r.status_code == 200 and b"Trust Profile" in r.data)

    # -------------------------------------------------------------
    # WORKFLOW 9: Administration & Audit Console
    # -------------------------------------------------------------
    print("\n>>> WORKFLOW 9: University Administration & Audit Portal")
    r = client.get("/admin")
    check("GET /admin Portal", r.status_code == 200 and b"University Administration Panel" in r.data)

    r = client.post("/api/admin/milestone/verify", json={"milestone_id": 1})
    check("POST /api/admin/milestone/verify", r.status_code == 200)

    r = client.post("/api/admin/user/toggle_verify", json={"user_id": 2})
    check("POST /api/admin/user/toggle_verify", r.status_code == 200)

    # -------------------------------------------------------------
    # WORKFLOW 10: Logout Button Presence Across All Views
    # -------------------------------------------------------------
    print("\n>>> WORKFLOW 10: Logout Accessibility Verification Across Screens")
    screens = ["/dashboard", "/loan-request", "/crowdfunding", "/gigs", "/gig-score", "/meal-drops", "/trust-profile", "/admin"]
    for s in screens:
        res = client.get(s)
        has_logout = b"/logout" in res.data
        check(f"Logout Button Visible on {s}", has_logout)

    # -------------------------------------------------------------
    # FINAL RESULTS SUMMARY
    # -------------------------------------------------------------
    print("\n==================================================================")
    print(f"   AUDIT SUMMARY: {passed}/{total_checks} CHECKS PASSED ({round(passed/total_checks*100, 1)}%)")
    if failed == 0:
        print("   >>> ALL 9 CORE USER WORKFLOWS ARE 100% OPERATIONAL! <<<")
    else:
        print(f"   >>> {failed} CHECKS FAILED! PLEASE REVIEW LOGS. <<<")
    print("==================================================================")

    return failed == 0

if __name__ == "__main__":
    success = run_workflow_audit()
    sys.exit(0 if success else 1)
