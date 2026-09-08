import re
import sys

def rewrite_auction():
    with open('templates/reverse_auction.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Page Title
    content = re.sub(r'<title>.*?</title>', '<title>Live Reverse Auction — Loan #{{ loan.id }}</title>', content)

    # Borrower profile
    content = re.sub(r'<span class="av av-lg av-2">TH</span>', '<span class="av av-lg {{ borrower.avatar_class }}">{{ borrower.initials }}</span>', content)
    content = re.sub(r'<div class="borrower-name">Tanvir Hasan</div>', '<div class="borrower-name">{{ borrower.name }}</div>', content)
    content = re.sub(r'<span class="trust-mini">78</span>', '<span class="trust-mini">{{ borrower.trust_score }}</span>', content)
    content = re.sub(r'<div class="borrower-sub" style="margin-top:2px;">CSE &middot; 7th trimester</div>', '<div class="borrower-sub" style="margin-top:2px;">{{ borrower.department }} &middot; {{ borrower.trimester }}</div>', content)
    
    # Gauges (Score 78 -> {{ borrower.trust_score }})
    # We can replace the stroke-dashoffset math with Jinja:
    content = re.sub(
        r'stroke-dashoffset="71\.9"',
        'stroke-dashoffset="{{ 326.7 * (1 - (borrower.trust_score / 100)) }}"',
        content
    )
    content = re.sub(
        r'<text x="60" y="57".*?>78</text>',
        '<text x="60" y="57" text-anchor="middle" font-size="30" font-weight="800" fill="#0F172A" font-family="Inter">{{ borrower.trust_score }}</text>',
        content
    )
    content = re.sub(
        r'Silver Tier',
        '{{ borrower.tier }}',
        content
    )

    # Loan info
    content = re.sub(r'<span class="ms">money</span> 3,000 Tk &middot; Medical emergency', '<span class="ms">money</span> {{ loan.amount | int }} Tk &middot; {{ loan.purpose }}', content)
    content = re.sub(r'<span class="ms">event</span> Repay by: Sep 5, 2026', '<span class="ms">event</span> Repay by: {{ loan.repay_by }}', content)
    content = re.sub(r'<span class="ms">percent</span> Max rate: 5\.0%', '<span class="ms">percent</span> Max rate: {{ loan.max_interest_rate }}%', content)
    content = re.sub(r'I urgently need funds to buy asthma medicine.*?</div>', '{{ loan.message }}</div>', content)

    # Guarantors
    content = re.sub(
        r'<div class="guarantor-name">Rahim Ali</div>\s*<div class="guarantor-stake">1,500 Tk liability</div>',
        '<div class="guarantor-name">{{ loan.guarantor_1 }}</div><div class="guarantor-stake">{{ (loan.amount / 2) | int }} Tk liability</div>',
        content
    )
    content = re.sub(
        r'<div class="guarantor-name">Sarah Rahman</div>\s*<div class="guarantor-stake">1,500 Tk liability</div>',
        '<div class="guarantor-name">{{ loan.guarantor_2 }}</div><div class="guarantor-stake">{{ (loan.amount / 2) | int }} Tk liability</div>',
        content
    )

    # Lowest bid banner
    content = re.sub(
        r'<div class="bid-banner-rate">2\.8%</div>',
        '<div class="bid-banner-rate">{% if lowest_bid %}{{ lowest_bid.interest_rate }}{% else %}{{ loan.max_interest_rate }}{% endif %}%</div>',
        content
    )
    content = re.sub(
        r'<div class="bid-banner-by">Offered by SJ</div>',
        '<div class="bid-banner-by">Offered by {% if lowest_bid %}{{ lowest_bid.initials }}{% else %}No one yet{% endif %}</div>',
        content
    )
    content = re.sub(
        r'<div class="bid-banner-timer">20:15:09</div>',
        '<div class="bid-banner-timer" id="auction-timer">--:--:--</div>',
        content
    )
    
    # Savings calculator
    content = re.sub(
        r'If accepted now: you pay <strong>3,084 Tk</strong> total \(save 66 Tk vs max rate\)',
        'If accepted now: you pay <strong><span id="calc-total">{{ (loan.amount * (1 + (lowest_bid.interest_rate if lowest_bid else loan.max_interest_rate)/100)) | int }}</span> Tk</strong> total (save <span id="calc-save">{{ (loan.amount * (loan.max_interest_rate - (lowest_bid.interest_rate if lowest_bid else loan.max_interest_rate))/100) | int }}</span> Tk vs max rate)',
        content
    )

    # Bids leaderboard (Find the feed-container and replace its contents)
    feed_replacement = """
            {% for bid in bids %}
            <div class="bid-row" style="display:flex;align-items:center;gap:16px;padding:16px 0;border-bottom:1px solid var(--border);">
              <div class="bid-rank {% if loop.index == 1 %}rank-1{% endif %}" style="font-size:18px;font-weight:800;color:var({% if loop.index == 1 %}--amber{% else %}--text2{% endif %});width:24px;text-align:center;">#{{ loop.index }}</div>
              <span class="av av-sm {{ bid.avatar_class }}">{{ bid.initials }}</span>
              <div style="flex:1;min-width:0;">
                <div style="font-size:14px;font-weight:600;display:flex;align-items:center;gap:6px;">
                  {{ bid.lender_name }}
                  {% if loop.index == 1 %}
                  <span class="pill pill-amber" style="padding:2px 6px;font-size:10px;"><span class="ms ms-16 ms-fill">star</span>Winning</span>
                  {% endif %}
                </div>
                <div style="font-size:13px;color:var(--text2);margin-top:2px;">{{ bid.notes }}</div>
              </div>
              <div style="text-align:right;">
                <div style="font-size:18px;font-weight:800;letter-spacing:-.01em;">{{ bid.interest_rate }}%</div>
                <div style="font-size:11.5px;color:var(--text2);">{{ bid.created_at.strftime('%I:%M %p') if bid.created_at else 'Just now' }}</div>
              </div>
            </div>
            {% else %}
            <div style="padding:24px;text-align:center;color:var(--text2);font-size:14px;">No bids yet. Be the first to offer!</div>
            {% endfor %}
"""
    # Replace contents of <div class="feed-container">
    content = re.sub(r'(<div class="feed-container"[^>]*>).*?(</div>\s*</div>\s*</div>\s*</div>)', r'\1' + feed_replacement + r'\2', content, flags=re.DOTALL)

    # Accept this offer button logic
    accept_btn = """
          {% if bids %}
          <div style="margin-top:20px;padding-top:20px;border-top:1px solid var(--border);">
            <button type="button" class="btn btn-primary btn-block btn-lg" onclick="acceptOffer({{ loan.id }})">
              <span class="ms">handshake</span>Accept Best Offer ({% if lowest_bid %}{{ lowest_bid.interest_rate }}{% else %}{{ loan.max_interest_rate }}{% endif %}%)
            </button>
          </div>
          {% endif %}
"""
    content = re.sub(r'<!-- Accept button \(borrower view\) -->.*?</div>', accept_btn, content, flags=re.DOTALL)

    # Place bid form min/max & JS hooks
    content = re.sub(r'<input type="number" class="input" value="2\.7" step="0\.1" />', '<input type="number" id="bid-rate" class="input" value="{{ (lowest_bid.interest_rate - 0.1) if lowest_bid else (loan.max_interest_rate - 0.1) }}" step="0.1" min="0.5" max="{{ loan.max_interest_rate }}" />', content)
    content = re.sub(r'<textarea class="input" placeholder="e\.g\., Can send via Nagad immediately"></textarea>', '<textarea id="bid-notes" class="input" placeholder="e.g., Can send via Nagad immediately"></textarea>', content)
    content = re.sub(r'<button type="button" class="btn btn-primary btn-block">.*?Place Bid.*?</button>', '<button type="button" class="btn btn-primary btn-block" onclick="placeBid({{ loan.id }})"><span class="ms">gavel</span>Place Bid</button>', content, flags=re.DOTALL)

    # Javascript for Timer, Place Bid, Accept Offer
    js_addition = """
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
    // Client-side validation: must be lower than lowest bid
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
        setTimeout(() => location.reload(), 1000); // Reload to fetch latest bids
      }
    } catch(e) {
      showToast('Error placing bid.', 'error');
    }
  }

  async function acceptOffer(loanId) {
    try {
      const res = await fetch(`/api/auction/${loanId}/accept`, { method: 'POST' });
      const data = await res.json();
      if(data.status === 'success') {
        showToast('Offer accepted!');
        setTimeout(() => window.location.href = '/repayment', 1000);
      }
    } catch(e) {
      showToast('Error accepting offer.', 'error');
    }
  }

  // Simulate real-time updates every 15s
  setInterval(() => {
    // location.reload();
  }, 15000);
</script>
"""
    content = re.sub(r'</body>', js_addition + '\n</body>', content)

    with open('templates/reverse_auction.html', 'w', encoding='utf-8') as f:
        f.write(content)

def rewrite_repayment():
    with open('templates/loan_repayment.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Loan amounts
    content = re.sub(r'<div class="m-value">3,000<span class="m-sub">Tk</span></div>', '<div class="m-value">{{ loan.total_due | int }}<span class="m-sub">Tk</span></div>', content)
    content = re.sub(r'<div class="m-value" style="color:var\(--emerald\);">2,448<span class="m-sub" style="color:inherit">Tk</span></div>', '<div class="m-value" style="color:var(--emerald);">{{ loan.total_repaid | int }}<span class="m-sub" style="color:inherit">Tk</span></div>', content)
    content = re.sub(r'<div class="m-value" style="color:var\(--amber\);">552<span class="m-sub" style="color:inherit">Tk</span></div>', '<div class="m-value" style="color:var(--amber);">{{ (loan.total_due - loan.total_repaid) | int }}<span class="m-sub" style="color:inherit">Tk</span></div>', content)

    # Progress bar width
    content = re.sub(r'<i style="width:81\.6%"></i>', '<i style="width:{{ (loan.total_repaid / loan.total_due * 100) | int }}%"></i>', content)
    
    # Days remaining and urgency color
    # Amber/crimson class dynamic based on days_remaining
    content = re.sub(r'<div class="m-value" style="color:var\(--crimson\);">3<span class="m-sub" style="color:inherit">Days</span></div>', '<div class="m-value" style="color:var(--{% if loan.days_remaining <= 3 %}crimson{% else %}amber{% endif %});">{{ loan.days_remaining }}<span class="m-sub" style="color:inherit">Days</span></div>', content)

    # Lender profile
    content = re.sub(r'<span class="av av-lg av-4">KH</span>', '<span class="av av-lg {% if lender %}{{ lender.avatar_class }}{% else %}av-4{% endif %}">{% if lender %}{{ lender.initials }}{% else %}KH{% endif %}</span>', content)
    content = re.sub(r'<div class="borrower-name">Karim Hossain</div>', '<div class="borrower-name">{% if lender %}{{ lender.name }}{% else %}Karim Hossain{% endif %}</div>', content)
    content = re.sub(r'<span class="trust-mini" style="background:var\(--navy\)">91</span>', '<span class="trust-mini" style="background:var(--navy)">{% if lender %}{{ lender.trust_score }}{% else %}91{% endif %}</span>', content)
    
    # Loan terms display
    content = re.sub(r'<span class="ms">money</span> 3,000 Tk @ 2\.8% interest', '<span class="ms">money</span> {{ loan.amount | int }} Tk @ {{ loan.current_interest_rate }}% interest', content)
    content = re.sub(r'<span class="ms">group</span> Guarantors: Rahim Ali &amp; Sarah Rahman', '<span class="ms">group</span> Guarantors: {{ loan.guarantor_1 }} &amp; {{ loan.guarantor_2 }}', content)
    content = re.sub(r'Due date: <strong style="color:var\(--crimson\);">Sep 5, 2026</strong>', 'Due date: <strong style="color:var(--crimson);">{{ loan.due_date }}</strong>', content)

    # Make the steps dynamic based on loan.days_remaining
    content = re.sub(
        r'<div class="step done">\s*<div class="step-dot"><span class="ms">check</span></div>\s*<b>On time</b>\s*<small>All good</small>\s*</div>',
        '<div class="step {% if loan.days_remaining > 5 %}current{% elif loan.days_remaining > 0 %}done{% else %}done{% endif %}"><div class="step-dot"><span class="ms">check</span></div><b>On time</b><small>All good</small></div>',
        content
    )
    content = re.sub(
        r'<div class="step current">\s*<div class="step-dot"><span class="ms">priority_high</span></div>\s*<b>Grace period</b>\s*<small>3 days left</small>\s*</div>',
        '<div class="step {% if loan.days_remaining <= 5 and loan.days_remaining > 0 %}current{% elif loan.days_remaining <= 0 %}done{% endif %}"><div class="step-dot"><span class="ms">priority_high</span></div><b>Grace period</b><small>{{ loan.days_remaining }} days left</small></div>',
        content
    )

    # Make the input fields dynamic
    content = re.sub(
        r'<input type="number" class="input" value="552" />',
        '<input type="number" id="repay-amount" class="input" value="{{ (loan.total_due - loan.total_repaid) | int }}" />',
        content
    )

    # Interactive JS for payment method selection, pay button, extend button
    js_addition = """
<div id="toast-container" style="position:fixed;bottom:24px;right:24px;display:flex;flex-direction:column;gap:10px;z-index:9999;"></div>
<div id="success-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:10000;align-items:center;justify-content:center;">
    <div style="background:#fff;padding:32px;border-radius:12px;text-align:center;max-width:400px;width:100%;">
        <div style="font-size:48px;margin-bottom:16px;">🎉</div>
        <h2 style="font-size:24px;margin-bottom:8px;">Payment Successful!</h2>
        <p style="color:var(--text2);margin-bottom:16px;">Trx ID: <span id="modal-trx-id" style="font-weight:700;"></span></p>
        <div style="background:var(--emerald);color:#fff;padding:12px;border-radius:8px;margin-bottom:24px;font-weight:600;">
            Trust Score +2! New Score: <span id="modal-trust-score"></span>
        </div>
        <button class="btn btn-primary btn-block" onclick="location.reload()">Close & Reload</button>
    </div>
</div>
<script>
  let selectedMethod = 'bKash';
  
  // Wire up payment method chips
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

  // Inject confetti library (lightweight)
  const script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js';
  document.head.appendChild(script);

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
      }
    } catch(e) {
      showToast('Error processing payment.', 'error');
      btn.disabled = false;
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

  // Animation for spinner
  const style = document.createElement('style');
  style.innerHTML = `@keyframes spin { 100% { transform: rotate(360deg); } }`;
  document.head.appendChild(style);
</script>
"""
    content = re.sub(r'<button type="button" class="btn btn-primary btn-block btn-lg">.*?Pay 552 Tk via bKash.*?</button>', '<button type="button" id="pay-btn" class="btn btn-primary btn-block btn-lg" onclick="repayLoan({{ loan.id }})"><span class="ms">lock</span><span id="pay-btn-text">Pay via bKash</span></button>', content, flags=re.DOTALL)
    content = re.sub(r'<button type="button" class="btn btn-secondary btn-block">.*?Request 7-day extension.*?</button>', '<button type="button" id="extend-btn" class="btn btn-secondary btn-block" onclick="extendLoan({{ loan.id }})"><span class="ms">update</span>Request 7-day extension</button>', content, flags=re.DOTALL)

    content = re.sub(r'</body>', js_addition + '\n</body>', content)

    with open('templates/loan_repayment.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    rewrite_auction()
    rewrite_repayment()
