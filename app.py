import os
import random
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv
import db

load_dotenv()

base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(
    __name__,
    static_folder=os.path.join(base_dir, "static"),
    template_folder=os.path.join(base_dir, "templates")
)
app.secret_key = os.getenv("SECRET_KEY", "uiu-aid-secret-key-2026")

def get_current_user():
    """Helper to fetch logged in user from session or fallback to default."""
    user_id = session.get('user_id')
    if user_id:
        user = db.query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
        if user:
            return user
    # Default demo user (Nusrat Jahan)
    return db.query_db("SELECT * FROM users WHERE id = 1", one=True)

# -------------------------------------------------------------
# Auth Routes (Login, Register, Logout, Role-based Redirection)
# -------------------------------------------------------------

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    student_id = data.get('student_id', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'student')
    
    # 1. Admin login credentials
    if student_id.upper() == 'ADMIN001':
        session['user_id'] = 0
        session['role'] = 'admin'
        session['name'] = 'University Administrator'
        return jsonify({'status': 'success', 'role': 'admin', 'redirect': '/admin'})
    
    # 2. Student / Lender check against PostgreSQL
    user = db.query_db(
        "SELECT * FROM users WHERE student_id = %s",
        (student_id,), one=True
    )
    
    if user:
        session['user_id'] = user['id']
        session['role'] = role
        session['name'] = user['name']
        session['student_id'] = user['student_id']

        if role == 'lender':
            return jsonify({'status': 'success', 'role': 'lender', 'redirect': '/auction'})
        return jsonify({'status': 'success', 'role': role, 'redirect': '/'})
    else:
        return jsonify({'status': 'error', 'message': f"Student ID '{student_id}' not found. Please verify or register."}), 401

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    student_id = data.get('student_id', '').strip()
    department = data.get('department', 'CSE').strip()
    trimester = data.get('trimester', '1st trimester').strip()
    
    if not name or not student_id:
        return jsonify({'status': 'error', 'message': 'Name and Student ID are required.'}), 400

    existing = db.query_db("SELECT id FROM users WHERE student_id = %s", (student_id,), one=True)
    if existing:
        return jsonify({'status': 'error', 'message': f"Student ID '{student_id}' is already registered."}), 400

    # Derive initials
    parts = name.split()
    initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()
    avatar_class = f"av-{random.randint(1, 6)}"

    res = db.execute_db("""
        INSERT INTO users (name, initials, student_id, department, trimester, trust_score, tier, borrowing_limit, borrowed_amount, lent_amount, is_verified, avatar_class)
        VALUES (%s, %s, %s, %s, %s, 75, 'Silver', 3000, 0, 0, TRUE, %s)
        RETURNING id;
    """, (name, initials, student_id, department, trimester, avatar_class), returning=True)

    # Add welcome trust event
    db.execute_db("""
        INSERT INTO trust_events (user_id, event_type, points_delta, description)
        VALUES (%s, 'account_created', 5, 'Welcome to UIU Aid Community Network');
    """, (res['id'],))

    return jsonify({'status': 'success', 'message': f"Account registered for {name}. Please sign in."})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# -------------------------------------------------------------
# Admin Console & Administrative APIs
# -------------------------------------------------------------

@app.route('/admin')
def admin_panel():
    """Full-featured Administration and Audit Portal."""
    users = db.query_db("SELECT * FROM users ORDER BY id ASC")
    loans = db.query_db("""
        SELECT l.*, u.name as borrower_name, u.department as borrower_dept, u.trust_score as borrower_trust
        FROM loans l
        JOIN users u ON l.borrower_id = u.id
        ORDER BY l.id DESC
    """)
    milestones = db.query_db("""
        SELECT m.*, c.title as campaign_title
        FROM milestones m
        JOIN crowdfunding_campaigns c ON m.campaign_id = c.id
        ORDER BY m.id DESC
    """)
    campaigns = db.query_db("SELECT * FROM crowdfunding_campaigns ORDER BY id DESC")
    expenditures = db.query_db("""
        SELECT e.*, c.title as campaign_title 
        FROM expenditures e 
        JOIN crowdfunding_campaigns c ON e.campaign_id = c.id 
        ORDER BY e.id DESC
    """)
    total_loans = db.query_db("SELECT COALESCE(SUM(amount), 0) as total FROM loans WHERE status IN ('active','repaid')", one=True)
    available_meals = db.query_db("SELECT count(*) as count FROM meal_drops WHERE status = 'available'", one=True)["count"]
    
    return render_template(
        'admin.html',
        users=users,
        loans=loans,
        milestones=milestones,
        campaigns=campaigns,
        expenditures=expenditures,
        total_facilitated=int(total_loans['total']),
        available_meals=available_meals
    )

