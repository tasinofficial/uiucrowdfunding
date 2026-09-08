import os
import re

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

os.makedirs("templates", exist_ok=True)

# Shared navbar replacement
def replace_sidebar(html, active_key):
    pattern = r'<nav class="nav">.*?</nav>'
    replacement = f"""<nav class="nav">
      <a class="nav-item {'active' if active_key == 'dashboard' else ''}" href="/"><span class="ms">space_dashboard</span>Dashboard</a>
      <a class="nav-item {'active' if active_key in ['loans', 'auction', 'repayment'] else ''}" href="/loan-request"><span class="ms">handshake</span>Loans</a>
      <a class="nav-item {'active' if active_key == 'crowdfunding' else ''}" href="/crowdfunding"><span class="ms">volunteer_activism</span>Crowdfunding</a>
      <a class="nav-item {'active' if active_key == 'gigs' else ''}" href="/gigs"><span class="ms">work</span>Gig Board</a>
      <a class="nav-item {'active' if active_key == 'meals' else ''}" href="/meal-drops"><span class="ms">restaurant</span>Meal Drops</a>
      <a class="nav-item {'active' if active_key == 'trust' else ''}" href="/trust-profile"><span class="ms">verified_user</span>Trust Profile</a>
    </nav>"""
    return re.sub(pattern, replacement, html, flags=re.DOTALL)

def inject_head_and_scripts(html, extra_head="", extra_script=""):
    # Inject extra styles before </head>
    if extra_head:
        html = html.replace("</head>", f"{extra_head}\n</head>")
    
    # Inject main.js and extra scripts before </body>
    script_block = f"""
<script src="/static/js/main.js"></script>
{extra_script}
</body>
"""
    html = re.sub(r'</body>', script_block, html, count=1)
    return html

# -------------------------------------------------------------
# 1. Dashboard
# -------------------------------------------------------------
print("Building templates/dashboard.html...")
t1 = read_file("uiu-aid-1-student-dashboard.html")
t1 = replace_sidebar(t1, "dashboard")

# Make banner link to /repayment
t1 = t1.replace('href="#" class="pay-link"', 'href="/repayment" class="pay-link"')

# Make quick actions link to real pages
t1 = t1.replace('<a href="#" class="btn btn-primary btn-block">\n            <span class="ms ms-18">handshake</span>\n            Request a Loan\n          </a>',
                '<a href="/loan-request" class="btn btn-primary btn-block">\n            <span class="ms ms-18">handshake</span>\n            Request a Loan\n          </a>')

t1 = t1.replace('<a href="#" class="btn btn-secondary btn-block">\n              <span class="ms ms-18">sos</span>\n              Report an Emergency\n            </a>',
                '<a href="/crowdfunding" class="btn btn-secondary btn-block">\n              <span class="ms ms-18">sos</span>\n              Emergency Crowdfunding\n            </a>')

t1 = t1.replace('<a href="#" class="btn btn-secondary btn-block">\n              <span class="ms ms-18">work</span>\n              Post a Gig\n            </a>',
                '<a href="/gigs" class="btn btn-secondary btn-block">\n              <span class="ms ms-18">work</span>\n              Campus Gig Board\n            </a>')

t1 = t1.replace('<a href="#" class="btn btn-secondary btn-block">\n              <span class="ms ms-18">restaurant</span>\n              Claim a Meal\n            </a>',
                '<a href="/meal-drops" class="btn btn-secondary btn-block">\n              <span class="ms ms-18">restaurant</span>\n              Anonymous Meal Drops\n            </a>')

t1 = t1.replace('<a href="#" class="link">Pay now</a>', '<a href="/repayment" class="link">Pay now</a>')
t1 = t1.replace('<a href="#" class="link" style="font-weight:500;color:var(--text2);">Request extension</a>',
                '<a href="/repayment" class="link" style="font-weight:500;color:var(--text2);">Request extension</a>')

