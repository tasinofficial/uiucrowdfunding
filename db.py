import os
import threading
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_8oZcQdE2zyrH@ep-steep-bonus-aydbaplr-pooler.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

_pool = None
_pool_lock = threading.Lock()

def get_pool():
    """Returns a singleton ThreadedConnectionPool to reuse warm TLS sockets."""
    global _pool
    if _pool is None or _pool.closed:
        with _pool_lock:
            if _pool is None or _pool.closed:
                _pool = ThreadedConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dsn=DATABASE_URL,
                    cursor_factory=RealDictCursor
                )
    return _pool

def get_db_connection():
    """Fetches a warm connection from the pool and verifies liveness."""
    pool = get_pool()
    conn = pool.getconn()
    try:
        # Check if socket is still alive (reconnect if Neon dropped idle socket)
        if conn.closed != 0:
            pool.putconn(conn, close=True)
            conn = pool.getconn()
    except Exception:
        pass
    conn.autocommit = False
    return conn

def release_db_connection(conn, is_bad=False):
    """Returns connection to pool with rollback so next query gets a clean transaction."""
    if not conn:
        return
    try:
        pool = get_pool()
        if is_bad or conn.closed != 0:
            pool.putconn(conn, close=True)
        else:
            try:
                conn.rollback()
            except Exception:
                pass
            pool.putconn(conn)
    except Exception:
        try:
            conn.close()
        except Exception:
            pass

def query_db(query, args=(), one=False):
    """Fast query helper reusing warm pooled connection."""
    conn = None
    is_bad = False
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(query, args)
            rv = cur.fetchall()
            return (rv[0] if rv else None) if one else rv
    except psycopg2.OperationalError:
        # Auto-recover on dropped connection: close bad conn, grab fresh one, retry once
        is_bad = True
        release_db_connection(conn, is_bad=True)
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(query, args)
            rv = cur.fetchall()
            return (rv[0] if rv else None) if one else rv
    except Exception as e:
        is_bad = True
        raise e
    finally:
        release_db_connection(conn, is_bad=is_bad)

def execute_db(query, args=(), returning=False):
    """Fast execute helper for INSERT/UPDATE/DELETE reusing warm pooled connection."""
    conn = None
    is_bad = False
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(query, args)
            res = None
            if returning:
                res = cur.fetchone()
            conn.commit()
            return res
    except psycopg2.OperationalError:
        # Auto-recover on dropped connection: close bad conn, grab fresh one, retry once
        is_bad = True
        release_db_connection(conn, is_bad=True)
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(query, args)
            res = None
            if returning:
                res = cur.fetchone()
            conn.commit()
            return res
    except Exception as e:
        is_bad = True
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise e
    finally:
        release_db_connection(conn, is_bad=is_bad)

