import random
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_8oZcQdE2zyrH@ep-steep-bonus-aydbaplr-pooler.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

def populate():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cur = conn.cursor()

    print("Populating comprehensive realistic data for UIU Aid...")

    # 1. Expand Users
    users_data = [
        ('Nusrat Jahan', 'NJ', '011211045', 'BBA', '9th trimester', 86, 'Gold', 5000, 552, 2400, True, 'av-1'),
        ('Tanvir Hasan', 'TH', '011202088', 'CSE', '8th trimester', 74, 'Silver', 3000, 0, 1500, True, 'av-2'),
        ('Karim Hossain', 'KH', '011193012', 'EEE', '11th trimester', 94, 'Platinum', 8000, 0, 6800, True, 'av-3'),
        ('Adnan Chowdhury', 'AC', '011221199', 'CSE', '5th trimester', 85, 'Gold', 5000, 0, 1200, True, 'av-4'),
        ('Mim Akter', 'MA', '011213054', 'Media Studies', '7th trimester', 91, 'Gold', 6000, 0, 3000, True, 'av-6'),
        ('Fahim Al Farabi', 'FF', '011212001', 'CSE', '7th trimester', 78, 'Silver', 3500, 0, 800, True, 'av-5'),
        ('Sadia Rahman', 'SR', '011201044', 'Pharmacy', '10th trimester', 92, 'Platinum', 7500, 0, 4200, True, 'av-1'),
        ('Mahmudul Hasan', 'MH', '011223019', 'Civil Eng.', '4th trimester', 62, 'Bronze', 2000, 0, 500, True, 'av-2'),
        ('Tasnia Shahrin', 'TS', '011211112', 'BBA', '8th trimester', 88, 'Gold', 5000, 0, 2100, True, 'av-4'),
        ('Rakibul Islam', 'RI', '011203099', 'CSE', '9th trimester', 81, 'Gold', 4500, 0, 1900, True, 'av-3'),
        ('Jannatul Ferdous', 'JF', '011221088', 'Data Science', '5th trimester', 70, 'Silver', 2500, 0, 600, True, 'av-6'),
        ('Siam Ahmed', 'SA', '011192055', 'EEE', '12th trimester', 96, 'Platinum', 8500, 0, 7500, True, 'av-5'),
        ('Zarin Tasnim', 'ZT', '011213007', 'English', '6th trimester', 84, 'Gold', 4000, 0, 1500, True, 'av-2'),
        ('Ashikur Rahman', 'AR', '011222041', 'CSE', '4th trimester', 66, 'Bronze', 2000, 0, 400, True, 'av-1'),
        ('Nabila Haque', 'NH', '011202155', 'Economics', '9th trimester', 89, 'Gold', 5500, 0, 2800, True, 'av-4')
    ]

    for u in users_data:
        cur.execute("""
            INSERT INTO users (name, initials, student_id, department, trimester, trust_score, tier, borrowing_limit, borrowed_amount, lent_amount, is_verified, avatar_class)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (student_id) DO UPDATE SET
                trust_score = EXCLUDED.trust_score,
                tier = EXCLUDED.tier,
                borrowing_limit = EXCLUDED.borrowing_limit,
                is_verified = EXCLUDED.is_verified;
        """, u)

    # 2. Get user ids
    cur.execute("SELECT id, name, student_id FROM users")
    user_map = {row['name']: row['id'] for row in cur.fetchall()}

    # 3. Add Realistic Loans (active, auction, repaid)
    loans_data = [
        # (borrower_id, amount, purpose, repay_by, max_rate, cur_rate, winning_lender_id, message, status, g1, g2, due_date, days_remaining, total_due, total_repaid)
        (user_map.get('Nusrat Jahan', 1), 1500, 'Midterm exam fee clearance & book purchase', 'Aug 9, 2026', 5.0, 3.2, user_map.get('Karim Hossain', 3), 'Lab equipment fee bridge before stipend arrival.', 'active', 'Tanvir Hasan', 'Mim Akter', 'Aug 9, 2026', 4, 1550, 500),
        (user_map.get('Tanvir Hasan', 2), 3000, 'Laptop repair before finals', 'Sep 5, 2026', 5.0, 3.4, None, 'Display replaced. Peer tutoring income guaranteed for prompt repayment.', 'auction', 'Nusrat Jahan', 'Karim Hossain', 'Sep 5, 2026', 10, 3102, 0),
        (user_map.get('Fahim Al Farabi', 6), 2500, 'Emergency medical prescriptions & doctor visit', 'Sep 12, 2026', 4.5, 3.0, None, 'Fell sick during exam week. Need quick medicine funds.', 'auction', 'Sadia Rahman', 'Adnan Chowdhury', 'Sep 12, 2026', 14, 2575, 0),
        (user_map.get('Mahmudul Hasan', 8), 1200, 'Drafting kit and lab supplies for survey course', 'Sep 18, 2026', 5.0, 4.0, None, 'Civil engineering project drafting tools and printing.', 'auction', 'Rakibul Islam', 'Siam Ahmed', 'Sep 18, 2026', 16, 1248, 0),
        (user_map.get('Jannatul Ferdous', 11), 4000, 'Cloud compute credits for ML capstone project', 'Sep 22, 2026', 4.0, 3.1, None, 'Training transformer models for research paper submission.', 'auction', 'Tanvir Hasan', 'Karim Hossain', 'Sep 22, 2026', 18, 4124, 0),
        (user_map.get('Ashikur Rahman', 14), 1800, 'Hostel mess bill monthly due', 'Aug 25, 2026', 5.0, 3.5, user_map.get('Sadia Rahman', 7), 'Hostel deadline before late penalty strikes.', 'active', 'Fahim Al Farabi', 'Nabila Haque', 'Aug 25, 2026', 8, 1863, 1863),
        (user_map.get('Adnan Chowdhury', 4), 2000, 'IEEE Student branch conference registration', 'Jul 28, 2026', 4.0, 3.0, user_map.get('Siam Ahmed', 12), 'Attending IEEE AI symposium at BUET.', 'repaid', 'Nusrat Jahan', 'Karim Hossain', 'Jul 28, 2026', 0, 2060, 2060),
        (user_map.get('Mim Akter', 5), 3500, 'Documentary production camera lens rental', 'Jul 15, 2026', 5.0, 3.8, user_map.get('Karim Hossain', 3), 'Media studies short film grading submission.', 'repaid', 'Tasnia Shahrin', 'Sadia Rahman', 'Jul 15, 2026', 0, 3633, 3633)
    ]

    for l in loans_data:
        cur.execute("""
            INSERT INTO loans (borrower_id, amount, purpose, repay_by, max_interest_rate, current_interest_rate, winning_lender_id, message, status, guarantor_1, guarantor_2, due_date, days_remaining, total_due, total_repaid)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, l)

    # 4. Loan Bids for auction loans
    cur.execute("SELECT id, max_interest_rate FROM loans WHERE status = 'auction'")
    auction_loans = cur.fetchall()

    bid_pool = [
        (user_map.get('Karim Hossain', 3), 3.4, 'Instant bKash disbursement ready.'),
        (user_map.get('Sadia Rahman', 7), 3.6, 'Available via Nagad or cafeteria handover.'),
        (user_map.get('Siam Ahmed', 12), 3.2, 'Happy to support fellow batchmate!'),
        (user_map.get('Nabila Haque', 15), 3.8, 'Standard peer rate, immediate transfer.'),
        (user_map.get('Tasnia Shahrin', 9), 3.0, 'Can disburse within 15 mins.')
    ]

    for al in auction_loans:
        loan_id = al['id']
        selected_bids = random.sample(bid_pool, 3)
        for sb in selected_bids:
            cur.execute("""
                INSERT INTO loan_bids (loan_id, lender_id, interest_rate, notes, is_winning)
                VALUES (%s, %s, %s, %s, FALSE)
            """, (loan_id, sb[0], sb[1], sb[2]))

    # 5. Expand Gigs
    gigs_data = [
        (user_map.get('Karim Hossain', 3), 'Debug Django REST API & Celery Task Queue', 'Tech & Code', 1200, 'due in 2 days', 3, 'open'),
        (user_map.get('Sadia Rahman', 7), 'Club Fest Promotional Banner & Poster Pack', 'Design', 800, 'due in 3 days', 5, 'open'),
        (user_map.get('Tanvir Hasan', 2), 'Tutoring Discrete Mathematics (Graph Theory)', 'Tutoring', 600, 'due in 1 day', 2, 'open'),
        (user_map.get('Tasnia Shahrin', 9), 'Proofread & Format 25-page Research Monograph', 'Notes & Writing', 750, 'due in 4 days', 1, 'open'),
        (user_map.get('Mim Akter', 5), 'Campus Event Photography & Light Editing', 'Design', 1500, 'due in 5 days', 4, 'open'),
        (user_map.get('Fahim Al Farabi', 6), 'Data Science Pandas & NumPy Cleaning Script', 'Tech & Code', 900, 'due in 2 days', 2, 'open'),
        (user_map.get('Nabila Haque', 15), 'Microeconomics Assignment Problem Set Help', 'Tutoring', 500, 'due in 3 days', 3, 'open'),
        (user_map.get('Siam Ahmed', 12), 'Pick up 3D printed model from Dhanmondi Lab', 'Errands', 400, 'due in 1 day', 4, 'open'),
        (user_map.get('Adnan Chowdhury', 4), 'Build responsive HTML/CSS Landing Page', 'Tech & Code', 1800, 'due in 4 days', 6, 'open'),
        (user_map.get('Rakibul Islam', 10), 'C++ Object Oriented Programming Practice Prep', 'Tutoring', 700, 'due in 2 days', 1, 'open')
    ]

    for g in gigs_data:
        cur.execute("""
            INSERT INTO gigs (poster_id, title, category, budget, due_info, applicants_count, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, g)

    # 6. Expand Crowdfunding Campaigns & Milestones & Donations
    cur.execute("SELECT count(*) as c FROM crowdfunding_campaigns")
    if cur.fetchone()['c'] <= 1:
        campaigns_data = [
            ('UIU Solar Rover Team — Formula Green International Challenge', 'Ashikur Rahman', 'EEE & CSE Dept', 'Student Project', 85000, 48200, 
             'Our multidisciplinary student team qualified for the prestigious Formula Green Engineering Competition! We are designing and manufacturing an ultra-efficient lightweight solar vehicle on campus.\n\nAll funds go directly toward solar MPPT cells, brushless DC hub motors, and certified safety roll cages with full itemized invoice transparency.', 'active', 21),
            ('Medical Recovery Support for Senior Lab Assistant M. Rafiq', 'UIU Student Welfare Club', 'Community Care', 'Emergency Relief', 45000, 39500,
             'Mr. M. Rafiq has served UIU engineering labs diligently for 9 years. He was recently hospitalized for emergency surgery. We are mobilizing campus support to cover hospital bills and essential post-operative treatment.', 'active', 8),
            ('Flood Relief Package Distribution — Feni & Noakhali Campuses', 'UIU Social Services Club', 'Disaster Relief', 'Community Care', 120000, 114500,
             'Emergency food rations, clean drinking water filtration kits, and urgent medical supplies dispatched by volunteer student caravans to remote submerged areas.', 'active', 4)
        ]

        for c in campaigns_data:
            cur.execute("""
                INSERT INTO crowdfunding_campaigns (title, student_name, student_dept, category, goal_amount, raised_amount, story, status, days_left)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, c)
            camp_id = cur.fetchone()['id']

            # Add milestones
            cur.execute("""
                INSERT INTO milestones (campaign_id, title, amount, status, vendor, memo)
                VALUES 
                (%s, 'Phase 1: Emergency Supplies & Procurement', 25000, 'verified', 'Direct Wholesale Supplies', 'Itemized receipt verified by Admin.'),
                (%s, 'Phase 2: Logistics & Transportation Caravan', 15000, 'verified', 'Campus Transport Division', 'Fuel & dispatch slips audited.'),
                (%s, 'Phase 3: Community Field Delivery', 30000, 'pending', 'Field NGO Partner', 'Pending post-delivery receipt verification.');
            """, (camp_id, camp_id, camp_id))

            # Add donations
            donors = [
                ('Tanvir Hasan', False, 2000, 'bKash', 'BKH98124012'),
                ('Anonymous Peer', True, 1000, 'Nagad', 'NGD77123991'),
                ('Prof. Dr. M. Rezwan', False, 5000, 'bKash', 'BKH55192004'),
                ('Sadia Rahman', False, 1500, 'bKash', 'BKH33291084'),
                ('Anonymous Alumnus', True, 4000, 'Nagad', 'NGD88201944')
            ]
            for d in donors:
                cur.execute("""
                    INSERT INTO donations (campaign_id, donor_name, is_anonymous, amount, payment_method, trx_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (camp_id, d[0], d[1], d[2], d[3], d[4]))

    # 7. Add Meal Drops
    meals = [
        (user_map.get('Karim Hossain', 3), 'Karim Hossain', 2, 240, 'UIU-MEAL-8419', 'available'),
        (user_map.get('Sadia Rahman', 7), 'Sadia Rahman', 3, 360, 'UIU-MEAL-9124', 'available'),
        (user_map.get('Siam Ahmed', 12), 'Anonymous Classmate', 1, 120, 'UIU-MEAL-6231', 'available'),
        (user_map.get('Tasnia Shahrin', 9), 'Tasnia Shahrin', 2, 240, 'UIU-MEAL-4190', 'available'),
        (user_map.get('Nusrat Jahan', 1), 'Nusrat Jahan', 1, 120, 'UIU-MEAL-3812', 'claimed'),
        (user_map.get('Tanvir Hasan', 2), 'Anonymous Classmate', 2, 240, 'UIU-MEAL-2189', 'claimed')
    ]
    for m in meals:
        cur.execute("""
            INSERT INTO meal_drops (donor_id, donor_name, meals_count, amount, claim_code, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (claim_code) DO NOTHING;
        """, m)

    # 8. Add Trust Events
    trust_events_data = [
        (1, 'loan_repaid', 2, 'On-time repayment of 552 Tk via bKash'),
        (1, 'vouch_received', 3, 'Endorsed by Peer Guarantor Tanvir Hasan (CSE)'),
        (1, 'gig_completed', 4, 'Successfully completed campus gig: Python Debugging'),
        (1, 'meal_drop', 1, 'Gifted 1 anonymous lunch meal to cafeteria pool'),
        (1, 'vouch_received', 3, 'Endorsed by Peer Guarantor Mim Akter (Media Studies)'),
        (2, 'loan_repaid', 3, 'Repaid laptop repair loan in full on schedule'),
        (3, 'lender_praise', 5, 'Disbursed 5 peer emergency loans with 100% community satisfaction')
    ]
    for te in trust_events_data:
        cur.execute("""
            INSERT INTO trust_events (user_id, event_type, points_delta, description)
            VALUES (%s, %s, %s, %s)
        """, te)

    conn.commit()
    conn.close()
    print("Database successfully populated with rich, realistic campus data!")

if __name__ == '__main__':
    populate()