dash_script = """
<script>
function requestExtensionQuick(e) {
  e.preventDefault();
  fetch('/api/loans/1/extend', {method: 'POST'})
    .then(r => r.json())
    .then(d => showToast('Extension requested: 7-day grace period granted!'));
}
</script>
"""
t1 = inject_head_and_scripts(t1, "", dash_script)
write_file("templates/dashboard.html", t1)

# -------------------------------------------------------------
# 2. Loan Request
# -------------------------------------------------------------
print("Building templates/loan_request.html...")
t2 = read_file("uiu-aid-2-loan-request.html")
t2 = replace_sidebar(t2, "loans")

# Add loan tabs after page head
loan_tabs = """
    <!-- Loan Flow Sub-Navigation -->
    <div class="tabs" style="margin-bottom: 24px; background: #fff; border-radius: 8px; border: 1px solid var(--border); padding: 4px 16px; box-shadow: var(--shadow); display:flex; gap:16px;">
      <a href="/loan-request" class="tab on" style="text-decoration:none;"><span class="ms ms-18">add_circle</span>1. Request a Loan</a>
      <a href="/auction" class="tab" style="text-decoration:none;"><span class="ms ms-18">gavel</span>2. Live Reverse Auction</a>
      <a href="/repayment" class="tab" style="text-decoration:none;"><span class="ms ms-18">payments</span>3. Active Loan Repayment</a>
    </div>
"""
t2 = t2.replace('<div class="lr-layout">', loan_tabs + '\n    <div class="lr-layout">')

# Add IDs to inputs
t2 = t2.replace('<input class="input" type="text" value="3,000" style="padding-right:42px;font-weight:700;font-size:16px;">',
                '<input id="loan-amount" class="input" type="number" value="3000" style="padding-right:42px;font-weight:700;font-size:16px;">')

t2 = t2.replace('<select class="input">', '<select id="loan-purpose" class="input">')
t2 = t2.replace('<input class="input" type="text" value="Sep 5, 2026">', '<input id="loan-repay-by" class="input" type="text" value="Sep 5, 2026">')
t2 = t2.replace('<textarea class="input" rows="3">', '<textarea id="loan-message" class="input" rows="3">')

t2 = t2.replace('<button class="btn btn-primary">\n                <span class="ms ms-18">gavel</span>\n                Post to Auction\n              </button>',
                '<button id="btn-post-loan" type="button" class="btn btn-primary" onclick="submitLoanRequest()">\n                <span class="ms ms-18">gavel</span>\n                Post to Auction\n              </button>')

loan_req_script = """
<script>
function submitLoanRequest() {
  const amount = document.getElementById('loan-amount').value || 3000;
  const purpose = document.getElementById('loan-purpose').value;
  const repayBy = document.getElementById('loan-repay-by').value;
  const message = document.getElementById('loan-message').value;

  fetch('/api/loans/create', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      amount: parseInt(amount),
      purpose: purpose,
      repay_by: repayBy,
      max_rate: 5.0,
      message: message
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      showToast('Loan request posted to Live Auction successfully!');
      setTimeout(() => {
        window.location.href = '/auction?id=' + data.loan_id;
      }, 1000);
    } else {
      showToast('Error: ' + data.message, 'error');
    }
  })
  .catch(err => {
    showToast('Failed to connect to server', 'error');
  });
}
</script>
"""
t2 = inject_head_and_scripts(t2, "", loan_req_script)
write_file("templates/loan_request.html", t2)

# -------------------------------------------------------------
# 3. Live Reverse Auction
# -------------------------------------------------------------
print("Building templates/reverse_auction.html...")
t3 = read_file("uiu-aid-3-live-reverse-auction.html")
t3 = replace_sidebar(t3, "auction")

loan_tabs_auction = """
    <!-- Loan Flow Sub-Navigation -->
    <div class="tabs" style="margin-bottom: 24px; background: #fff; border-radius: 8px; border: 1px solid var(--border); padding: 4px 16px; box-shadow: var(--shadow); display:flex; gap:16px;">
      <a href="/loan-request" class="tab" style="text-decoration:none;"><span class="ms ms-18">add_circle</span>1. Request a Loan</a>
      <a href="/auction" class="tab on" style="text-decoration:none;"><span class="ms ms-18">gavel</span>2. Live Reverse Auction</a>
      <a href="/repayment" class="tab" style="text-decoration:none;"><span class="ms ms-18">payments</span>3. Active Loan Repayment</a>
    </div>
"""
t3 = t3.replace('<div class="row">', loan_tabs_auction + '\n    <div class="row">', 1)

