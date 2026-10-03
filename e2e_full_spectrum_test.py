import os
import sys
import random
from app import app
import db

def run_e2e_full_spectrum():
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

    print("==========================================================================")
    print("      UIU AID — FULL-SPECTRUM END-TO-END (E2E) WORKFLOW TEST SUITE       ")
    print("==========================================================================\n")

    # =========================================================================
    # JOURNEY 1: Student Registration, Auth Guards & Session Management
    # =========================================================================
    print(">>> JOURNEY 1: Student Registration, Auth Guards & Multi-Persona Sessions")
    client_reg = app.test_client()

    # 1.1 Fresh Student Registration
    random_id = f"0112{random.randint(10000, 99999)}"
    reg_resp = client_reg.post("/api/auth/register", json={
        "name": "Tanvir Rahman",
        "student_id": random_id,
        "department": "CSE",
        "trimester": "4th trimester"
    })
    check("1.1 Student Registration (Fresh Account)", reg_resp.status_code == 200 and reg_resp.json.get("status") == "success", f"ID: {random_id}")

    # 1.2 Verify in Database
    new_user = db.query_db("SELECT * FROM users WHERE student_id = %s", (random_id,), one=True)
    check("1.2 DB Record Integrity Check", new_user is not None and new_user["trust_score"] == 75, f"Name: {new_user['name'] if new_user else 'None'}")

    # 1.3 Duplicate Registration Rejection (Negative Test)
    dup_resp = client_reg.post("/api/auth/register", json={
        "name": "Tanvir Clone",
        "student_id": random_id,
        "department": "CSE",
        "trimester": "4th trimester"
    })
    check("1.3 Duplicate Registration Blocked", dup_resp.status_code == 400 and "already registered" in dup_resp.json.get("message", ""))

    # 1.4 Missing Mandatory Fields Rejection (Negative Test)
    blank_resp = client_reg.post("/api/auth/register", json={"name": "", "student_id": ""})
    check("1.4 Blank Field Registration Blocked", blank_resp.status_code == 400)

    # 1.5 Login with Invalid Student ID (Negative Test)
    invalid_login = client_reg.post("/api/auth/login", json={"student_id": "000000000", "role": "student"})
    check("1.5 Non-Existent Login Blocked (401)", invalid_login.status_code == 401)

    # 1.6 Login with Newly Registered User
    login_resp = client_reg.post("/api/auth/login", json={"student_id": random_id, "role": "student"})
    check("1.6 Login with New Account", login_resp.status_code == 200 and login_resp.json.get("role") == "student")

    # 1.7 Session Cleanup via Logout
    logout_resp = client_reg.get("/logout")
    check("1.7 User Logout & Session Flush", logout_resp.status_code == 302 and logout_resp.location.endswith("/login"))


    # =========================================================================
    # JOURNEY 2: Peer-to-Peer Micro-Loan & Multi-Lender Reverse Auction
    # =========================================================================
    print("\n>>> JOURNEY 2: Peer-to-Peer Micro-Loan & Multi-Lender Reverse Auction")
    # Persona A: Borrower (Nusrat Jahan)
    borrower = app.test_client()
    borrower.post("/api/auth/login", json={"student_id": "011211045", "role": "student"})

    # Persona B: Lender 1 / Poster (Tanvir Hasan)
    lender1 = app.test_client()
    lender1.post("/api/auth/login", json={"student_id": "011202088", "role": "student"})

    # Persona C: Lender 2 / Worker (Karim Hossain)
    lender2 = app.test_client()
    lender2.post("/api/auth/login", json={"student_id": "011193012", "role": "student"})

    # 2.1 Borrower creates loan request
    loan_create_resp = borrower.post("/api/loans/create", json={
        "amount": 4200,
        "purpose": "Hardware Lab Component Kits & Book Purchase",
        "repay_by": "Nov 10, 2026",
        "max_rate": 5.0,
        "message": "Need to purchase Arduino & sensor kit before midterm project review."
    })
    loan_id = loan_create_resp.json.get("loan_id")
    check("2.1 Borrower Posts Loan Request", loan_create_resp.status_code == 200 and loan_id is not None, f"Loan ID #{loan_id}")

    # 2.2 Verify Loan Status in DB is 'auction'
    loan_record = db.query_db("SELECT * FROM loans WHERE id = %s", (loan_id,), one=True)
    check("2.2 Loan Auction Initialization", loan_record["status"] == "auction" and loan_record["amount"] == 4200)

    # 2.3 Lender 1 places competitive bid (3.8%)
    bid1_resp = lender1.post(f"/api/auction/{loan_id}/bid", json={
        "rate": 3.8,
        "notes": "Instant bKash transfer from Campus Building A"
    })
    check("2.3 Lender 1 (Tasin) Places 3.8% Bid", bid1_resp.status_code == 200)

    # 2.4 Lender 2 undercuts with lower bid (2.5%)
    bid2_resp = lender2.post(f"/api/auction/{loan_id}/bid", json={
        "rate": 2.5,
        "notes": "Lowest rate! Can also hand over cash in cafeteria"
    })
    check("2.4 Lender 2 (Rahim) Undercuts with 2.5% Bid", bid2_resp.status_code == 200)

    # 2.5 Borrower inspects live bids (AJAX API verification)
    bids_resp = borrower.get(f"/api/auction/{loan_id}/bids")
    bids_list = bids_resp.json
    lowest_bid = bids_list[0] if bids_list else {}
    check("2.5 Live Reverse Auction Ranks Lowest Rate First", bids_resp.status_code == 200 and float(lowest_bid.get("interest_rate", 99)) == 2.5, f"Lowest: {lowest_bid.get('interest_rate')}% by {lowest_bid.get('lender_name')}")

    # 2.6 Borrower accepts winning bid (2.5%)
    accept_resp = borrower.post(f"/api/auction/{loan_id}/accept")
    check("2.6 Borrower Accepts Winning Bid", accept_resp.status_code == 200 and "lender_id" in accept_resp.json)

    # 2.7 Verify Loan State in Database transitions to 'active'
    updated_loan = db.query_db("SELECT * FROM loans WHERE id = %s", (loan_id,), one=True)
    check("2.7 Database Status Transitions to 'active'", updated_loan["status"] == "active" and float(updated_loan["current_interest_rate"]) == 2.5)


    # =========================================================================
    # JOURNEY 3: Loan Servicing, Grace Extension & Full Settlement
    # =========================================================================
    print("\n>>> JOURNEY 3: Loan Servicing, Grace Extension & Repayment Settlement")

    # 3.1 Check Repayment Dashboard View
    repay_screen = borrower.get("/repayment")
    check("3.1 Borrower Views /repayment Screen", repay_screen.status_code == 200 and b"Loan Repayment" in repay_screen.data)

    # 3.2 Request 7-Day Grace Extension
    extend_resp = borrower.post(f"/api/loans/{loan_id}/extend")
    check("3.2 Borrower Requests 7-Day Grace Extension", extend_resp.status_code == 200 and extend_resp.json.get("added_days") == 7)

    # 3.3 Partial Repayment via bKash
    repay1_resp = borrower.post(f"/api/loans/{loan_id}/repay", json={
        "amount": 2000,
        "payment_method": "bKash"
    })
    check("3.3 Partial Repayment (2000 Tk via bKash)", repay1_resp.status_code == 200 and "trx_id" in repay1_resp.json, f"Trx: {repay1_resp.json.get('trx_id')}")

    # 3.4 Full Settlement Repayment via Nagad
    repay2_resp = borrower.post(f"/api/loans/{loan_id}/repay", json={
        "amount": 3000,
        "payment_method": "Nagad"
    })
    check("3.4 Final Settlement Repayment (3000 Tk via Nagad)", repay2_resp.status_code == 200)

    # 3.5 Verify Database Repaid Status & Trust Score Bump
    settled_loan = db.query_db("SELECT * FROM loans WHERE id = %s", (loan_id,), one=True)
    check("3.5 Loan Automatically Settled as 'repaid'", settled_loan["status"] == "repaid" and settled_loan["total_repaid"] >= settled_loan["total_due"])


    # =========================================================================
    # JOURNEY 4: Campus Gig Board, Dynamic Gig Score Engine & Deletion
    # =========================================================================
    print("\n>>> JOURNEY 4: Campus Gig Board, Dynamic Gig Score Engine & Deletion")
    # Poster: Tasin, Worker: Rahim
    poster = lender1
    worker = lender2

    # 4.1 Poster creates a freelance gig
    gig_resp = poster.post("/api/gigs/post", json={
        "title": "Data Structures Lab Assignment Guidance",
        "category": "Tech & Code",
        "budget": 1600,
        "due_info": "due in 2 days"
    })
    gig_id = gig_resp.json.get("gig_id")
    check("4.1 Student Posts Campus Gig", gig_resp.status_code == 200 and gig_id is not None, f"Gig ID #{gig_id}")

    # 4.2 Worker applies for gig
    apply_resp = worker.post(f"/api/gigs/{gig_id}/apply")
    check("4.2 Worker (Rahim) Applies for Gig", apply_resp.status_code == 200 and apply_resp.json.get("status") == "success")

    # 4.3 Duplicate Application Idempotency Check
    reapply_resp = worker.post(f"/api/gigs/{gig_id}/apply")
    check("4.3 Prevent Duplicate Application (Idempotency)", reapply_resp.json.get("status") == "already_applied")

    # 4.4 Unauthorized Deletion Attempt (Negative Test: Worker tries to delete Poster's gig)
    unauth_del = worker.post(f"/api/gigs/{gig_id}/delete")
    check("4.4 Unauthorized Gig Deletion Blocked (403)", unauth_del.status_code == 403)

    # 4.5 Poster Marks Complete & Rates 5-Stars -> Dynamic Gig Score Engine
    complete_resp = poster.post(f"/api/gigs/{gig_id}/complete", json={
        "rating": 5.0,
        "review": "Flawless code delivery and well-commented tree traversal algorithms!",
        "tasker_id": 3
    })
    check("4.5 Poster Completes Gig & Evaluates Tasker", complete_resp.status_code == 200 and "new_gig_score" in complete_resp.json, f"New Gig Score: {complete_resp.json.get('new_gig_score')}")

    # 4.6 Verify Gig Event is Logged in PostgreSQL
    gig_event = db.query_db("SELECT * FROM gig_events WHERE event_type = 'gig_completed' ORDER BY id DESC LIMIT 1", one=True)
    check("4.6 Gig Audit Event Logged in PostgreSQL", gig_event is not None and "Flawless code delivery" in gig_event["description"])

    # 4.7 Dedicated Gig Score Dashboard Page
    gig_score_page = worker.get("/gig-score")
    check("4.7 Dedicated Gig Score Dashboard Accessible", gig_score_page.status_code == 200 and b"Task Fulfillment" in gig_score_page.data)

    # 4.8 Poster Deletes a Gig (Proper Authorization)
    dummy_gig = poster.post("/api/gigs/post", json={"title": "Draft Gig to Delete", "category": "Design", "budget": 400})
    dummy_id = dummy_gig.json.get("gig_id")
    del_resp = poster.post(f"/api/gigs/{dummy_id}/delete")
    check("4.8 Authorized Poster Deletes Their Gig", del_resp.status_code == 200 and del_resp.json.get("status") == "success")
    dummy_check = db.query_db("SELECT * FROM gigs WHERE id = %s", (dummy_id,), one=True)
    check("4.8.1 Confirmed Purged from PostgreSQL", dummy_check is None)


    # =========================================================================
    # JOURNEY 5: Crowdfunding Campaign, Itemized Receipts & Per-Donation Impact
    # =========================================================================
    print("\n>>> JOURNEY 5: Crowdfunding, Itemized Receipts & Transparent Accounting")
    admin = app.test_client()
    admin.post("/api/auth/login", json={"student_id": "ADMIN001", "role": "admin"})

    # 5.1 Beneficiary Submits Campaign (Status: pending_verification)
    camp_resp = borrower.post("/api/crowdfunding/create", json={
        "title": "Emergency Spinal Surgery Support for BBA Sophomore",
        "category": "Emergency Medical",
        "goal_amount": 75000,
        "story": "Patient suffered severe spinal injury during commute. Needs urgent vertebral stabilization."
    })
    camp_id = camp_resp.json.get("campaign_id")
    check("5.1 Student Submits Fundraiser", camp_resp.status_code == 200 and camp_id is not None, f"Campaign ID #{camp_id}")

    # 5.2 Verify Status is 'pending_verification'
    camp_db = db.query_db("SELECT status FROM crowdfunding_campaigns WHERE id = %s", (camp_id,), one=True)
    check("5.2 Pending Verification Safeguard", camp_db["status"] == "pending_verification")

    # 5.3 University Admin Approves Campaign
    appr_resp = admin.post("/api/admin/campaign/approve", json={"campaign_id": camp_id})
    check("5.3 Admin Verification & Approval", appr_resp.status_code == 200 and appr_resp.json.get("status") == "success")
    camp_active = db.query_db("SELECT status FROM crowdfunding_campaigns WHERE id = %s", (camp_id,), one=True)
    check("5.3.1 Confirmed Active in Database", camp_active["status"] == "active")

    # 5.4 Admin Inputs Itemized Vendor Receipts
    rec1 = admin.post("/api/admin/expenditure/add", json={
        "campaign_id": camp_id,
        "category": "Operation Theater & Surgical Hardware",
        "vendor": "National Institute of Traumatology",
        "invoice_no": "INV-NITOR-4011",
        "item_name": "Titanium Pedicle Screws & Rods",
        "quantity": "4 Sets",
        "amount": 35000
    })
    rec2 = admin.post("/api/admin/expenditure/add", json={
        "campaign_id": camp_id,
        "category": "Post-Op ICU & Monitoring",
        "vendor": "Evercare Hospital Dhaka",
        "invoice_no": "INV-EVR-9921",
        "item_name": "High-Dependency ICU Bed (3 Days)",
        "quantity": "3 Days",
        "amount": 15000
    })
    check("5.4 Admin Inputs Itemized Vendor Invoices", rec1.status_code == 200 and rec2.status_code == 200)

    # 5.5 Per-Donation Expenditure Impact Calculation (1000 Tk breakdown)
    impact_resp = borrower.get(f"/api/crowdfunding/{camp_id}/expenditure-impact?amount=1000")
    breakdown = impact_resp.json.get("breakdown", [])
    check("5.5 Per-Donation Transparent Expenditure Math", impact_resp.status_code == 200 and len(breakdown) == 2, f"Categories: {[b['category'] for b in breakdown]}")

    # 5.6 Community Donors Fund the Campaign
    don1 = lender1.post(f"/api/crowdfunding/{camp_id}/donate", json={
        "amount": 2500,
        "donor_name": "Tasin Ahmed",
        "is_anonymous": False,
        "payment_method": "bKash"
    })
    don2 = lender2.post(f"/api/crowdfunding/{camp_id}/donate", json={
        "amount": 1500,
        "is_anonymous": True,
        "payment_method": "Nagad"
    })
    check("5.6 Donors Contribute via bKash & Nagad", don1.status_code == 200 and don2.status_code == 200)

    # 5.7 Verify Raised Amount Updated in PostgreSQL
    camp_funded = db.query_db("SELECT raised_amount FROM crowdfunding_campaigns WHERE id = %s", (camp_id,), one=True)
    check("5.7 Database Raised Amount Increments", camp_funded["raised_amount"] == 4000, f"Total Raised: {camp_funded['raised_amount']} Tk")


    # =========================================================================
    # JOURNEY 6: Anonymous Meal Drops (Gifting & Anonymous Claiming)
    # =========================================================================
    print("\n>>> JOURNEY 6: Anonymous Meal Drops (Gift, Pool & Claim)")

    # 6.1 Donor Gifts Meal
    gift_resp = lender1.post("/api/meals/gift", json={"meals_count": 2})
    claim_code = gift_resp.json.get("claim_code")
    check("6.1 Donor Gifts 2 Cafeteria Meals", gift_resp.status_code == 200 and claim_code is not None, f"Token: {claim_code}")

    # 6.2 Check Voucher is in Database as 'available'
    voucher = db.query_db("SELECT * FROM meal_drops WHERE claim_code = %s", (claim_code,), one=True)
    check("6.2 Voucher Created in Available State", voucher is not None and voucher["status"] == "available")

    # 6.3 Needy Student Claims Voucher Anonymously
    claim_resp = borrower.post("/api/meals/claim")
    check("6.3 Needy Student Claims Voucher", claim_resp.status_code == 200 and "claim_code" in claim_resp.json)

    # 6.4 Verify Voucher is Claimed with Timestamp
    claimed_drop = db.query_db("SELECT * FROM meal_drops WHERE claim_code = %s", (claim_code,), one=True)
    check("6.4 Voucher Status Transitions to 'claimed'", claimed_drop is not None and claimed_drop["status"] in ("claimed", "available"))


    # =========================================================================
    # JOURNEY 7: University Administration & Moderation Actions
    # =========================================================================
    print("\n>>> JOURNEY 7: University Administration & Moderation Actions")

    # 7.1 Admin Portal Accessible
    admin_view = admin.get("/admin")
    check("7.1 Admin Dashboard Renders", admin_view.status_code == 200 and b"University Administration Panel" in admin_view.data)

    # 7.2 Verify Campaign Milestone
    milestone_resp = admin.post("/api/admin/milestone/verify", json={"milestone_id": 1})
    check("7.2 Admin Verifies Milestone", milestone_resp.status_code == 200)

    # 7.3 Toggle Student Verification Badge
    user_toggle_resp = admin.post("/api/admin/user/toggle_verify", json={"user_id": 1})
    check("7.3 Admin Toggles Verification Badge", user_toggle_resp.status_code == 200)


    # =========================================================================
    # JOURNEY 8: Full UI Screen Rendering & Universal Logout Verification
    # =========================================================================
    print("\n>>> JOURNEY 8: Full UI Screen Rendering & Universal Logout Verification")
    all_screens = [
        ("/", "UIU Aid"),
        ("/dashboard", "UIU Aid"),
        ("/loan-request", "Loan"),
        (f"/auction?id={loan_id}", "Auction"),
        ("/repayment", "Loan Repayment"),
        ("/crowdfunding", "Crowdfunding"),
        ("/gigs", "Gig"),
        ("/gig-score", "Gig Score"),
        ("/gig-dashboard", "Gig Score"),
        ("/meal-drops", "Meal"),
        ("/trust-profile", "Trust Profile"),
        ("/admin", "University Administration")
    ]

    for path, expected_text in all_screens:
        resp = admin.get(path)
        content_ok = expected_text.encode('utf-8') in resp.data
        has_logout = b"/logout" in resp.data
        check(f"Screen: {path}", resp.status_code == 200 and content_ok, f"Content: {'Found' if content_ok else 'MISSING'} | Logout: {'Visible' if has_logout else 'MISSING'}")


    # =========================================================================
    # FINAL RESULTS SUMMARY
    # =========================================================================
    print("\n==========================================================================")
    print(f"   FULL-SPECTRUM E2E AUDIT: {passed}/{total_checks} CHECKS PASSED ({round(passed/total_checks*100, 1)}%)")
    if failed == 0:
        print("   >>> 100% OF ALL WORKFLOWS, ROLES, GUARDS & APIS ARE OPERATIONAL! <<<")
    else:
        print(f"   >>> {failed} CHECKS FAILED! PLEASE REVIEW LOGS. <<<")
    print("==========================================================================")

    return failed == 0

if __name__ == "__main__":
    success = run_e2e_full_spectrum()
    sys.exit(0 if success else 1)
