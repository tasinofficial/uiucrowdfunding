import re

# Read dashboard as base
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dashboard = f.read()

# Extract from start up to <main class="main">
base_idx = dashboard.find('<main class="main">')
base_head = dashboard[:base_idx + len('<main class="main">')]

# For reverse_auction.html we need to fix the active nav
base_head_auction = re.sub(r'class="nav-item active" href="/"', 'class="nav-item " href="/"', base_head)
base_head_auction = re.sub(r'class="nav-item " href="/loan-request"', 'class="nav-item active" href="/loan-request"', base_head_auction)

base_head_repayment = re.sub(r'class="nav-item active" href="/"', 'class="nav-item " href="/"', base_head)
base_head_repayment = re.sub(r'class="nav-item " href="/loan-request"', 'class="nav-item active" href="/loan-request"', base_head_repayment)

auction_content = """
    <div class="page-head" style="margin-bottom:24px;">
      <div>
        <h1>Loan Auction #{{ loan.id }}</h1>
        <div class="sub">Live reverse auction — the lowest rate wins</div>
      </div>
    </div>

    <!-- Loan Flow Sub-Navigation -->
    <div class="tabs" style="margin-bottom: 24px; background: #fff; border-radius: 8px; border: 1px solid var(--border); padding: 4px 16px; box-shadow: var(--shadow); display:flex; gap:16px;">
      <a href="/loan-request" class="tab" style="text-decoration:none;"><span class="ms ms-18">add_circle</span>1. Request a Loan</a>
      <a href="/auction" class="tab on" style="text-decoration:none;"><span class="ms ms-18">gavel</span>2. Live Reverse Auction</a>
      <a href="/repayment" class="tab" style="text-decoration:none;"><span class="ms ms-18">payments</span>3. Active Loan Repayment</a>
    </div>

    <div class="row" style="display:flex;gap:24px;">

      <!-- LEFT COLUMN -->
      <div class="col" style="flex:1;">
        <div class="card" style="height:100%;display:flex;flex-direction:column;">
          <!-- Borrower header -->
          <div style="display:flex;justify-content:space-between;margin-bottom:16px;">
            <div style="display:flex;gap:14px;">
              <span class="av av-lg {{ borrower.avatar_class }}">{{ borrower.initials }}</span>
              <div style="display:flex;flex-direction:column;gap:4px;">
                <div style="font-size:18px;font-weight:700;">{{ borrower.name }}</div>
                <div style="display:flex;align-items:center;gap:8px;">
                  <span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:var(--emerald);color:#fff;font-size:12px;font-weight:800;">{{ borrower.trust_score }}</span>
                  <span style="font-size:13.5px;color:var(--text2);">Trust Score</span>
                </div>
                <div style="font-size:13.5px;color:var(--text2);">{{ borrower.department }} &middot; {{ borrower.trimester }}</div>
              </div>
            </div>
            <div style="display:flex;flex-direction:column;align-items:center;gap:6px;">
              <span class="pill pill-slate" style="font-size:11px;">{{ borrower.tier }}</span>
            </div>
          </div>
          <hr class="divider">
          <!-- Loan info -->
          <div style="margin-bottom:8px;"><span class="tag">Requested</span></div>
          <div style="font-size:40px;font-weight:800;letter-spacing:-.02em;">{{ loan.amount | int }} Tk</div>
          
          <div style="display:flex;flex-direction:column;gap:10px;margin-top:14px;">
            <div style="display:flex;align-items:center;gap:10px;font-size:14px;">
              <span class="ms" style="color:var(--text2);">campaign</span>
              <span>{{ loan.purpose }}</span>
            </div>
            <div style="display:flex;align-items:center;gap:10px;font-size:14px;">
              <span class="ms" style="color:var(--text2);">schedule</span>
              <span>Repay by {{ loan.repay_by }}</span>
            </div>
            <div style="display:flex;align-items:center;gap:10px;font-size:14px;">
              <span class="ms" style="color:var(--text2);">percent</span>
              <span>Max rate <strong>{{ loan.max_interest_rate }}%</strong></span>
            </div>
            <div style="font-size:14px;color:var(--text2);margin-top:8px;">"{{ loan.message }}"</div>
          </div>
          
          <hr class="divider">
          <div style="font-size:13px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--text2);margin-bottom:12px;">Guarantors</div>
          <div style="display:flex;align-items:center;gap:10px;padding:9px 0;">
             <span class="ms">person</span>
             <div>
               <div style="font-size:14px;font-weight:600;">{{ loan.guarantor_1 }}</div>
             </div>
          </div>
          <div style="display:flex;align-items:center;gap:10px;padding:9px 0;border-top:1px solid var(--border);">
             <span class="ms">person</span>
             <div>
               <div style="font-size:14px;font-weight:600;">{{ loan.guarantor_2 }}</div>
             </div>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN -->
      <div class="col" style="flex:1.1;display:flex;flex-direction:column;gap:24px;">
        
        <!-- Lowest Bid Banner -->
        <div style="background:var(--emerald);border-radius:var(--r);padding:20px 22px;box-shadow:var(--shadow);display:flex;align-items:center;justify-content:space-between;gap:16px;color:#fff;">
           <div style="display:flex;flex-direction:column;gap:4px;">
             <div style="display:flex;align-items:center;gap:8px;">
               <span class="dot-live"></span><span style="font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:rgba(255,255,255,.72);">Current Lowest Bid</span>
             </div>
             <div style="font-size:34px;font-weight:800;font-variant-numeric:tabular-nums;letter-spacing:-.02em;line-height:1.1;">
               {% if lowest_bid %}{{ lowest_bid.interest_rate }}{% else %}{{ loan.max_interest_rate }}{% endif %}%
             </div>
             <div style="font-size:13px;color:rgba(255,255,255,.85);font-weight:500;">
               Offered by {% if lowest_bid %}{{ lowest_bid.initials }}{% else %}None{% endif %}
             </div>
           </div>
           <div style="display:flex;flex-direction:column;align-items:flex-end;gap:8px;">
             <div style="font-size:12px;color:rgba(255,255,255,.72);font-weight:500;">Auction ends in</div>
             <div id="auction-timer" style="font-size:20px;font-weight:700;font-variant-numeric:tabular-nums;letter-spacing:-.01em;">--:--:--</div>
           </div>
        </div>

        <!-- Place Bid Card -->
        <div class="card">
          <div class="card-title"><span class="ms">gavel</span>Place your bid</div>
          <div class="field">
            <label>Your interest rate (%)</label>
            <input type="number" id="bid-rate" class="input" step="0.1" min="0.5" max="{{ loan.max_interest_rate }}" value="{% if lowest_bid %}{{ lowest_bid.interest_rate - 0.1 }}{% else %}{{ loan.max_interest_rate - 0.1 }}{% endif %}">
          </div>
          <div class="field" style="margin-top:12px;">
            <label>Notes</label>
            <textarea id="bid-notes" class="input" placeholder="e.g. Can disburse via bKash right now"></textarea>
          </div>
          <button type="button" class="btn btn-primary btn-block" style="margin-top:18px;" onclick="placeBid({{ loan.id }})">Submit Bid</button>
          
          {% if bids %}
          <div style="margin-top:16px;border-top:1px solid var(--border);padding-top:16px;font-size:13px;">
             If accepted now: you pay <strong><span id="calc-total">{{ (loan.amount * (1 + (lowest_bid.interest_rate if lowest_bid else loan.max_interest_rate)/100)) | int }}</span> Tk</strong> total (save <strong>{{ (loan.amount * (loan.max_interest_rate - (lowest_bid.interest_rate if lowest_bid else loan.max_interest_rate))/100) | int }}</strong> Tk vs max rate)
          </div>
          <button type="button" class="btn btn-secondary btn-block" style="margin-top:16px;" onclick="acceptOffer({{ loan.id }})"><span class="ms">handshake</span> Accept Best Offer</button>
          {% endif %}
        </div>

        <!-- Live Bids List -->
        <div class="card">
          <div class="card-title"><span class="ms">format_list_bulleted</span>Live bids</div>
          <div style="display:flex;flex-direction:column;">
            {% for bid in bids %}
            <div style="display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid var(--border);">
               <div style="font-size:16px;font-weight:800;color:var({% if loop.index == 1 %}--amber{% else %}--text2{% endif %});width:20px;">#{{ loop.index }}</div>
               <span class="av av-sm {{ bid.avatar_class }}">{{ bid.initials }}</span>
               <div style="flex:1;">
                 <div style="font-size:14px;font-weight:600;display:flex;gap:6px;align-items:center;">
                   {{ bid.lender_name }}
                   {% if loop.index == 1 %}<span class="pill pill-amber" style="padding:2px 6px;font-size:10px;"><span class="ms ms-16 ms-fill">star</span>Winning</span>{% endif %}
                 </div>
                 <div style="font-size:12px;color:var(--text2);">{{ bid.notes }}</div>
               </div>
               <div style="text-align:right;">
                 <div style="font-size:16px;font-weight:800;">{{ bid.interest_rate }}%</div>
               </div>
            </div>
            {% else %}
            <div style="padding:16px;text-align:center;color:var(--text2);font-size:14px;">No bids yet.</div>
            {% endfor %}
          </div>
        </div>

      </div>
    </div>
  </main>
</div>

<div id="toast-container" style="position:fixed;bottom:24px;right:24px;display:flex;flex-direction:column;gap:10px;z-index:9999;"></div>

<script>
  let secondsRemaining = {{ loan.days_remaining * 86400 }};
  const timerEl = document.getElementById("auction-timer");
  setInterval(() => {
    if(secondsRemaining <= 0) return;
    secondsRemaining--;
    let h = Math.floor(secondsRemaining / 3600);
    let m = Math.floor((secondsRemaining % 3600) / 60);
    let s = secondsRemaining % 60;
    timerEl.innerText = `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
  }, 1000);

  function showToast(msg, type='success') {
    const c = document.getElementById('toast-container');
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.innerHTML = `<span class="ms" style="color:var(--${type==='success'?'emerald':'crimson'})">${type==='success'?'check_circle':'error'}</span> <div style="background:#fff;padding:12px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">${msg}</div>`;
    c.appendChild(t);
    setTimeout(() => t.remove(), 4000);
  }

  async function placeBid(loanId) {
    const rate = parseFloat(document.getElementById('bid-rate').value);
    const notes = document.getElementById('bid-notes').value;
    const currentBest = {% if lowest_bid %}{{ lowest_bid.interest_rate }}{% else %}{{ loan.max_interest_rate }}{% endif %};
    if (rate >= currentBest) {
        showToast('Bid rate must be lower than current best rate.', 'error');
        return;
    }
    try {
      const res = await fetch(`/api/auction/${loanId}/bid`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({rate, notes, lender_id: 2})
      });
      const data = await res.json();
      if(data.status === 'success') {
        showToast('Bid placed successfully!');
        setTimeout(() => location.reload(), 1000);
      }
    } catch(e) { showToast('Error placing bid.', 'error'); }
  }

  async function acceptOffer(loanId) {
    try {
      const res = await fetch(`/api/auction/${loanId}/accept`, { method: 'POST' });
      const data = await res.json();
      if(data.status === 'success') {
        showToast('Offer accepted!');
        setTimeout(() => window.location.href = '/repayment', 1000);
      }
    } catch(e) { showToast('Error accepting offer.', 'error'); }
  }

  setInterval(() => {
    // location.reload();
  }, 15000);
</script>
</body>
</html>
"""