# Hook up bid submit button
t3 = t3.replace('<button class="btn btn-primary btn-block" style="margin-top:18px;">\n              Submit Bid\n            </button>',
                """<button type="button" class="btn btn-primary btn-block" style="margin-top:18px;" onclick="placeBid()">
              Submit Bid
            </button>
            <button type="button" class="btn btn-secondary btn-block" style="margin-top:10px;" onclick="acceptOffer()">
              <span class="ms ms-18">check_circle</span> Accept Best Offer (3.5%) & Disburse
            </button>""")

auction_script = """
<script>
function placeBid() {
  const rateInput = document.getElementById('bid-rate');
  const rate = parseFloat(rateInput.value) || 3.0;
  
  fetch('/api/auction/2/bid', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      rate: rate,
      lender_id: 1, // Nusrat bidding
      notes: 'Disburse via bKash instant transfer'
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      showToast('Bid of ' + rate + '% submitted! You now hold the lowest bid.');
      
      // Update UI
      const rateBanner = document.querySelector('.bid-banner-rate');
      if (rateBanner) rateBanner.textContent = rate + '%';
      
      const bidsList = document.querySelector('.bids-list');
      if (bidsList) {
        const newRow = document.createElement('div');
        newRow.className = 'frow frow-lowest';
        newRow.innerHTML = `
          <span class="av av-sm av-1">NJ</span>
          <div class="frow-name-block" style="flex:1;min-width:0;">
            <span class="frow-name">Nusrat Jahan (You)</span>
            <span class="frow-time">Just now</span>
          </div>
          <div class="frow-rate-block">
            <span class="frow-rate money" style="color:var(--emerald);">${rate}%</span>
            <span class="pill pill-emerald" style="font-size:11px;padding:2px 8px;">Lowest</span>
          </div>
        `;
        bidsList.insertBefore(newRow, bidsList.firstChild);
      }
    }
  })
  .catch(err => {
    showToast('Failed to place bid', 'error');
  });
}

function acceptOffer() {
  fetch('/api/auction/2/accept', {method: 'POST'})
    .then(r => r.json())
    .then(d => {
      showToast('Offer accepted! Loan activated and funds ready for disbursement.');
      setTimeout(() => {
        window.location.href = '/repayment';
      }, 1200);
    });
}
</script>
"""
t3 = inject_head_and_scripts(t3, "", auction_script)
write_file("templates/reverse_auction.html", t3)

# -------------------------------------------------------------
# 4. Active Loan Repayment
# -------------------------------------------------------------
print("Building templates/loan_repayment.html...")
t4 = read_file("uiu-aid-4-active-loan-repayment.html")
t4 = replace_sidebar(t4, "repayment")

loan_tabs_repay = """
    <!-- Loan Flow Sub-Navigation -->
    <div class="tabs" style="margin-bottom: 24px; background: #fff; border-radius: 8px; border: 1px solid var(--border); padding: 4px 16px; box-shadow: var(--shadow); display:flex; gap:16px;">
      <a href="/loan-request" class="tab" style="text-decoration:none;"><span class="ms ms-18">add_circle</span>1. Request a Loan</a>
      <a href="/auction" class="tab" style="text-decoration:none;"><span class="ms ms-18">gavel</span>2. Live Reverse Auction</a>
      <a href="/repayment" class="tab on" style="text-decoration:none;"><span class="ms ms-18">payments</span>3. Active Loan Repayment</a>
    </div>
"""
t4 = t4.replace('<div class="card summary-card">', loan_tabs_repay + '\n    <div class="card summary-card">', 1)