@app.route('/api/admin/loan/approve', methods=['POST'])
def api_admin_approve_loan():
    data = request.get_json() or {}
    loan_id = data.get('loan_id')
    db.execute_db("UPDATE loans SET status = 'active' WHERE id = %s", (loan_id,))
    return jsonify({'status': 'success'})

@app.route('/api/admin/milestone/verify', methods=['POST'])
def api_admin_verify_milestone():
    data = request.get_json() or {}
    milestone_id = data.get('milestone_id')
    db.execute_db("UPDATE milestones SET status = 'verified' WHERE id = %s", (milestone_id,))
    return jsonify({'status': 'success'})

@app.route('/api/admin/campaign/approve', methods=['POST'])
def api_admin_approve_campaign():
    data = request.get_json() or {}
    campaign_id = data.get('campaign_id')
    db.execute_db("UPDATE crowdfunding_campaigns SET status = 'active' WHERE id = %s", (campaign_id,))
    return jsonify({'status': 'success', 'message': 'Campaign approved and now live!'})

@app.route('/api/admin/expenditure/add', methods=['POST'])
def api_admin_add_expenditure():
    """Admin or Medical Committee audits and logs itemized hospital/equipment receipts."""
    data = request.get_json() or {}
    campaign_id = int(data.get("campaign_id", 1))
    category = data.get("category", "Hospital & Room Charges").strip()
    vendor = data.get("vendor", "Evercare Hospital Dhaka").strip()
    invoice_no = data.get("invoice_no", f"INV-{random.randint(10000, 99999)}").strip()
    item_name = data.get("item_name", "Medical Procedure").strip()
    quantity = data.get("quantity", "1 Unit").strip()
    amount = int(data.get("amount", 5000))
    verified_by = data.get("verified_by", "UIU Medical Centre Audit Committee")

    db.execute_db("""
        INSERT INTO expenditures (campaign_id, category, vendor, invoice_no, item_name, quantity, amount, status, verified_by, receipt_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'verified', %s, 'Oct 3, 2026');
    """, (campaign_id, category, vendor, invoice_no, item_name, quantity, amount, verified_by))

    return jsonify({"status": "success", "message": f"Expenditure receipt of {amount} Tk verified and logged!"})

@app.route('/api/admin/user/toggle_verify', methods=['POST'])
def api_admin_toggle_verify():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    db.execute_db("UPDATE users SET is_verified = NOT is_verified WHERE id = %s", (user_id,))
    return jsonify({'status': 'success'})

# -------------------------------------------------------------
# Web Page Routes (The 8 UIU Aid Screens)
# -------------------------------------------------------------

@app.route("/")
@app.route("/dashboard")
def dashboard():
    """Screen 1: Student Dashboard"""
    user = get_current_user()
    active_loan = db.query_db("SELECT * FROM loans WHERE borrower_id = %s AND status = 'active' ORDER BY id DESC", (user['id'],), one=True)
    if not active_loan:
        active_loan = db.query_db("SELECT * FROM loans WHERE status = 'active' ORDER BY id DESC", one=True)
    return render_template("dashboard.html", active_page="dashboard", user=user, active_loan=active_loan)

@app.route("/loan-request")
def loan_request():
    """Screen 2: Request a Loan"""
    user = get_current_user()
    return render_template("loan_request.html", active_page="loans", user=user)

@app.route("/auction")
def reverse_auction():
    """Screen 3: Live Reverse Auction"""
    loan_id = request.args.get("id")
    if loan_id:
        loan = db.query_db("SELECT * FROM loans WHERE id = %s", (loan_id,), one=True)
    else:
        loan = db.query_db("SELECT * FROM loans WHERE status = 'auction' ORDER BY id DESC", one=True)
    
    borrower = None
    if loan:
        borrower = db.query_db("SELECT * FROM users WHERE id = %s", (loan["borrower_id"],), one=True)
    
    bids = []
    if loan:
        bids = db.query_db("""
            SELECT b.*, u.name as lender_name, u.initials, u.avatar_class 
            FROM loan_bids b
            JOIN users u ON b.lender_id = u.id
            WHERE b.loan_id = %s
            ORDER BY b.interest_rate ASC, b.created_at DESC
        """, (loan["id"],))
    
    lowest_bid = bids[0] if bids else None
    user = get_current_user()
    return render_template("reverse_auction.html", active_page="auction", loan=loan, borrower=borrower, bids=bids, lowest_bid=lowest_bid, user=user)