def init_db():
    """Creates tables in Neon PostgreSQL and seeds initial realistic demo data."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Users table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                initials VARCHAR(5),
                student_id VARCHAR(20) UNIQUE NOT NULL,
                department VARCHAR(50),
                trimester VARCHAR(20),
                trust_score INT DEFAULT 82,
                tier VARCHAR(20) DEFAULT 'Gold',
                borrowing_limit INT DEFAULT 5000,
                borrowed_amount INT DEFAULT 552,
                lent_amount INT DEFAULT 2400,
                is_verified BOOLEAN DEFAULT TRUE,
                avatar_class VARCHAR(10) DEFAULT 'av-1',
                gig_score INT DEFAULT 88,
                gig_rating NUMERIC(3,2) DEFAULT 4.90,
                gigs_completed INT DEFAULT 6,
                gigs_posted INT DEFAULT 2,
                gig_tier VARCHAR(50) DEFAULT 'Level 2 Tasker',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Ensure columns exist on already created tables
            cur.execute("""
                ALTER TABLE users ADD COLUMN IF NOT EXISTS gig_score INT DEFAULT 88;
                ALTER TABLE users ADD COLUMN IF NOT EXISTS gig_rating NUMERIC(3,2) DEFAULT 4.90;
                ALTER TABLE users ADD COLUMN IF NOT EXISTS gigs_completed INT DEFAULT 6;
                ALTER TABLE users ADD COLUMN IF NOT EXISTS gigs_posted INT DEFAULT 2;
                ALTER TABLE users ADD COLUMN IF NOT EXISTS gig_tier VARCHAR(50) DEFAULT 'Level 2 Tasker';
            """)

            # Gig Reputation Events
            cur.execute("""
            CREATE TABLE IF NOT EXISTS gig_events (
                id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id) ON DELETE CASCADE,
                event_type VARCHAR(50),
                points_delta INT,
                description VARCHAR(255),
                client_name VARCHAR(100),
                rating NUMERIC(3,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Crowdfunding Itemized Expenditures (Per-Donation Breakdown & Receipts)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS expenditures (
                id SERIAL PRIMARY KEY,
                campaign_id INT REFERENCES crowdfunding_campaigns(id) ON DELETE CASCADE,
                milestone_id INT,
                category VARCHAR(50) NOT NULL,
                vendor VARCHAR(100) NOT NULL,
                invoice_no VARCHAR(50),
                item_name VARCHAR(150) NOT NULL,
                quantity VARCHAR(30),
                amount INT NOT NULL,
                status VARCHAR(30) DEFAULT 'verified',
                verified_by VARCHAR(100) DEFAULT 'UIU Medical Centre Audit Committee',
                receipt_date VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Loans table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                id SERIAL PRIMARY KEY,
                borrower_id INT REFERENCES users(id),
                amount INT NOT NULL,
                purpose VARCHAR(255) NOT NULL,
                repay_by VARCHAR(50),
                max_interest_rate NUMERIC(4,2) DEFAULT 5.00,
                current_interest_rate NUMERIC(4,2) DEFAULT 3.20,
                winning_lender_id INT REFERENCES users(id),
                message TEXT,
                status VARCHAR(20) DEFAULT 'active',
                guarantor_1 VARCHAR(100),
                guarantor_2 VARCHAR(100),
                due_date VARCHAR(50) DEFAULT 'Aug 2, 2026',
                days_remaining INT DEFAULT 3,
                total_due INT DEFAULT 552,
                total_repaid INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Loan Bids table (for live reverse auction)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS loan_bids (
                id SERIAL PRIMARY KEY,
                loan_id INT REFERENCES loans(id) ON DELETE CASCADE,
                lender_id INT REFERENCES users(id),
                interest_rate NUMERIC(4,2) NOT NULL,
                notes VARCHAR(255),
                is_winning BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Repayments table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS repayments (
                id SERIAL PRIMARY KEY,
                loan_id INT REFERENCES loans(id),
                payer_id INT REFERENCES users(id),
                amount INT NOT NULL,
                payment_method VARCHAR(30) DEFAULT 'bKash',
                trx_id VARCHAR(50),
                status VARCHAR(20) DEFAULT 'completed',
                paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Crowdfunding campaigns table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS crowdfunding_campaigns (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                student_name VARCHAR(100) NOT NULL,
                student_dept VARCHAR(50),
                category VARCHAR(50),
                goal_amount INT NOT NULL,
                raised_amount INT DEFAULT 0,
                story TEXT,
                status VARCHAR(20) DEFAULT 'active',
                days_left INT DEFAULT 14,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Crowdfunding milestones / transparency receipts
            cur.execute("""
            CREATE TABLE IF NOT EXISTS milestones (
                id SERIAL PRIMARY KEY,
                campaign_id INT REFERENCES crowdfunding_campaigns(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                amount INT NOT NULL,
                status VARCHAR(30) DEFAULT 'verified',
                vendor VARCHAR(100),
                memo VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Donations table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS donations (
                id SERIAL PRIMARY KEY,
                campaign_id INT REFERENCES crowdfunding_campaigns(id) ON DELETE CASCADE,
                donor_name VARCHAR(100) DEFAULT 'Anonymous Peer',
                is_anonymous BOOLEAN DEFAULT FALSE,
                amount INT NOT NULL,
                payment_method VARCHAR(30) DEFAULT 'bKash',
                trx_id VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Campus Gigs table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS gigs (
                id SERIAL PRIMARY KEY,
                poster_id INT REFERENCES users(id),
                title VARCHAR(255) NOT NULL,
                category VARCHAR(50) NOT NULL,
                budget INT NOT NULL,
                due_info VARCHAR(50),
                applicants_count INT DEFAULT 0,
                status VARCHAR(20) DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Gig Applications
            cur.execute("""
            CREATE TABLE IF NOT EXISTS gig_applications (
                id SERIAL PRIMARY KEY,
                gig_id INT REFERENCES gigs(id) ON DELETE CASCADE,
                applicant_id INT REFERENCES users(id),
                status VARCHAR(20) DEFAULT 'submitted',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Anonymous Meal Drops
            cur.execute("""
            CREATE TABLE IF NOT EXISTS meal_drops (
                id SERIAL PRIMARY KEY,
                donor_id INT REFERENCES users(id),
                donor_name VARCHAR(100) DEFAULT 'Anonymous Classmate',
                meals_count INT DEFAULT 1,
                amount INT DEFAULT 120,
                claim_code VARCHAR(20) UNIQUE,
                status VARCHAR(20) DEFAULT 'available',
                claimed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Trust Reputation Events
            cur.execute("""
            CREATE TABLE IF NOT EXISTS trust_events (
                id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id),
                event_type VARCHAR(50),
                points_delta INT,
                description VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Check if seed data exists
            cur.execute("SELECT COUNT(*) AS count FROM users;")
            user_count = cur.fetchone()["count"]

            if user_count == 0:
                print("Seeding initial demo data into Neon PostgreSQL...")
                # 1. Seed users
                cur.execute("""
                INSERT INTO users (name, initials, student_id, department, trimester, trust_score, tier, borrowing_limit, borrowed_amount, lent_amount, is_verified, avatar_class)
                VALUES 
                ('Nusrat Jahan', 'NJ', '011211045', 'BBA', '9th trimester', 82, 'Gold', 5000, 552, 2400, TRUE, 'av-1'),
                ('Tanvir Hasan', 'TH', '011202088', 'CSE', '8th trimester', 74, 'Silver', 3000, 0, 1500, TRUE, 'av-2'),
                ('Karim Hossain', 'KH', '011193012', 'EEE', '11th trimester', 91, 'Platinum', 8000, 0, 5000, TRUE, 'av-3'),
                ('Adnan Chowdhury', 'AC', '011221199', 'CSE', '5th trimester', 85, 'Gold', 5000, 0, 1200, TRUE, 'av-4'),
                ('Mim Akter', 'MA', '011213054', 'Media Studies', '7th trimester', 91, 'Gold', 6000, 0, 3000, TRUE, 'av-6');
                """)

                # 2. Seed active loan for Nusrat from Karim
                cur.execute("""
                INSERT INTO loans (borrower_id, amount, purpose, repay_by, max_interest_rate, current_interest_rate, winning_lender_id, message, status, guarantor_1, guarantor_2, due_date, days_remaining, total_due, total_repaid)
                VALUES 
                (1, 500, 'Course registration fee top-up', 'Aug 2, 2026', 5.00, 3.20, 3, 'Needed small emergency bridge for lab course registration. Tutor every weekend.', 'active', 'Tanvir Hasan', 'Mim Akter', 'Aug 2, 2026', 3, 552, 0),
                (2, 3000, 'Laptop repair before finals', 'Sep 5, 2026', 5.00, 3.50, NULL, 'My laptop died right before finals. I tutor on weekends and will repay promptly.', 'auction', 'Nusrat Jahan', 'Karim Hossain', 'Sep 5, 2026', 12, 3105, 0);
                """)

                # 3. Seed loan bids for auction loan (loan_id 2)
                cur.execute("""
                INSERT INTO loan_bids (loan_id, lender_id, interest_rate, notes, is_winning)
                VALUES 
                (2, 3, 4.50, 'Can disburse via bKash right away.', FALSE),
                (2, 4, 3.80, 'Full 3000 Tk available in cash on campus.', FALSE),
                (2, 1, 3.50, 'Current best bid! Disburse via Nagad or bKash.', TRUE);
                """)

                # 4. Seed crowdfunding campaign
                cur.execute("""
                INSERT INTO crowdfunding_campaigns (title, student_name, student_dept, category, goal_amount, raised_amount, story, status, days_left)
                VALUES 
                ('Emergency Surgery Recovery for Fahim', 'Fahim Ahmed', 'BSc in CSE, 6th Trimester', 'Medical Emergency', 45000, 38400, 'Fahim suffered a sudden acute appendicitis during midterms and required emergency surgery at Evercare Hospital. 100% transparent milestone verification with hospital receipts attached.', 'active', 6);
                """)

                # 5. Seed milestones for campaign
                cur.execute("""
                INSERT INTO milestones (campaign_id, title, amount, status, vendor, memo)
                VALUES 
                (1, 'Hospital Admission & Diagnostic Tests', 15000, 'verified', 'Evercare Hospital Dhaka', 'Verified by UIU Medical Centre — Receipt #EC-99412'),
                (1, 'Surgical Procedure & Anesthesia', 20000, 'verified', 'Evercare Operation Theater', 'Disbursed directly to hospital billing counter'),
                (1, 'Post-Op Medications & Follow-up Care', 10000, 'pending', 'Lazz Pharma UIU Campus Gate', 'Awaiting final pharmacist invoice');
                """)

                # 6. Seed donations
                cur.execute("""
                INSERT INTO donations (campaign_id, donor_name, is_anonymous, amount, payment_method, trx_id)
                VALUES 
                (1, 'Nusrat Jahan', FALSE, 1500, 'bKash', 'BKH8821948291'),
                (1, 'Tanvir Hasan', FALSE, 1000, 'Nagad', 'NGD7721839211'),
                (1, 'Anonymous CSE Peer', TRUE, 5000, 'bKash', 'BKH3321948332'),
                (1, 'UIU Robotics Club Members', FALSE, 6500, 'bKash', 'BKH5512948119');
                """)

                # 7. Seed campus gigs
                cur.execute("""
                INSERT INTO gigs (poster_id, title, category, budget, due_info, applicants_count, status)
                VALUES 
                (4, 'Debug my Python data-structures assignment', 'Tech & Code', 800, 'due in 2 days', 4, 'open'),
                (5, 'Poster design for Robotics Club fest', 'Design', 600, 'due Jul 30', 2, 'open'),
                (3, 'Tutoring: Linear Algebra & Matrix Calc', 'Tutoring', 1200, 'due in 5 days', 3, 'open'),
                (2, 'Transcribe audio lecture notes (Bangla + English)', 'Notes & Writing', 500, 'due Aug 3', 1, 'open'),
                (1, 'Campus book delivery & library errand', 'Errands', 350, 'due tomorrow', 5, 'open');
                """)

                # 8. Seed anonymous meal drops
                cur.execute("""
                INSERT INTO meal_drops (donor_id, donor_name, meals_count, amount, claim_code, status, created_at)
                VALUES 
                (1, 'Anonymous Classmate', 1, 120, 'UIU-MEAL-8821', 'available', CURRENT_TIMESTAMP - INTERVAL '1 hour'),
                (3, 'Anonymous Senior', 2, 240, 'UIU-MEAL-9412', 'available', CURRENT_TIMESTAMP - INTERVAL '3 hours'),
                (5, 'Anonymous Classmate', 1, 120, 'UIU-MEAL-5510', 'claimed', CURRENT_TIMESTAMP - INTERVAL '12 minutes');
                """)

                # 9. Seed trust events
                cur.execute("""
                INSERT INTO trust_events (user_id, event_type, points_delta, description)
                VALUES 
                (1, 'loan_repaid', 2, 'Repaid 400 Tk on time to Tanvir H.'),
                (1, 'vouch_received', 3, 'Vouched by senior Karim H. (Platinum Tier)'),
                (1, 'gig_completed', 2, 'Completed Python assignment debugging gig'),
                (1, 'meal_drop', 1, 'Gifted an anonymous cafeteria meal token');
                """)

                print("Demo data seeded successfully!")

            # Ensure users have rich, diverse gig stats
            cur.execute("""
                UPDATE users SET gig_score = 94, gig_rating = 4.95, gigs_completed = 8, gigs_posted = 1, gig_tier = 'Elite Campus Freelancer' WHERE id = 1 AND (gig_score IS NULL OR gig_score = 88);
                UPDATE users SET gig_score = 78, gig_rating = 4.60, gigs_completed = 3, gigs_posted = 2, gig_tier = 'Rising Tasker' WHERE id = 2 AND (gig_score IS NULL OR gig_score = 88);
                UPDATE users SET gig_score = 96, gig_rating = 5.00, gigs_completed = 14, gigs_posted = 1, gig_tier = 'Master Tasker' WHERE id = 3 AND (gig_score IS NULL OR gig_score = 88);
                UPDATE users SET gig_score = 85, gig_rating = 4.80, gigs_completed = 5, gigs_posted = 3, gig_tier = 'Level 2 Tasker' WHERE id = 4 AND (gig_score IS NULL OR gig_score = 88);
                UPDATE users SET gig_score = 91, gig_rating = 4.90, gigs_completed = 7, gigs_posted = 1, gig_tier = 'Level 2 Tasker' WHERE id = 5 AND (gig_score IS NULL OR gig_score = 88);
            """)

            # Seed gig events if empty
            cur.execute("SELECT COUNT(*) AS count FROM gig_events;")
            gig_events_count = cur.fetchone()["count"]
            if gig_events_count == 0:
                print("Seeding initial gig score events...")
                cur.execute("""
                INSERT INTO gig_events (user_id, event_type, points_delta, description, client_name, rating)
                VALUES
                (1, 'task_completed', 4, 'Completed Python data-structures debugging ahead of deadline', 'Adnan Chowdhury', 5.00),
                (1, 'task_completed', 3, 'Delivered Calculus tutoring crash review', 'Karim Hossain', 4.90),
                (1, 'task_completed', 4, 'Designed UI wireframe for CSE project showcase', 'Tanvir Hasan', 5.00),
                (1, 'ontime_streak', 2, 'Maintained 5-task consecutive on-time delivery streak', 'System Automated', NULL),
                (1, 'review_received', 3, 'Received 5.0 rating: "Super clear explanation, saved my midterms!"', 'Priya Das', 5.00);
                """)

            # Seed expenditures if empty
            cur.execute("SELECT COUNT(*) AS count FROM expenditures;")
            exp_count = cur.fetchone()["count"]
            if exp_count == 0:
                print("Seeding initial crowdfunding itemized expenditures...")
                cur.execute("""
                INSERT INTO expenditures (campaign_id, milestone_id, category, vendor, invoice_no, item_name, quantity, amount, status, verified_by, receipt_date)
                VALUES
                (1, 1, 'Hospital & Room Charges', 'Evercare Hospital Dhaka', 'INV-EC-99412', 'Emergency Room admission & bed charges (3 nights)', '3 days', 8500, 'verified', 'UIU Medical Centre (Dr. Shamsul Alam)', 'Jul 18, 2026'),
                (1, 1, 'Diagnostics & Imaging', 'Evercare Hospital Dhaka', 'INV-EC-99413', 'Ultrasonography & Whole Abdomen CT Scan', '2 scans', 6500, 'verified', 'UIU Medical Centre (Dr. Shamsul Alam)', 'Jul 18, 2026'),
                (1, 2, 'Surgery & Operating Theater', 'Evercare Hospital Dhaka', 'INV-EC-99450', 'Laparoscopic Appendectomy OT Charges & Surgical Kit', '1 procedure', 14500, 'verified', 'UIU Medical Centre (Dr. Shamsul Alam)', 'Jul 19, 2026'),
                (1, 2, 'Anesthesia & Surgeon Team', 'Evercare Hospital Dhaka', 'INV-EC-99451', 'Senior Surgeon & Chief Anesthesiologist fee', '1 procedure', 5500, 'verified', 'UIU Medical Centre (Dr. Shamsul Alam)', 'Jul 19, 2026'),
                (1, 3, 'Post-Op Pharmacy', 'Lazz Pharma (UIU Campus Gate)', 'LZ-UIU-4019', 'IV Antibiotics (Meropenem), Analgesics, Infusions', 'Batch of 12', 3400, 'verified', 'UIU Medical Centre (Dr. Shamsul Alam)', 'Jul 20, 2026');
                """)

            conn.commit()
            print("Database initialized successfully in Neon PostgreSQL.")
    except Exception as e:
        conn.rollback()
        print(f"Error initializing database: {e}")
        raise e
    finally:
        release_db_connection(conn)

if __name__ == "__main__":
    init_db()
