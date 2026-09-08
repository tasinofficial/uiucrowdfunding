import os
import re

os.makedirs("templates", exist_ok=True)

def update_nav(content, active_name):
    """Replaces sidebar nav items with proper Flask url paths and active state."""
    nav_pattern = r'<nav class="nav">.*?</nav>'
    replacement = f"""<nav class="nav">
      <a class="nav-item {'active' if active_name == 'dashboard' else ''}" href="/"><span class="ms">space_dashboard</span>Dashboard</a>
      <a class="nav-item {'active' if active_name in ['loans', 'auction', 'repayment'] else ''}" href="/loan-request"><span class="ms">handshake</span>Loans</a>
      <a class="nav-item {'active' if active_name == 'crowdfunding' else ''}" href="/crowdfunding"><span class="ms">volunteer_activism</span>Crowdfunding</a>
      <a class="nav-item {'active' if active_name == 'gigs' else ''}" href="/gigs"><span class="ms">work</span>Gig Board</a>
      <a class="nav-item {'active' if active_name == 'meals' else ''}" href="/meal-drops"><span class="ms">restaurant</span>Meal Drops</a>
      <a class="nav-item {'active' if active_name == 'trust' else ''}" href="/trust-profile"><span class="ms">verified_user</span>Trust Profile</a>
    </nav>"""
    return re.sub(nav_pattern, replacement, content, flags=re.DOTALL)

def add_loan_subnav(content, active_subpage):
    """Adds tabs for loan subpages."""
    subnav = f"""
    <!-- Loan Section Sub-Navigation Tabs -->
    <div class="tabs" style="margin-bottom: 24px; background: #fff; border-radius: 8px; border: 1px solid var(--border); padding: 4px 12px; box-shadow: var(--shadow);">
      <a href="/loan-request" class="tab {'on' if active_subpage == 'loans' else ''}" style="text-decoration:none;"><span class="ms ms-18">add_circle</span>1. Request a Loan</a>
      <a href="/auction" class="tab {'on' if active_subpage == 'auction' else ''}" style="text-decoration:none;"><span class="ms ms-18">gavel</span>2. Live Reverse Auction</a>
      <a href="/repayment" class="tab {'on' if active_subpage == 'repayment' else ''}" style="text-decoration:none;"><span class="ms ms-18">payments</span>3. Active Loan Repayment</a>
    </div>
    """
    # Insert right after <div class="page-head">...</div>
    match = re.search(r'(</div>\s*<!-- Page header -->|</div>\s*<!-- PAGE HEADER -->|</div>\s*<!-- Main two-column layout -->)', content)
    # Better: find the end of the first .page-head
    page_head_match = re.search(r'(<div class="page-head">.*?</div>\s*</div>)', content, flags=re.DOTALL)
    if page_head_match:
        return content[:page_head_match.end()] + subnav + content[page_head_match.end():]
    return content

print("Helper defined.")