@app.route("/repayment")
def loan_repayment():
    """Screen 4: Active Loan Repayment"""
    user = get_current_user()
    loan = db.query_db("SELECT * FROM loans WHERE borrower_id = %s AND status = 'active' ORDER BY id ASC", (user['id'],), one=True)
    if not loan:
        loan = db.query_db("SELECT * FROM loans WHERE status = 'active' ORDER BY id ASC", one=True)
        
    lender = None
    if loan and loan.get('winning_lender_id'):
        lender = db.query_db("SELECT * FROM users WHERE id = %s", (loan['winning_lender_id'],), one=True)
    elif loan:
        winning_bid = db.query_db("SELECT * FROM loan_bids WHERE loan_id=%s AND is_winning=TRUE LIMIT 1", (loan['id'],), one=True)
        if winning_bid:
            lender = db.query_db("SELECT * FROM users WHERE id=%s", (winning_bid['lender_id'],), one=True)
    return render_template("loan_repayment.html", active_page="repayment", loan=loan, user=user, lender=lender)

@app.route("/crowdfunding")
def crowdfunding():
    """Screen 5: Crowdfunding & Transparency with Deep Data & Itemized Expenditures"""
    campaign_id = request.args.get("id", 1)
    campaign = db.query_db("SELECT * FROM crowdfunding_campaigns WHERE id = %s", (campaign_id,), one=True)
    if not campaign:
        campaign = db.query_db("SELECT * FROM crowdfunding_campaigns ORDER BY id ASC", one=True)
    
    camp_id = campaign["id"] if campaign else 1
    milestones = db.query_db("SELECT * FROM milestones WHERE campaign_id = %s ORDER BY id ASC", (camp_id,))
    expenditures = db.query_db("SELECT * FROM expenditures WHERE campaign_id = %s ORDER BY id ASC", (camp_id,))
    donations = db.query_db("SELECT * FROM donations WHERE campaign_id = %s ORDER BY created_at DESC", (camp_id,))
    user = get_current_user()

    # Data-heavy statistics computation
    goal = campaign["goal_amount"] if campaign else 45000
    raised = campaign["raised_amount"] if campaign else 38400
    deficit = max(0, goal - raised)
    pct_funded = min(100.0, round((raised / goal) * 100, 1)) if goal > 0 else 0
    
    donor_count = len(donations)
    avg_donation = round(raised / donor_count) if donor_count > 0 else 0
    
    # Expenditures breakdown by category
    total_expenditure = sum(e["amount"] for e in expenditures) if expenditures else 38400
    categories_map = {}
    if expenditures:
        for e in expenditures:
            cat = e["category"]
            categories_map[cat] = categories_map.get(cat, 0) + e["amount"]
    
    cat_breakdown = []
    if categories_map:
        for cat, amt in categories_map.items():
            pct = round((amt / total_expenditure) * 100, 1) if total_expenditure > 0 else 0
            cat_breakdown.append({"category": cat, "amount": amt, "percent": pct})
    else:
        cat_breakdown = [
            {"category": "Hospital & Room Charges", "amount": 15000, "percent": 39.1},
            {"category": "Surgery & Operating Theater", "amount": 20000, "percent": 52.1},
            {"category": "Post-Op Pharmacy", "amount": 3400, "percent": 8.8}
        ]

    days_left = campaign.get("days_left", 6) if campaign else 6
    stats = {
        "goal": goal,
        "raised": raised,
        "deficit": deficit,
        "pct_funded": pct_funded,
        "donor_count": donor_count,
        "avg_donation": avg_donation,
        "verified_disbursement_rate": 100,
        "daily_velocity_needed": round(deficit / max(1, days_left)),
        "days_left": days_left,
        "total_expenditure": total_expenditure,
        "categories": cat_breakdown
    }

    all_campaigns = db.query_db("SELECT * FROM crowdfunding_campaigns ORDER BY id ASC")

    return render_template(
        "crowdfunding.html",
        active_page="crowdfunding",
        campaign=campaign,
        all_campaigns=all_campaigns,
        milestones=milestones,
        expenditures=expenditures,
        donations=donations,
        user=user,
        stats=stats
    )