# Hook up payment button
t4 = t4.replace('<button class="btn btn-primary btn-block">\n          <span class="ms ms-18">payment</span>\n          Pay 552 Tk now\n        </button>',
                '<button id="btn-pay-now" type="button" class="btn btn-primary btn-block" onclick="submitRepayment()">\n          <span class="ms ms-18">payment</span>\n          Pay 552 Tk now via bKash\n        </button>')

# Hook up extension button
t4 = t4.replace('<button class="btn btn-secondary btn-block" style="margin-bottom:12px">\n            Request Extension\n          </button>',
                '<button type="button" class="btn btn-secondary btn-block" style="margin-bottom:12px" onclick="requestExtension()">\n            Request Extension\n          </button>')

# Hook up gig apply links
t4 = t4.replace('<a class="link" style="font-size:13px">Apply</a>',
                '<a href="#" class="link" style="font-size:13px" onclick="applyGigFromRepay(event, this)">Apply</a>')

repay_script = """
<script>
function submitRepayment() {
  const btn = document.getElementById('btn-pay-now');
  btn.disabled = true;
  btn.innerHTML = '<span class="ms ms-18">hourglass_top</span> Processing bKash...';
  
  fetch('/api/loans/1/repay', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      amount: 552,
      payment_method: 'bKash'
    })
  })
  .then(r => r.json())
  .then(d => {
    btn.innerHTML = '<span class="ms ms-18">check_circle</span> Paid in Full!';
    btn.className = 'btn btn-block';
    btn.style.background = '#059669';
    btn.style.color = '#fff';
    
    // Update progress bar
    const bar = document.querySelector('.bar.bar-10 i');
    if (bar) bar.style.width = '100%';
    
    const barText = document.querySelector('.bar-row');
    if (barText) barText.innerHTML = '<span class="ms ms-16" style="color:var(--emerald)">verified</span> <strong>1,552 of 1,552 Tk repaid (100% complete)</strong>';
    
    showToast('Payment of 552 Tk verified! +2 Trust Points awarded.');
  })
  .catch(err => {
    btn.disabled = false;
    btn.innerHTML = '<span class="ms ms-18">payment</span> Pay 552 Tk now via bKash';
    showToast('Payment failed, please retry.', 'error');
  });
}

function requestExtension() {
  fetch('/api/loans/1/extend', {method: 'POST'})
    .then(r => r.json())
    .then(d => {
      showToast('Extension approved! Due date moved to Aug 9, 2026.');
      const duePill = document.querySelector('.summary-top .pill');
      if (duePill) duePill.textContent = 'Due in 10 days';
    });
}

function applyGigFromRepay(e, el) {
  e.preventDefault();
  el.textContent = 'Applied ✓';
  el.style.color = '#059669';
  showToast('Gig application submitted! Earnings will route directly to loan.');
}
</script>
"""
t4 = inject_head_and_scripts(t4, "", repay_script)
write_file("templates/loan_repayment.html", t4)

# -------------------------------------------------------------
# 5. Crowdfunding Transparency
# -------------------------------------------------------------
print("Building templates/crowdfunding.html...")
t5 = read_file("uiu-aid-5-crowdfunding-transparency.html")
t5 = replace_sidebar(t5, "crowdfunding")

# Hook up donate button in sticky card
t5 = t5.replace('<button class="btn btn-primary btn-block btn-lg" style="margin-top: 20px;">\n            Contribute to Fahim\n          </button>',
                '<button id="btn-donate-crowd" type="button" class="btn btn-primary btn-block btn-lg" style="margin-top: 20px;" onclick="donateCrowdfunding()">\n            Contribute 1,000 Tk to Fahim\n          </button>')

