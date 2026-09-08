import os
import random
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv
import db

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
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
    total_loans = db.query_db("SELECT COALESCE(SUM(amount), 0) as total FROM loans WHERE status IN ('active','repaid')", one=True)
    available_meals = db.query_db("SELECT count(*) as count FROM meal_drops WHERE status = 'available'", one=True)["count"]
    
    return render_template(
        'admin.html',
        users=users,
        loans=loans,
        milestones=milestones,
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
    """Screen 5: Crowdfunding & Transparency"""
    campaign_id = request.args.get("id", 1)
    campaign = db.query_db("SELECT * FROM crowdfunding_campaigns WHERE id = %s", (campaign_id,), one=True)
    if not campaign:
        campaign = db.query_db("SELECT * FROM crowdfunding_campaigns ORDER BY id ASC", one=True)
    
    camp_id = campaign["id"] if campaign else 1
    milestones = db.query_db("SELECT * FROM milestones WHERE campaign_id = %s ORDER BY id ASC", (camp_id,))
    donations = db.query_db("SELECT * FROM donations WHERE campaign_id = %s ORDER BY created_at DESC", (camp_id,))
    user = get_current_user()
    return render_template("crowdfunding.html", active_page="crowdfunding", campaign=campaign, milestones=milestones, donations=donations, user=user)

@app.route("/gigs")
def gig_board():
    """Screen 6: Campus Gig Board"""
    gigs = db.query_db("""
        SELECT g.*, u.name as poster_name, u.initials, u.avatar_class, u.trust_score
        FROM gigs g
        JOIN users u ON g.poster_id = u.id
        ORDER BY g.id DESC
    """)
    user = get_current_user()
    return render_template("gig_board.html", active_page="gigs", gigs=gigs, user=user)

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
        (%s, 7, 4.0, 'Available via bKash or cafeteria handover');
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

    new_gig = db.query_db("SELECT g.*, u.name as poster_name, u.initials, u.avatar_class, u.trust_score FROM gigs g JOIN users u ON g.poster_id = u.id WHERE g.id = %s", (result['id'],), one=True)
    return jsonify({"status": "success", "gig_id": result['id'], "gig": dict(new_gig) if new_gig else {}})

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