@app.route("/gigs")
def gig_board():
    """Screen 6: Campus Gig Board with Gig Score & Micro-Economy Statistics"""
    gigs = db.query_db("""
        SELECT g.*, u.name as poster_name, u.initials, u.avatar_class, 
               COALESCE(u.gig_score, 88) as gig_score,
               COALESCE(u.gig_rating, 4.90) as gig_rating,
               COALESCE(u.gig_tier, 'Level 2 Tasker') as gig_tier
        FROM gigs g
        JOIN users u ON g.poster_id = u.id
        ORDER BY g.id DESC
    """)
    user = get_current_user()

    # Community Gig Board Analytics
    total_vol = db.query_db("SELECT COALESCE(SUM(budget), 0) as total FROM gigs", one=True)["total"]
    open_count = db.query_db("SELECT COUNT(*) as count FROM gigs WHERE status = 'open'", one=True)["count"]
    total_applicants = db.query_db("SELECT COALESCE(SUM(applicants_count), 0) as total FROM gigs", one=True)["total"]
    avg_payout = db.query_db("SELECT COALESCE(ROUND(AVG(budget)), 0) as avg FROM gigs", one=True)["avg"]
    active_taskers = db.query_db("SELECT COUNT(DISTINCT poster_id) as count FROM gigs", one=True)["count"]

    gig_stats = {
        "total_facilitated": int(total_vol) + 42000,
        "open_gigs": open_count,
        "fulfillment_rate": 96.4,
        "avg_payout": int(avg_payout) if avg_payout else 690,
        "active_taskers": int(active_taskers) + 128,
        "total_applicants": int(total_applicants)
    }

    return render_template("gig_board.html", active_page="gigs", gigs=gigs, user=user, stats=gig_stats)

@app.route("/gig-score")
@app.route("/gig-dashboard")
def gig_score_dashboard():
    """Dedicated Gig Score & Campus Freelancer Dashboard"""
    user = get_current_user()
    events = db.query_db("SELECT * FROM gig_events WHERE user_id = %s ORDER BY id DESC", (user['id'],))
    if not events:
        events = db.query_db("SELECT * FROM gig_events ORDER BY id DESC LIMIT 5")

    metrics = {
        "score": user.get('gig_score') or 94,
        "tier": user.get('gig_tier') or 'Elite Campus Freelancer',
        "rating": float(user.get('gig_rating') or 4.95),
        "completion_rate": 98.2,
        "ontime_rate": 96.5,
        "response_time": "14 mins",
        "completed_tasks": user.get('gigs_completed') or 8,
        "posted_tasks": user.get('gigs_posted') or 1,
        "total_earned": 8450,
        "escrow_pending": 800,
        "campus_percentile": "Top 5% at UIU"
    }
    return render_template("gig_score.html", active_page="gig_score", user=user, metrics=metrics, events=events)

@app.route("/meal-drops")
def meal_drops():
    """Screen 7: Anonymous Meal Drops"""
    available_count = db.query_db("SELECT COUNT(*) as count FROM meal_drops WHERE status = 'available'", one=True)["count"]
    total_shared = 213 + db.query_db("SELECT COUNT(*) as count FROM meal_drops", one=True)["count"]
    recent_drops = db.query_db("SELECT * FROM meal_drops ORDER BY created_at DESC LIMIT 10")
    user = get_current_user()
    return render_template("meal_drops.html", active_page="meals", total_available=available_count, total_shared=total_shared, recent_drops=recent_drops, user=user)

@app.route("/trust-profile")
def trust_profile():
    """Screen 8: Campus Trust Profile & Reputation"""
    user = get_current_user()
    events = db.query_db("SELECT * FROM trust_events WHERE user_id = %s ORDER BY id DESC", (user['id'],))
    return render_template("trust_profile.html", active_page="trust", user=user, events=events)


# -------------------------------------------------------------
# REST API Endpoints (Real Interactive Backend Actions)
# -------------------------------------------------------------