crowd_script = """
<script>
function donateCrowdfunding() {
  const btn = document.getElementById('btn-donate-crowd');
  btn.disabled = true;
  btn.textContent = 'Processing bKash Contribution...';
  
  fetch('/api/crowdfunding/1/donate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      amount: 1000,
      donor_name: 'Nusrat Jahan',
      is_anonymous: false
    })
  })
  .then(r => r.json())
  .then(d => {
    btn.disabled = false;
    btn.textContent = 'Contributed 1,000 Tk ✓';
    showToast('Thank you! 1,000 Tk donated to Fahim via bKash. Receipt logged in ledger.');
    
    // Update raised total if displayed
    const progressFill = document.querySelector('.cf-progress-fill');
    if (progressFill) progressFill.style.width = '88%';
  })
  .catch(err => {
    btn.disabled = false;
    btn.textContent = 'Contribute to Fahim';
    showToast('Donation failed to connect', 'error');
  });
}
</script>
"""
t5 = inject_head_and_scripts(t5, "", crowd_script)
write_file("templates/crowdfunding.html", t5)

# -------------------------------------------------------------
# 6. Campus Gig Board
# -------------------------------------------------------------
print("Building templates/gig_board.html...")
t6 = read_file("uiu-aid-6-campus-gig-board.html")
t6 = replace_sidebar(t6, "gigs")

# Add IDs to filters and search
t6 = t6.replace('<div class="filter-pills">', '<div class="filter-pills" id="gig-filters">')
t6 = t6.replace('<input class="input" type="text" placeholder="Search gigs…">',
                '<input id="gig-search" class="input" type="text" placeholder="Search gigs…" oninput="filterGigsSearch(this.value)">')

# Add modal for Post a Gig
post_gig_modal = """
<!-- Post a Gig Modal -->
<div id="modal-post-gig" style="display:none;position:fixed;inset:0;background:rgba(15,23,42,0.6);z-index:9999;align-items:center;justify-content:center;padding:20px;">
  <div class="card" style="width:100%;max-width:520px;background:#fff;padding:28px;border-radius:12px;box-shadow:0 20px 40px rgba(0,0,0,0.2);">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;">
      <h3 style="font-size:18px;font-weight:700;">Post a Campus Gig</h3>
      <button type="button" onclick="closeModal('modal-post-gig')" style="background:none;border:none;cursor:pointer;font-size:20px;">&times;</button>
    </div>
    <div class="field" style="margin-bottom:14px;">
      <label>Gig Title</label>
      <input id="post-gig-title" class="input" placeholder="e.g. Lab Report typing & formatting">
    </div>
    <div class="grid-2" style="margin-bottom:14px;">
      <div class="field">
        <label>Category</label>
        <select id="post-gig-category" class="input">
          <option>Tech & Code</option>
          <option>Design</option>
          <option>Tutoring</option>
          <option>Notes & Writing</option>
          <option>Errands</option>
        </select>
      </div>
      <div class="field">
        <label>Budget (Tk)</label>
        <input id="post-gig-budget" type="number" class="input" value="500">
      </div>
    </div>
    <div class="field" style="margin-bottom:20px;">
      <label>Due Info</label>
      <input id="post-gig-due" class="input" value="due in 3 days">
    </div>
    <button type="button" class="btn btn-primary btn-block" onclick="createGigSubmit()">Post Gig to Board</button>
  </div>
</div>
"""
t6 = t6.replace('</main>', post_gig_modal + '\n  </main>')

# Make "Post a Gig" button open modal
t6 = t6.replace('<button class="btn btn-primary">\n          <span class="ms ms-18">add_circle</span>\n          Post a Gig\n        </button>',
                '<button class="btn btn-primary" onclick="openModal(\'modal-post-gig\')">\n          <span class="ms ms-18">add_circle</span>\n          Post a Gig\n        </button>')

# Make withdraw link clickable
t6 = t6.replace('<a class="link withdraw-link" href="#">Withdraw to bKash &rarr;</a>',
                '<a class="link withdraw-link" href="#" onclick="withdrawBkash(event)">Withdraw to bKash &rarr;</a>')

# Make gig apply buttons interactive
t6 = re.sub(r'<button class="btn btn-secondary btn-sm btn-block">Apply</button>',
            r'<button class="btn btn-secondary btn-sm btn-block" onclick="applyGigCard(this)">Apply</button>', t6)