repayment_content = """
    <div class="page-head" style="margin-bottom:24px;">
      <div>
        <h1>Loan Repayment</h1>
        <div class="sub">Active Loan #{{ loan.id }}</div>
      </div>
    </div>

    <!-- Loan Flow Sub-Navigation -->
    <div class="tabs" style="margin-bottom: 24px; background: #fff; border-radius: 8px; border: 1px solid var(--border); padding: 4px 16px; box-shadow: var(--shadow); display:flex; gap:16px;">
      <a href="/loan-request" class="tab" style="text-decoration:none;"><span class="ms ms-18">add_circle</span>1. Request a Loan</a>
      <a href="/auction" class="tab" style="text-decoration:none;"><span class="ms ms-18">gavel</span>2. Live Reverse Auction</a>
      <a href="/repayment" class="tab on" style="text-decoration:none;"><span class="ms ms-18">payments</span>3. Active Loan Repayment</a>
    </div>

    <!-- Repayment escalation stepper -->
    <div class="card" style="margin-bottom:24px;padding:32px;">
      <div class="steps">
        <div class="step {% if loan.days_remaining > 5 %}current{% else %}done{% endif %}">
           <div class="step-dot"><span class="ms">check</span></div>
           <b>On time</b><small>All good</small>
        </div>
        <div class="step {% if loan.days_remaining <= 5 and loan.days_remaining > 0 %}current{% elif loan.days_remaining <= 0 %}done{% endif %}">
           <div class="step-dot"><span class="ms">priority_high</span></div>
           <b>Grace period</b><small>{{ loan.days_remaining }} days left</small>
        </div>
        <div class="step {% if loan.days_remaining <= 0 %}current danger{% endif %}">
           <div class="step-dot"><span class="ms">warning</span></div>
           <b>At-risk</b><small>Reputation hit</small>
        </div>
        <div class="step">
           <div class="step-dot"><span class="ms">gavel</span></div>
           <b>Default</b><small>Guarantors pay</small>
        </div>
      </div>
    </div>

    <div class="row" style="display:flex;gap:24px;">
      
      <!-- LEFT COLUMN -->
      <div class="col" style="flex:1;">
        <div class="card" style="display:flex;flex-direction:column;gap:24px;">
           <div class="card-title" style="margin:0;"><span class="ms">account_balance_wallet</span>Payment Status</div>
           
           <div style="display:flex;justify-content:space-between;align-items:center;">
             <div class="m-card">
               <div class="m-label">Total Due</div>
               <div class="m-value">{{ loan.total_due | int }}<span class="m-sub">Tk</span></div>
             </div>
             <div class="m-card text-right" style="text-align:right;">
               <div class="m-label">Repaid</div>
               <div class="m-value" style="color:var(--emerald);">{{ loan.total_repaid | int }}<span class="m-sub">Tk</span></div>
             </div>
           </div>

           <div>
             <div style="display:flex;justify-content:space-between;margin-bottom:6px;font-size:13px;font-weight:600;">
               <span>Progress</span>
               <span>{{ ((loan.total_repaid / loan.total_due) * 100) | int }}%</span>
             </div>
             <div class="bar bar-lg">
               <i style="width:{{ (loan.total_repaid / loan.total_due * 100) | int }}%"></i>
             </div>
           </div>
           
           <div style="display:flex;justify-content:space-between;align-items:center;background:var(--bg);padding:16px;border-radius:var(--r);">
             <div class="m-card">
               <div class="m-label">Remaining</div>
               <div class="m-value" style="color:var(--amber);">{{ (loan.total_due - loan.total_repaid) | int }}<span class="m-sub">Tk</span></div>
             </div>
             <div class="m-card" style="text-align:right;">
               <div class="m-label">Days Left</div>
               <div class="m-value" style="color:var(--{% if loan.days_remaining <= 3 %}crimson{% else %}amber{% endif %});">{{ loan.days_remaining }}<span class="m-sub">Days</span></div>
             </div>
           </div>
        </div>

        <div class="card" style="margin-top:24px;">
          <div class="card-title"><span class="ms">description</span>Loan Terms</div>
          <div style="display:flex;flex-direction:column;gap:12px;">
            <div style="display:flex;align-items:center;gap:8px;font-size:14px;"><span class="ms">money</span>{{ loan.amount | int }} Tk @ {{ loan.current_interest_rate }}% interest</div>
            <div style="display:flex;align-items:center;gap:8px;font-size:14px;"><span class="ms">group</span>Guarantors: {{ loan.guarantor_1 }} &amp; {{ loan.guarantor_2 }}</div>
            <div style="display:flex;align-items:center;gap:8px;font-size:14px;"><span class="ms">event</span>Due date: <strong>{{ loan.due_date }}</strong></div>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN -->
      <div class="col" style="flex:1;">
        
        <div class="card">
          <div class="card-title"><span class="ms">person</span>Lender</div>
          <div style="display:flex;align-items:center;gap:12px;">
            <span class="av av-lg {% if lender %}{{ lender.avatar_class }}{% else %}av-4{% endif %}">{% if lender %}{{ lender.initials }}{% else %}KH{% endif %}</span>
            <div style="flex:1;">
              <div style="font-size:16px;font-weight:700;">{% if lender %}{{ lender.name }}{% else %}Karim Hossain{% endif %}</div>
              <div style="display:flex;align-items:center;gap:6px;margin-top:4px;">
                <span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;background:var(--navy);color:#fff;font-size:11px;font-weight:800;">{% if lender %}{{ lender.trust_score }}{% else %}91{% endif %}</span>
                <span style="font-size:13px;color:var(--text2);">Trust Score</span>
              </div>
            </div>
          </div>
        </div>

        <div class="card" style="margin-top:24px;">
          <div class="card-title"><span class="ms">payments</span>Make a Payment</div>
          <div class="field" style="margin-bottom:16px;">
            <label>Payment Method</label>
            <div class="chips">
              <span class="chip on">bKash</span>
              <span class="chip">Nagad</span>
              <span class="chip">Cash chips</span>
            </div>
          </div>
          <div class="field" style="margin-bottom:24px;">
            <label>Amount to Pay (Tk)</label>
            <input type="number" id="repay-amount" class="input" value="{{ (loan.total_due - loan.total_repaid) | int }}" style="font-size:20px;font-weight:700;">
          </div>
          
          <button type="button" id="pay-btn" class="btn btn-primary btn-block btn-lg" onclick="repayLoan({{ loan.id }})">
            <span class="ms">lock</span><span id="pay-btn-text">Pay via bKash</span>
          </button>
          <button type="button" id="extend-btn" class="btn btn-secondary btn-block" style="margin-top:12px;" onclick="extendLoan({{ loan.id }})">
            <span class="ms">update</span>Request 7-day extension
          </button>
        </div>

      </div>

    </div>
  </main>
</div>

<div id="toast-container" style="position:fixed;bottom:24px;right:24px;display:flex;flex-direction:column;gap:10px;z-index:9999;"></div>
<div id="success-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:10000;align-items:center;justify-content:center;">
    <div style="background:#fff;padding:32px;border-radius:12px;text-align:center;max-width:400px;width:100%;box-shadow:var(--shadow);">
        <div style="font-size:48px;margin-bottom:16px;">🎉</div>
        <h2 style="font-size:24px;margin-bottom:8px;">Payment Successful!</h2>
        <p style="color:var(--text2);margin-bottom:16px;">Trx ID: <span id="modal-trx-id" style="font-weight:700;"></span></p>
        <div style="background:var(--emerald);color:#fff;padding:12px;border-radius:8px;margin-bottom:24px;font-weight:600;">
            Trust Score +2! New Score: <span id="modal-trust-score"></span>
        </div>
        <button class="btn btn-primary btn-block" onclick="location.reload()">Close & Reload</button>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
<script>
  let selectedMethod = 'bKash';
  document.querySelectorAll('.chip').forEach(chip => {
      chip.addEventListener('click', (e) => {
          document.querySelectorAll('.chip').forEach(c => c.classList.remove('on'));
          e.currentTarget.classList.add('on');
          selectedMethod = e.currentTarget.innerText.trim();
          document.getElementById('pay-btn-text').innerText = 'Pay via ' + selectedMethod;
      });
  });

  function showToast(msg, type='success') {
    const c = document.getElementById('toast-container');
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.innerHTML = `<span class="ms" style="color:var(--${type==='success'?'emerald':'crimson'})">${type==='success'?'check_circle':'error'}</span> <div style="background:#fff;padding:12px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">${msg}</div>`;
    c.appendChild(t);
    setTimeout(() => t.remove(), 4000);
  }

  async function repayLoan(loanId) {
    const btn = document.getElementById('pay-btn');
    const amount = parseInt(document.getElementById('repay-amount').value);
    btn.innerHTML = '<span class="ms" style="animation: spin 1s linear infinite;">refresh</span> Processing...';
    btn.disabled = true;

    try {
      const res = await fetch(`/api/loans/${loanId}/repay`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({amount, payment_method: selectedMethod})
      });
      const data = await res.json();
      if(data.status === 'success') {
        confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } });
        document.getElementById('success-modal').style.display = 'flex';
        document.getElementById('modal-trx-id').innerText = data.trx_id;
        document.getElementById('modal-trust-score').innerText = data.new_trust_score;
      } else {
          showToast('Payment failed.', 'error');
          btn.disabled = false;
          btn.innerHTML = '<span class="ms">lock</span><span id="pay-btn-text">Pay via ' + selectedMethod + '</span>';
      }
    } catch(e) {
      showToast('Error processing payment.', 'error');
      btn.disabled = false;
      btn.innerHTML = '<span class="ms">lock</span><span id="pay-btn-text">Pay via ' + selectedMethod + '</span>';
    }
  }

  async function extendLoan(loanId) {
    const btn = document.getElementById('extend-btn');
    btn.disabled = true;
    try {
      const res = await fetch(`/api/loans/${loanId}/extend`, { method: 'POST' });
      const data = await res.json();
      if(data.status === 'success') {
        showToast(`Extension granted. New remaining days: ${data.new_days}`);
        setTimeout(() => location.reload(), 1500);
      }
    } catch(e) {
      showToast('Error requesting extension.', 'error');
      btn.disabled = false;
    }
  }
</script>
<style>
@keyframes spin { 100% { transform: rotate(360deg); } }
</style>
</body>
</html>
"""

with open('templates/reverse_auction.html', 'w', encoding='utf-8') as f:
    f.write(base_head_auction + auction_content)

with open('templates/loan_repayment.html', 'w', encoding='utf-8') as f:
    f.write(base_head_repayment + repayment_content)