@app.route("/api/loans/create", methods=["POST"])
def api_create_loan():
    """Create a new loan request and place it on the reverse auction board."""
    user = get_current_user()
    data = request.get_json() or {}
    amount = int(data.get("amount", 3000))
    purpose = data.get("purpose", "Urgent campus expense")
    repay_by = data.get("repay_by", "Sep 5, 2026")
    max_rate = float(data.get("max_rate", 5.0))
    message = data.get("message", "Request for student loan.")

    res = db.execute_db("""
        INSERT INTO loans (borrower_id, amount, purpose, repay_by, max_interest_rate, current_interest_rate, message, status, due_date, total_due)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'auction', %s, %s)
        RETURNING id;
    """, (user['id'], amount, purpose, repay_by, max_rate, max_rate, message, repay_by, int(amount * (1 + max_rate/100))), returning=True)

    loan_id = res["id"]

    db.execute_db("""
        INSERT INTO loan_bids (loan_id, lender_id, interest_rate, notes)
        VALUES 
        (%s, 3, 4.5, 'Can disburse right away via bKash'),
        (%s, 4, 4.0, 'Available via bKash or cafeteria handover');
    """, (loan_id, loan_id))

    return jsonify({"status": "success", "loan_id": loan_id})

@app.route("/api/auction/<int:loan_id>/bid", methods=["POST"])
def api_place_bid(loan_id):
    """Lenders place lower bids in the reverse auction."""
    user = get_current_user()
    data = request.get_json() or {}
    rate = float(data.get("rate", 3.0))
    notes = data.get("notes", "Instant transfer")

    db.execute_db("""
        INSERT INTO loan_bids (loan_id, lender_id, interest_rate, notes)
        VALUES (%s, %s, %s, %s);
    """, (loan_id, user['id'], rate, notes))

    db.execute_db("""
        UPDATE loans 
        SET current_interest_rate = LEAST(current_interest_rate, %s)
        WHERE id = %s;
    """, (rate, loan_id))

    return jsonify({"status": "success"})

@app.route("/api/auction/<int:loan_id>/accept", methods=["POST"])
def api_accept_bid(loan_id):
    """Accept the lowest bid and transition loan to active."""
    winning_bid = db.query_db("""
        SELECT * FROM loan_bids 
        WHERE loan_id = %s 
        ORDER BY interest_rate ASC, created_at ASC 
        LIMIT 1;
    """, (loan_id,), one=True)

    if not winning_bid:
        return jsonify({"status": "error", "message": "No bids to accept"}), 400

    db.execute_db("""
        UPDATE loan_bids SET is_winning = TRUE WHERE id = %s;
    """, (winning_bid["id"],))

    db.execute_db("""
        UPDATE loans 
        SET status = 'active', winning_lender_id = %s, current_interest_rate = %s
        WHERE id = %s;
    """, (winning_bid["lender_id"], winning_bid["interest_rate"], loan_id))

    return jsonify({"status": "success", "lender_id": winning_bid["lender_id"]})

@app.route("/api/loans/<int:loan_id>/repay", methods=["POST"])
def api_repay_loan(loan_id):
    """Submit a loan repayment via bKash/Nagad."""
    user = get_current_user()
    data = request.get_json() or {}
    amount = int(data.get("amount", 552))
    method = data.get("payment_method", "bKash")
    trx_id = f"TRX{random.randint(10000000, 99999999)}"

    db.execute_db("""
        INSERT INTO repayments (loan_id, payer_id, amount, payment_method, trx_id, status)
        VALUES (%s, %s, %s, %s, %s, 'completed');
    """, (loan_id, user['id'], amount, method, trx_id))

    db.execute_db("""
        UPDATE loans 
        SET total_repaid = total_repaid + %s,
            status = CASE WHEN total_repaid + %s >= total_due THEN 'repaid' ELSE status END
        WHERE id = %s;
    """, (amount, amount, loan_id))

    db.execute_db("""
        UPDATE users 
        SET trust_score = LEAST(100, trust_score + 2),
            borrowed_amount = GREATEST(0, borrowed_amount - %s)
        WHERE id = %s;
    """, (amount, user['id']))

    db.execute_db("""
        INSERT INTO trust_events (user_id, event_type, points_delta, description)
        VALUES (%s, 'loan_repaid', 2, %s);
    """, (user['id'], f"Repaid {amount} Tk on-time via {method} (Trx: {trx_id[:8]})"))

    updated_user = db.query_db("SELECT trust_score FROM users WHERE id = %s", (user['id'],), one=True)
    return jsonify({
        "status": "success",
        "trx_id": trx_id,
        "amount": amount,
        "new_trust_score": updated_user["trust_score"]
    })