gig_script = """
<script>
function withdrawBkash(e) {
  e.preventDefault();
  showToast('Withdrawal of 3,400 Tk sent to bKash 01711-XXXXXX! Estimated arrival: 15 mins.');
}

function applyGigCard(btn) {
  btn.textContent = 'Applied ✓';
  btn.className = 'btn btn-sm btn-block';
  btn.style.background = '#059669';
  btn.style.color = '#fff';
  btn.disabled = true;
  showToast('Applied for gig! Funds reserved in UIU Aid escrow.');
}

function createGigSubmit() {
  const title = document.getElementById('post-gig-title').value;
  const category = document.getElementById('post-gig-category').value;
  const budget = parseInt(document.getElementById('post-gig-budget').value) || 500;
  const due = document.getElementById('post-gig-due').value || 'due in 2 days';
  
  if (!title) {
    showToast('Please enter a gig title', 'error');
    return;
  }
  
  fetch('/api/gigs/post', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      title: title,
      category: category,
      budget: budget,
      due_info: due,
      poster_id: 1
    })
  })
  .then(r => r.json())
  .then(d => {
    closeModal('modal-post-gig');
    showToast('Gig posted successfully to UIU Campus Board!');
    
    // Prepend new card
    const grid = document.querySelector('.grid-3');
    if (grid) {
      const card = document.createElement('div');
      card.className = 'gig-card';
      card.innerHTML = `
        <div class="gig-tag tag">${category}</div>
        <div class="gig-title">${title}</div>
        <div class="gig-budget money">${budget} Tk</div>
        <div class="gig-poster">
          <span class="av av-sm av-1">NJ</span>
          <span class="gig-poster-name">Nusrat Jahan</span>
          <span class="pill pill-emerald">82 trust</span>
        </div>
        <hr class="divider">
        <div class="gig-meta">
          <div class="gig-meta-left">
            <span class="ms">schedule</span>
            <span>${due}</span>
          </div>
          <div class="gig-meta-right">0 applicants</div>
        </div>
        <button class="btn btn-secondary btn-sm btn-block" disabled>Your Gig</button>
      `;
      grid.insertBefore(card, grid.firstChild);
    }
  });
}

// Category filter
document.addEventListener('DOMContentLoaded', () => {
  const pills = document.querySelectorAll('#gig-filters .fpill');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('on'));
      pill.classList.add('on');
      const cat = pill.textContent.trim();
      const cards = document.querySelectorAll('.gig-card');
      cards.forEach(c => {
        const tag = c.querySelector('.gig-tag')?.textContent.trim();
        if (cat === 'All' || tag === cat) {
          c.style.display = 'block';
        } else {
          c.style.display = 'none';
        }
      });
    });
  });
});

function filterGigsSearch(val) {
  const q = val.toLowerCase().trim();
  const cards = document.querySelectorAll('.gig-card');
  cards.forEach(c => {
    const title = c.querySelector('.gig-title')?.textContent.toLowerCase() || '';
    if (!q || title.includes(q)) {
      c.style.display = 'block';
    } else {
      c.style.display = 'none';
    }
  });
}
</script>
"""
t6 = inject_head_and_scripts(t6, "", gig_script)
write_file("templates/gig_board.html", t6)

# -------------------------------------------------------------
# 7. Anonymous Meal Drops
# -------------------------------------------------------------
print("Building templates/meal_drops.html...")
t7 = read_file("uiu-aid-7-anonymous-meal-drops.html")
t7 = replace_sidebar(t7, "meals")

# Make Gift a Meal button active
t7 = t7.replace('<button class="btn btn-primary btn-block btn-lg">Gift a Meal</button>',
                '<button id="btn-gift-meal" type="button" class="btn btn-primary btn-block btn-lg" onclick="giftMealDrop()">Gift a Meal (120 Tk)</button>')