@app.route("/api/loans/<int:loan_id>/extend", methods=["POST"])
def api_extend_loan(loan_id):
    """Request 7-day grace period extension."""
    user = get_current_user()
    db.execute_db("""
        UPDATE loans 
        SET days_remaining = days_remaining + 7 
        WHERE id = %s;
    """, (loan_id,))

    db.execute_db("""
        INSERT INTO trust_events (user_id, event_type, points_delta, description)
        VALUES (%s, 'loan_extended', -1, 'Requested 7-day grace extension for active loan');
    """, (user['id'],))

    return jsonify({"status": "success", "added_days": 7})

@app.route("/api/crowdfunding/<int:campaign_id>/donate", methods=["POST"])
def api_donate_crowdfunding(campaign_id):
    """Submit a real crowdfunding donation."""
    data = request.get_json() or {}
    amount = int(data.get("amount", 500))
    donor_name = data.get("donor_name", "Anonymous Peer")
    is_anon = bool(data.get("is_anonymous", False))
    method = data.get("payment_method", "bKash")
    trx_id = f"TXN{random.randint(10000000, 99999999)}"

    db.execute_db("""
        INSERT INTO donations (campaign_id, donor_name, is_anonymous, amount, payment_method, trx_id)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (campaign_id, donor_name, is_anon, amount, method, trx_id))

    db.execute_db("""
        UPDATE crowdfunding_campaigns 
        SET raised_amount = raised_amount + %s 
        WHERE id = %s;
    """, (amount, campaign_id))

    return jsonify({"status": "success", "trx_id": trx_id, "amount": amount})

@app.route("/api/crowdfunding/create", methods=["POST"])
def api_create_campaign():
    """Create a student crowdfunding request (submitted for admin verification)."""
    user = get_current_user()
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    category = data.get("category", "Emergency Aid").strip()
    goal = int(data.get("goal_amount", 50000))
    story = data.get("story", "").strip()

    if not title or not story:
        return jsonify({"status": "error", "message": "Title and story are required."}), 400

    res = db.execute_db("""
        INSERT INTO crowdfunding_campaigns (title, student_name, student_dept, category, goal_amount, raised_amount, story, status, days_left)
        VALUES (%s, %s, %s, %s, %s, 0, %s, 'pending_verification', 14)
        RETURNING id;
    """, (title, user['name'], user['department'], category, goal, story), returning=True)

    return jsonify({
        "status": "success",
        "campaign_id": res["id"],
        "message": "Campaign submitted! Under review by UIU Financial Aid & Medical Board."
    })

@app.route("/api/gigs/post", methods=["POST"])
def api_post_gig():
    """Post a new student gig."""
    user = get_current_user()
    data = request.get_json() or {}
    title = data.get("title", "Untitled Gig")
    category = data.get("category", "Tech & Code")
    budget = int(data.get("budget", 500))
    due_info = data.get("due_info", "due in 2 days")

    result = db.execute_db("""
        INSERT INTO gigs (poster_id, title, category, budget, due_info, applicants_count, status)
        VALUES (%s, %s, %s, %s, %s, 0, 'open')
        RETURNING id;
    """, (user['id'], title, category, budget, due_info), returning=True)

    new_gig = db.query_db("""
        SELECT g.*, u.name as poster_name, u.initials, u.avatar_class, 
               COALESCE(u.gig_score, 88) as gig_score, 
               COALESCE(u.gig_rating, 4.90) as gig_rating, 
               COALESCE(u.gig_tier, 'Level 2 Tasker') as gig_tier 
        FROM gigs g JOIN users u ON g.poster_id = u.id WHERE g.id = %s
    """, (result['id'],), one=True)
    return jsonify({"status": "success", "gig_id": result['id'], "gig": dict(new_gig) if new_gig else {}})

@app.route("/api/crowdfunding/<int:campaign_id>/expenditure-impact")
def api_expenditure_impact(campaign_id):
    """Calculates per-donation expenditure allocation for any given donation amount."""
    try:
        amount = int(request.args.get("amount", 1000))
    except (ValueError, TypeError):
        amount = 1000

    expenditures = db.query_db("SELECT category, SUM(amount) as cat_total FROM expenditures WHERE campaign_id = %s GROUP BY category", (campaign_id,))
    total = sum(e["cat_total"] for e in expenditures) if expenditures else 38400
    
    breakdown = []
    if expenditures and total > 0:
        for e in expenditures:
            ratio = float(e["cat_total"]) / float(total)
            allocated = round(amount * ratio)
            breakdown.append({
                "category": e["category"],
                "ratio_pct": round(ratio * 100, 1),
                "allocated_amount": allocated
            })
    else:
        breakdown = [
            {"category": "Hospital Admission & Bed Charges", "ratio_pct": 39.1, "allocated_amount": round(amount * 0.391)},
            {"category": "Surgical OT & Procedure Kit", "ratio_pct": 52.1, "allocated_amount": round(amount * 0.521)},
            {"category": "Post-Op Pharmacy Medicines", "ratio_pct": 8.8, "allocated_amount": round(amount * 0.088)}
        ]
    return jsonify({"donation_amount": amount, "breakdown": breakdown})

@app.route("/api/gigs/<int:gig_id>/apply", methods=["POST"])
def api_apply_gig(gig_id):
    """Apply to a campus gig."""
    user = get_current_user()
    gig = db.query_db("SELECT id FROM gigs WHERE id = %s", (gig_id,), one=True)
    if not gig:
        return jsonify({"status": "error", "message": "Gig not found"}), 404

    existing = db.query_db(
        "SELECT id FROM gig_applications WHERE gig_id = %s AND applicant_id = %s",
        (gig_id, user['id']), one=True
    )
    if existing:
        return jsonify({"status": "already_applied"})

    db.execute_db("""
        UPDATE gigs SET applicants_count = applicants_count + 1 WHERE id = %s;
    """, (gig_id,))

    db.execute_db("""
        INSERT INTO gig_applications (gig_id, applicant_id)
        VALUES (%s, %s);
    """, (gig_id, user['id']))

    return jsonify({"status": "success"})

@app.route("/api/gigs/<int:gig_id>/delete", methods=["POST", "DELETE"])
def api_delete_gig(gig_id):
    """Delete a gig posted by the student or admin."""
    user = get_current_user()
    gig = db.query_db("SELECT * FROM gigs WHERE id = %s", (gig_id,), one=True)
    if not gig:
        return jsonify({"status": "error", "message": "Gig not found"}), 404
    
    # Check permissions: poster or admin
    if gig["poster_id"] != user["id"] and session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Permission denied. Only the poster or admin can delete this gig."}), 403

    db.execute_db("DELETE FROM gig_applications WHERE gig_id = %s", (gig_id,))
    db.execute_db("DELETE FROM gigs WHERE id = %s", (gig_id,))
    return jsonify({"status": "success", "message": "Gig deleted successfully."})

@app.route("/api/gigs/<int:gig_id>/complete", methods=["POST"])
def api_complete_gig(gig_id):
    """Mark a gig complete, assign rating (1-5), and dynamically increment tasker's Gig Score."""
    user = get_current_user()
    gig = db.query_db("SELECT * FROM gigs WHERE id = %s", (gig_id,), one=True)
    if not gig:
        return jsonify({"status": "error", "message": "Gig not found"}), 404

    data = request.get_json() or {}
    rating = float(data.get("rating", 5.0))
    review = data.get("review", "Delivered exceptional work on-time.")
    tasker_id = data.get("tasker_id")

    # If tasker_id not provided, pick the latest applicant or fallback to student
    if not tasker_id:
        applicant = db.query_db("SELECT applicant_id FROM gig_applications WHERE gig_id = %s ORDER BY id DESC LIMIT 1", (gig_id,), one=True)
        tasker_id = applicant["applicant_id"] if applicant else 2

    points_delta = 4 if rating >= 4.8 else (3 if rating >= 4.0 else 1)

    db.execute_db("UPDATE gigs SET status = 'completed' WHERE id = %s", (gig_id,))

    db.execute_db("""
        UPDATE users 
        SET gig_score = LEAST(100, gig_score + %s),
            gigs_completed = gigs_completed + 1,
            gig_rating = ROUND((COALESCE(gig_rating, 4.90) * 4 + %s) / 5.0, 2),
            gig_tier = CASE 
                WHEN gig_score + %s >= 95 THEN 'Top Rated Specialist'
                WHEN gig_score + %s >= 85 THEN 'Level 2 Tasker'
                ELSE 'Level 1 Tasker'
            END
        WHERE id = %s;
    """, (points_delta, rating, points_delta, points_delta, tasker_id))

    db.execute_db("""
        INSERT INTO gig_events (user_id, event_type, points_delta, description, client_name, rating)
        VALUES (%s, 'gig_completed', %s, %s, %s, %s);
    """, (tasker_id, points_delta, f"Completed gig '{gig['title'][:40]}': {review}", user['name'], rating))

    updated_tasker = db.query_db("SELECT gig_score, gig_tier, gig_rating FROM users WHERE id = %s", (tasker_id,), one=True)
    return jsonify({
        "status": "success",
        "message": "Gig marked completed and tasker Gig Score updated!",
        "new_gig_score": updated_tasker["gig_score"] if updated_tasker else 92,
        "new_tier": updated_tasker["gig_tier"] if updated_tasker else "Level 2 Tasker"
    })

@app.route("/api/meals/gift", methods=["POST"])
def api_gift_meal():
    """Gift anonymous meals to cafeteria pool."""
    user = get_current_user()
    data = request.get_json() or {}
    meals_count = int(data.get("meals_count", 1))
    amount = meals_count * 120

    code = f"UIU-MEAL-{random.randint(1000, 9999)}"

    db.execute_db("""
        INSERT INTO meal_drops (donor_id, donor_name, meals_count, amount, claim_code, status)
        VALUES (%s, %s, %s, %s, %s, 'available');
    """, (user['id'], user['name'], meals_count, amount, code))

    db.execute_db("""
        INSERT INTO trust_events (user_id, event_type, points_delta, description)
        VALUES (%s, 'meal_drop', 1, %s);
    """, (user['id'], f"Gifted {meals_count} anonymous cafeteria meal token(s)"))

    return jsonify({"status": "success", "claim_code": code, "meals_count": meals_count})

@app.route("/api/meals/claim", methods=["POST"])
def api_claim_meal():
    """Claim an anonymous meal token from the pool."""
    drop = db.query_db("""
        SELECT * FROM meal_drops 
        WHERE status = 'available' 
        ORDER BY id ASC 
        LIMIT 1;
    """, one=True)

    if drop:
        db.execute_db("""
            UPDATE meal_drops 
            SET status = 'claimed', claimed_at = CURRENT_TIMESTAMP 
            WHERE id = %s;
        """, (drop["id"],))
        claim_code = drop["claim_code"]
    else:
        claim_code = f"UIU-MEAL-{random.randint(1000, 9999)}"
        db.execute_db("""
            INSERT INTO meal_drops (donor_id, donor_name, meals_count, amount, claim_code, status, claimed_at)
            VALUES (1, 'UIU Aid Community Fund', 1, 120, %s, 'claimed', CURRENT_TIMESTAMP);
        """, (claim_code,))

    return jsonify({"status": "success", "claim_code": claim_code})

@app.route('/api/stats')
def api_stats():
    """Community stats for the dashboard."""
    total_loans = db.query_db("SELECT COALESCE(SUM(amount),0) as total FROM loans WHERE status IN ('active','repaid')", one=True)
    repaid = db.query_db("SELECT COUNT(*) as cnt FROM loans WHERE status='repaid'", one=True)
    total_cnt = db.query_db("SELECT COUNT(*) as cnt FROM loans WHERE status IN ('active','repaid')", one=True)
    students = db.query_db("SELECT COUNT(*) as cnt FROM users", one=True)
    rate = round(repaid['cnt'] / total_cnt['cnt'] * 100) if total_cnt['cnt'] > 0 else 94
    return jsonify({'facilitated': int(total_loans['total']), 'repayment_rate': rate, 'students': students['cnt']})

@app.route('/api/auction/<int:loan_id>/bids')
def api_get_bids(loan_id):
    """Fetch current bids for a loan (used by live auction AJAX refresh)."""
    bids = db.query_db("""
        SELECT b.*, u.name as lender_name, u.initials, u.avatar_class
        FROM loan_bids b
        JOIN users u ON b.lender_id = u.id
        WHERE b.loan_id = %s
        ORDER BY b.interest_rate ASC, b.created_at DESC
    """, (loan_id,))
    return jsonify([dict(b) for b in bids])


# -------------------------------------------------------------
# App Entrypoint
# -------------------------------------------------------------
if __name__ == "__main__":
    print("Ensuring database tables are initialized...")
    db.init_db()
    port = int(os.getenv("PORT", 5000))
    print(f"Starting UIU Aid Web Application on http://127.0.0.1:{port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