# Make Claim a Meal interactive
claim_card_find = '<p class="card-body-copy" style="max-width:340px">No questions, no names. If you\'re hungry today, eat today.</p>'
claim_card_replace = claim_card_find + """
          <button id="btn-claim-meal" type="button" class="btn btn-secondary btn-block btn-lg" style="margin-top:16px;" onclick="claimMealDrop()">
            <span class="ms ms-18">qr_code</span> Generate Cafeteria Token
          </button>
          <div id="claimed-voucher-box" style="display:none;width:100%;margin-top:20px;padding:16px;border-radius:8px;background:rgba(16,185,129,0.08);border:1.5px dashed #059669;">
            <div style="font-size:12px;font-weight:700;color:#065F46;text-transform:uppercase;">Cafeteria Voucher Active</div>
            <div id="voucher-code" class="money" style="font-size:24px;color:#0F172A;margin:8px 0;letter-spacing:1px;">UIU-MEAL-8821</div>
            <div style="font-size:12.5px;color:#475569;">Present this code to the attendant at Cafeteria Counter 2 for 1 Hot Meal. 100% Anonymous.</div>
          </div>
"""
t7 = t7.replace(claim_card_find, claim_card_replace)

meal_script = """
<script>
let currentMealQty = 1;

document.addEventListener('DOMContentLoaded', () => {
  const qtyNum = document.querySelector('.qty-num');
  const minusBtn = document.querySelectorAll('.qty-btn')[0];
  const plusBtn = document.querySelectorAll('.qty-btn')[1];
  const totalAmt = document.querySelector('.total-amt');
  const giftBtn = document.getElementById('btn-gift-meal');
  const chips = document.querySelectorAll('.qty-row .chip');
  
  function updateMealDisplay(qty) {
    currentMealQty = Math.max(1, qty);
    if (qtyNum) qtyNum.textContent = currentMealQty;
    const total = currentMealQty * 120;
    if (totalAmt) totalAmt.textContent = total + ' Tk';
    if (giftBtn) giftBtn.textContent = 'Gift ' + currentMealQty + ' Meal' + (currentMealQty > 1 ? 's' : '') + ' (' + total + ' Tk)';
  }
  
  if (minusBtn) minusBtn.addEventListener('click', () => updateMealDisplay(currentMealQty - 1));
  if (plusBtn) plusBtn.addEventListener('click', () => updateMealDisplay(currentMealQty + 1));
  
  chips.forEach((c, idx) => {
    c.addEventListener('click', () => {
      const q = idx === 0 ? 2 : 5;
      updateMealDisplay(q);
    });
  });
});

function giftMealDrop() {
  fetch('/api/meals/gift', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      meals_count: currentMealQty,
      donor_id: 1
    })
  })
  .then(r => r.json())
  .then(d => {
    showToast('Thank you! ' + currentMealQty + ' meal credit(s) added anonymously to UIU Cafeteria pool.');
    const statNums = document.querySelectorAll('.stat-num');
    if (statNums.length > 1) {
      statNums[0].textContent = parseInt(statNums[0].textContent || 213) + currentMealQty;
      statNums[1].textContent = parseInt(statNums[1].textContent || 41) + currentMealQty;
    }
  });
}

function claimMealDrop() {
  fetch('/api/meals/claim', {method: 'POST'})
    .then(r => r.json())
    .then(d => {
      if (d.status === 'success') {
        const box = document.getElementById('claimed-voucher-box');
        const codeEl = document.getElementById('voucher-code');
        if (box && codeEl) {
          codeEl.textContent = d.claim_code;
          box.style.display = 'block';
        }
        showToast('Meal token claimed! Secret code generated for cafeteria counter.');
        
        const statNums = document.querySelectorAll('.stat-num');
        if (statNums.length > 1) {
          statNums[1].textContent = Math.max(0, parseInt(statNums[1].textContent || 41) - 1);
        }
      }
    });
}
</script>
"""
t7 = inject_head_and_scripts(t7, "", meal_script)
write_file("templates/meal_drops.html", t7)

# -------------------------------------------------------------
# 8. Trust Profile & Reputation
# -------------------------------------------------------------
print("Building templates/trust_profile.html...")
t8 = read_file("uiu-aid-8-trust-profile-reputation.html")
t8 = replace_sidebar(t8, "trust")

write_file("templates/trust_profile.html", t8)

print("All 8 templates built successfully in templates/!")
