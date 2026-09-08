import urllib.request
import re

with open('d:/uiuCrowdFunding/templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

styles = re.findall(r'<style>.*?</style>', html, flags=re.DOTALL)
css = '\n'.join(styles)

meal_drops_html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>UIU Aid — Meal Drops</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
__CSS__
<style>
/* Additional Custom CSS for the rewrite */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.6); z-index: 999;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; pointer-events: none; transition: opacity 0.2s;
}
.modal-overlay.active {
  opacity: 1; pointer-events: auto;
}
.modal-content {
  background: #fff; border-radius: 12px; padding: 32px;
  width: 90%; max-width: 400px; text-align: center;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  transform: translateY(20px); transition: transform 0.2s;
}
.modal-overlay.active .modal-content {
  transform: translateY(0);
}
.modal-close {
  margin-top: 24px;
}
.step-item {
  display: flex; flex-direction: column; align-items: center; text-align: center; gap: 8px; flex: 1;
}
.step-item .step-icon {
  width: 48px; height: 48px; border-radius: 50%; background: rgba(30,58,138,0.1); color: var(--navy);
  display: flex; align-items: center; justify-content: center;
}
.step-item .step-icon .ms { font-size: 24px; }
.step-arrow { color: var(--text2); display: flex; align-items: center; padding: 0 16px; margin-top: 12px; }

.feed-list { display: flex; flex-direction: column; gap: 12px; }
.feed-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px; border: 1px solid var(--border); border-radius: var(--r);
  background: var(--surface); animation: fadeInDown 0.4s ease;
}
@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Toast notifications */
.toast-container {
  position: fixed; bottom: 24px; right: 24px; display: flex; flex-direction: column; gap: 12px; z-index: 10000;
}
.toast {
  background: #1E3A8A; color: #fff; padding: 12px 20px; border-radius: 8px; font-size: 14.5px; font-weight: 500; display: flex; align-items: center; gap: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  animation: slideInUp 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
@keyframes slideInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

</style>
</head>
<body>
<div class="app">
  <!-- SIDEBAR -->
  <aside class="sidebar">
    <div class="logo">UIU Aid<small>Mutual Aid Network</small></div>
    <nav class="nav">
      <a class="nav-item {% if active_page == 'dashboard' %}active{% endif %}" href="/"><span class="ms">space_dashboard</span>Dashboard</a>
      <a class="nav-item {% if active_page == 'loans' %}active{% endif %}" href="/loan-request"><span class="ms">handshake</span>Loans</a>
      <a class="nav-item {% if active_page == 'crowdfunding' %}active{% endif %}" href="/crowdfunding"><span class="ms">volunteer_activism</span>Crowdfunding</a>
      <a class="nav-item {% if active_page == 'gigs' %}active{% endif %}" href="/gigs"><span class="ms">work</span>Gig Board</a>
      <a class="nav-item {% if active_page == 'meals' %}active{% endif %}" href="/meal-drops"><span class="ms">restaurant</span>Meal Drops</a>
      <a class="nav-item {% if active_page == 'trust' %}active{% endif %}" href="/trust-profile"><span class="ms">verified_user</span>Trust Profile</a>
    </nav>
    <div class="side-user">
      <span class="av av-1">NJ</span>
      <div><b>Nusrat Jahan</b><span class="vrf"><span class="ms">verified</span>Verified</span></div>
    </div>
  </aside>

  <main class="main">
    <div class="meal-container">

      <!-- PAGE HEADER -->
      <div class="meal-page-head" style="display:flex; justify-content:space-between; margin-bottom:32px;">
        <div>
          <h1>Meal Drops</h1>
          <div class="sub">A meal from a classmate you'll never meet.</div>
        </div>
        <div class="head-actions">
          <div class="banner banner-emerald" style="background: rgba(16,185,129,0.1); border-radius: 99px; padding: 8px 16px;">
            <span class="ms" style="color: #059669; font-size: 18px;">lock</span>
            <strong style="color: #065F46; font-size: 13.5px;">Fully Anonymous — donor & recipient identities never revealed</strong>
          </div>
        </div>
      </div>

      <!-- HOW IT WORKS -->
      <div class="card" style="margin-bottom: 24px; background: #F8FAFC;">
        <div style="display: flex; justify-content: space-between;">
          <div class="step-item">
            <div class="step-icon"><span class="ms">volunteer_activism</span></div>
            <div style="font-weight: 600; margin-top: 12px; font-size: 14.5px;">1. Gift</div>
            <div style="font-size: 13px; color: var(--text2);">Pay for a 120 Tk meal token</div>
          </div>
          <div class="step-arrow"><span class="ms">arrow_forward</span></div>
          <div class="step-item">
            <div class="step-icon"><span class="ms">water_drop</span></div>
            <div style="font-weight: 600; margin-top: 12px; font-size: 14.5px;">2. Pool</div>
            <div style="font-size: 13px; color: var(--text2);">Token goes to the community pool</div>
          </div>
          <div class="step-arrow"><span class="ms">arrow_forward</span></div>
          <div class="step-item">
            <div class="step-icon"><span class="ms">restaurant</span></div>
            <div style="font-weight: 600; margin-top: 12px; font-size: 14.5px;">3. Claim</div>
            <div style="font-size: 13px; color: var(--text2);">A student in need generates a QR code</div>
          </div>
        </div>
      </div>

      <!-- STAT STRIP -->
      <div style="display: flex; align-items: center; gap: 0; background: var(--surface); border: 1px solid var(--border); border-radius: var(--r); box-shadow: var(--shadow); padding: 20px 28px; margin-bottom: 28px;">
        <div style="display: flex; flex-direction: column; gap: 3px; padding-right: 36px;">
          <div class="stat-num" id="stat-available" style="font-size: 26px; font-weight: 800; font-variant-numeric: tabular-nums;">{{ total_available }}</div>
          <div class="stat-label" style="font-size: 13px; color: var(--text2); font-weight: 500;">meals available right now</div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 3px; padding-left: 36px; padding-right: 36px; border-left: 1px solid var(--border);">
          <div class="stat-num" id="stat-shared" style="font-size: 26px; font-weight: 800; font-variant-numeric: tabular-nums;">{{ total_shared }}</div>
          <div class="stat-label" style="font-size: 13px; color: var(--text2); font-weight: 500;">total meals shared</div>
        </div>
        <div style="margin-left: auto;">
          <span class="pill pill-emerald">
            <span class="ms ms-fill dot-live" style="font-size:10px;color:#059669;margin-right: 6px;"></span>
            Live updates
          </span>
        </div>
      </div>

      <!-- TWO-CARD GRID -->
      <div class="grid-2" style="margin-bottom: 24px;">

        <!-- LEFT: Gift Meals -->
        <div class="card meal-card" style="padding:32px;">
          <div class="card-title">
            <span class="ms" style="color:#059669">favorite</span>
            Gift Meals Anonymously
          </div>
          <p style="font-size: 15px; color: var(--text2); line-height: 1.65; margin-bottom: 24px;">Gift meal credits to students who need one. You will never know who claims it.</p>

          <div style="font-size: 12px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--text2); margin-bottom: 10px;">Number of meals</div>
          <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 0;">
              <button style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border: 1px solid #C7D2E5; background: var(--surface); color: var(--navy); font-size: 20px; font-weight: 600; cursor: pointer; border-radius: var(--r) 0 0 var(--r); border-right: none;" onclick="changeQty(-1)">&minus;</button>
              <div id="gift-qty" style="width: 48px; height: 40px; display: flex; align-items: center; justify-content: center; border: 1px solid #C7D2E5; font-size: 17px; font-weight: 700; color: var(--text); background: var(--surface);">1</div>
              <button style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border: 1px solid #C7D2E5; background: var(--surface); color: var(--navy); font-size: 20px; font-weight: 600; cursor: pointer; border-radius: 0 var(--r) var(--r) 0; border-left: none;" onclick="changeQty(1)">+</button>
            </div>
            <div class="chips">
              <span class="chip" onclick="setQty(2)">2 meals</span>
              <span class="chip" onclick="setQty(5)">5 meals</span>
            </div>
          </div>

          <hr class="divider">

          <div style="display: flex; align-items: baseline; justify-content: space-between; padding: 4px 0;">
            <span style="font-size: 14px; color: var(--text2); font-weight: 500;">Total</span>
            <span id="gift-total" class="money" style="font-size: 28px; font-weight: 800; font-variant-numeric: tabular-nums; color: var(--text); letter-spacing: -.02em;">120 Tk</span>
          </div>

          <hr class="divider" style="margin-top:16px">

          <button id="btn-gift-meal" type="button" class="btn btn-primary btn-block btn-lg" onclick="giftMeal()">Gift 1 Meal (120 Tk)</button>
        </div>

        <!-- RIGHT: Claim a Meal -->
        <div class="card meal-card" style="display:flex;flex-direction:column;align-items:center;text-align:center; padding:32px;">
          <div class="card-title" style="width:100%;justify-content:center">
            <span class="ms">qr_code_2</span>
            Claim an Anonymous Meal Token
          </div>
          <p style="font-size: 15px; color: var(--text2); line-height: 1.65; margin-bottom: 24px; max-width:340px">If you're hungry today, eat today. Generate a secret token for the cafeteria. No names, no questions.</p>
          
          <button id="btn-claim-meal" type="button" class="btn btn-secondary btn-block btn-lg" style="margin-top:auto;" onclick="claimMeal()">
            <span class="ms ms-18">qr_code</span> Claim an Anonymous Meal Token
          </button>
        </div>
      </div>

      <!-- BOTTOM ROW -->
      <div class="grid-2">
        <!-- Recent Drops Feed -->
        <div class="card">
          <div class="card-title"><span class="ms">history</span> Recent Meal Drops</div>
          <div class="feed-list" id="drops-feed">
            {% for drop in recent_drops %}
            <div class="feed-item">
              <div style="display:flex; align-items:center; gap: 12px;">
                <div class="av av-2" style="background: var(--text2);"><span class="ms">person</span></div>
                <div>
                  <div style="font-weight: 600; font-size: 14.5px;">Anonymous Classmate</div>
                  <div style="font-size: 12.5px; color: var(--text2);">Gifted {{ drop.meals_count }} meal{% if drop.meals_count > 1 %}s{% endif %}</div>
                </div>
              </div>
              {% if drop.status == 'available' %}
                <span class="pill pill-emerald">Available</span>
              {% else %}
                <span class="pill pill-slate">Claimed</span>
              {% endif %}
            </div>
            {% endfor %}
          </div>
        </div>

        <!-- Privacy Commitment -->
        <div class="card" style="background: var(--navy); color: #fff;">
          <div class="card-title" style="color: #fff;"><span class="ms" style="color: #60A5FA;">shield</span> Privacy Commitment</div>
          <p style="font-size: 14.5px; line-height: 1.6; color: rgba(255,255,255,0.85); margin-bottom: 16px;">
            The UIU Mutual Aid Meal Drop system is strictly blind. We employ mathematical unlinking between the donor's payment ID and the generated meal token.
          </p>
          <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 12px; font-size: 14px;">
            <li style="display: flex; gap: 10px; align-items: flex-start;">
              <span class="ms" style="color: #6EE7B7; font-size: 18px;">check_circle</span>
              Donors cannot see who claims their meals.
            </li>
            <li style="display: flex; gap: 10px; align-items: flex-start;">
              <span class="ms" style="color: #6EE7B7; font-size: 18px;">check_circle</span>
              Recipients only see "Anonymous Classmate".
            </li>
            <li style="display: flex; gap: 10px; align-items: flex-start;">
              <span class="ms" style="color: #6EE7B7; font-size: 18px;">check_circle</span>
              Cafeteria staff only scan the QR code and see no names.
            </li>
          </ul>
        </div>
      </div>

    </div>
  </main>
</div>

<!-- Modal for Claim/Gift Success -->
<div class="modal-overlay" id="success-modal">
  <div class="modal-content">
    <div style="width: 64px; height: 64px; background: rgba(16,185,129,0.1); color: var(--emerald); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px;">
      <span class="ms" style="font-size: 32px;" id="modal-icon">check_circle</span>
    </div>
    <h3 style="font-size: 20px; font-weight: 700; margin-bottom: 8px;" id="modal-title">Success!</h3>
    <p style="font-size: 14.5px; color: var(--text2); margin-bottom: 24px;" id="modal-desc">Details here.</p>
    
    <div id="modal-qr-section" style="display: none; margin-bottom: 24px;">
      <div style="border: 2px dashed var(--border); padding: 16px; display: inline-block; border-radius: 8px;">
        <!-- SVG QR code placeholder -->
        <svg width="120" height="120" viewBox="0 0 100 100"><rect width="100" height="100" fill="#fff"/><rect x="10" y="10" width="30" height="30" fill="#0F172A"/><rect x="15" y="15" width="20" height="20" fill="#fff"/><rect x="20" y="20" width="10" height="10" fill="#0F172A"/><rect x="60" y="10" width="30" height="30" fill="#0F172A"/><rect x="65" y="15" width="20" height="20" fill="#fff"/><rect x="70" y="20" width="10" height="10" fill="#0F172A"/><rect x="10" y="60" width="30" height="30" fill="#0F172A"/><rect x="15" y="65" width="20" height="20" fill="#fff"/><rect x="20" y="70" width="10" height="10" fill="#0F172A"/><rect x="50" y="50" width="10" height="10" fill="#0F172A"/><rect x="70" y="60" width="20" height="20" fill="#0F172A"/><rect x="60" y="80" width="30" height="10" fill="#0F172A"/></svg>
      </div>
      <div id="modal-code" style="font-size: 24px; font-weight: 800; font-variant-numeric: tabular-nums; letter-spacing: 2px; margin-top: 12px;"></div>
      <div style="font-size: 12.5px; color: var(--text2); margin-top: 8px; font-weight: 600;">Show this code at UIU cafeteria counter</div>
    </div>

    <button class="btn btn-secondary btn-block modal-close" onclick="closeModal()">Done</button>
  </div>
</div>

<div class="toast-container" id="toast-container"></div>

<script>
let qty = 1;
const maxQty = 10;
const minQty = 1;

function updateQtyUI() {
  document.getElementById('gift-qty').textContent = qty;
  document.getElementById('gift-total').textContent = (qty * 120) + ' Tk';
  document.getElementById('btn-gift-meal').textContent = `Gift ${qty} Meal${qty>1?'s':''} (${qty * 120} Tk)`;
}
function changeQty(delta) {
  qty = Math.max(minQty, Math.min(maxQty, qty + delta));
  updateQtyUI();
}
function setQty(val) {
  qty = val;
  updateQtyUI();
}

function showToast(msg) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<span class="ms">notifications</span> ${msg}`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(20px)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function showModal(title, desc, code = null, isClaim = false) {
  document.getElementById('modal-title').textContent = title;
  document.getElementById('modal-desc').textContent = desc;
  document.getElementById('modal-icon').textContent = isClaim ? 'qr_code' : 'favorite';
  const qrSec = document.getElementById('modal-qr-section');
  if (code) {
    qrSec.style.display = 'block';
    document.getElementById('modal-code').textContent = code;
  } else {
    qrSec.style.display = 'none';
  }
  document.getElementById('success-modal').classList.add('active');
}

function closeModal() {
  document.getElementById('success-modal').classList.remove('active');
}

function animateNumber(id, newVal) {
  const el = document.getElementById(id);
  if (!el) return;
  const oldVal = parseInt(el.textContent || '0', 10);
  if (oldVal === newVal) return;
  el.style.transform = 'scale(1.2)';
  el.style.color = 'var(--emerald)';
  el.textContent = newVal;
  setTimeout(() => {
    el.style.transform = 'scale(1)';
    el.style.color = '';
  }, 300);
}

function giftMeal() {
  fetch('/api/meals/gift', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({meals_count: qty, donor_id: 1})
  })
  .then(res => res.json())
  .then(data => {
    if(data.status === 'success') {
      showModal('Meals Gifted', `You have successfully gifted ${qty} meal${qty>1?'s':''} to the community pool.`);
      showToast('Meals gifted successfully!');
      const availEl = document.getElementById('stat-available');
      const sharedEl = document.getElementById('stat-shared');
      animateNumber('stat-available', parseInt(availEl.textContent) + qty);
      animateNumber('stat-shared', parseInt(sharedEl.textContent) + qty);
      
      const feed = document.getElementById('drops-feed');
      if (feed) {
        const item = document.createElement('div');
        item.className = 'feed-item';
        item.innerHTML = `
          <div style="display:flex; align-items:center; gap: 12px;">
            <div class="av av-2" style="background: var(--text2);"><span class="ms">person</span></div>
            <div>
              <div style="font-weight: 600; font-size: 14.5px;">Anonymous Classmate</div>
              <div style="font-size: 12.5px; color: var(--text2);">Gifted ${qty} meal${qty>1?'s':''}</div>
            </div>
          </div>
          <span class="pill pill-emerald">Available</span>
        `;
        feed.insertBefore(item, feed.firstChild);
        if (feed.children.length > 10) feed.removeChild(feed.lastChild);
      }
    }
  });
}

function claimMeal() {
  fetch('/api/meals/claim', {method: 'POST'})
  .then(res => res.json())
  .then(data => {
    if(data.status === 'success') {
      showModal('Meal Token Generated', 'Present this anonymous token at the cafeteria counter.', data.claim_code, true);
      showToast('Meal claimed successfully!');
      const availEl = document.getElementById('stat-available');
      if (availEl) {
        let current = parseInt(availEl.textContent);
        if(current > 0) animateNumber('stat-available', current - 1);
      }
    }
  });
}
</script>
</body>
</html>
"""

trust_profile_html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>UIU Aid — Trust Profile</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
__CSS__
<style>
/* Tier colors */
.tier-slate { color: #475569; }
.tier-bronze { color: #B45309; }
.tier-silver { color: #94A3B8; }
.tier-gold { color: #D97706; }
.tier-platinum { color: #6366F1; }

.badge-card { display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; border: 1px solid var(--border); border-radius: 99px; background: #fff; font-size: 13.5px; font-weight: 600; }
.badge-card .ms { font-size: 20px; }

.breakdown-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.breakdown-label { width: 140px; font-size: 13.5px; font-weight: 500; color: var(--text2); }
.breakdown-bg { flex: 1; height: 10px; background: var(--border); border-radius: 5px; overflow: hidden; }
.breakdown-fill { height: 100%; border-radius: 5px; background: var(--emerald); }
.breakdown-val { width: 40px; font-size: 13.5px; font-weight: 600; text-align: right; }

.tier-progress-track { display: flex; gap: 2px; margin-top: 24px; }
.tier-segment { flex: 1; text-align: center; font-size: 11px; font-weight: 700; color: var(--text2); padding: 6px 0; border-top: 4px solid var(--border); }
.tier-segment.active { border-top-color: var(--emerald); color: var(--emerald); }
.tier-segment.past { border-top-color: var(--emerald); }

/* Profile Header */
.profile-header { display: flex; gap: 24px; align-items: center; padding: 32px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--r); box-shadow: var(--shadow); margin-bottom: 24px; }
.profile-av { width: 88px; height: 88px; font-size: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 700; }
.profile-info h1 { font-size: 28px; font-weight: 800; margin-bottom: 4px; display: flex; align-items: center; gap: 8px; }
.profile-meta { font-size: 15px; color: var(--text2); display: flex; gap: 16px; align-items: center; }

/* Modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.6); z-index: 999;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; pointer-events: none; transition: opacity 0.2s;
}
.modal-overlay.active { opacity: 1; pointer-events: auto; }
.modal-content {
  background: #fff; border-radius: 12px; padding: 32px;
  width: 90%; max-width: 400px; text-align: center;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  transform: translateY(20px); transition: transform 0.2s;
}
.modal-overlay.active .modal-content { transform: translateY(0); }

/* Toast notifications */
.toast-container { position: fixed; bottom: 24px; right: 24px; display: flex; flex-direction: column; gap: 12px; z-index: 10000; }
.toast { background: #1E3A8A; color: #fff; padding: 12px 20px; border-radius: 8px; font-size: 14.5px; font-weight: 500; display: flex; align-items: center; gap: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); animation: slideInUp 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
@keyframes slideInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

/* Trust Events */
.trust-event { display: flex; gap: 16px; padding: 16px 0; border-bottom: 1px solid var(--border); }
.trust-event:last-child { border-bottom: none; padding-bottom: 0; }
.trust-event-icon { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex: none; }
.trust-event-icon.emerald { background: rgba(16,185,129,0.1); color: var(--emerald); }
.trust-event-icon.crimson { background: rgba(239,68,68,0.1); color: var(--crimson); }
.trust-event-icon.navy { background: rgba(30,58,138,0.1); color: var(--navy); }
.trust-event-details { flex: 1; }
.trust-event-title { font-size: 15px; font-weight: 600; }
.trust-event-meta { font-size: 13px; color: var(--text2); margin-top: 4px; }
.trust-event-points { font-size: 16px; font-weight: 700; font-variant-numeric: tabular-nums; }
.trust-event-points.pos { color: var(--emerald); }
.trust-event-points.neg { color: var(--crimson); }
</style>
</head>
<body>

{% set points_repayment = 0 %}
{% set points_gig = 0 %}
{% set points_giveback = 0 %}
{% set points_vouch = 0 %}
{% set has_loan_repaid = false %}
{% set has_meal_drop = false %}

{% for ev in events %}
  {% if ev.event_type == 'loan_repaid' %}
    {% set points_repayment = points_repayment + ev.points_delta %}
    {% set has_loan_repaid = true %}
  {% elif ev.event_type == 'gig_completed' %}
    {% set points_gig = points_gig + ev.points_delta %}
  {% elif ev.event_type == 'meal_drop' %}
    {% set points_giveback = points_giveback + ev.points_delta %}
    {% set has_meal_drop = true %}
  {% elif ev.event_type == 'vouch_received' %}
    {% set points_vouch = points_vouch + ev.points_delta %}
  {% endif %}
{% endfor %}

{% set total_calculated_points = points_repayment + points_gig + points_giveback + points_vouch %}
{% if total_calculated_points == 0 %}{% set total_calculated_points = 1 %}{% endif %}

<div class="app">
  <aside class="sidebar">
    <div class="logo">UIU Aid<small>Mutual Aid Network</small></div>
    <nav class="nav">
      <a class="nav-item {% if active_page == 'dashboard' %}active{% endif %}" href="/"><span class="ms">space_dashboard</span>Dashboard</a>
      <a class="nav-item {% if active_page == 'loans' %}active{% endif %}" href="/loan-request"><span class="ms">handshake</span>Loans</a>
      <a class="nav-item {% if active_page == 'crowdfunding' %}active{% endif %}" href="/crowdfunding"><span class="ms">volunteer_activism</span>Crowdfunding</a>
      <a class="nav-item {% if active_page == 'gigs' %}active{% endif %}" href="/gigs"><span class="ms">work</span>Gig Board</a>
      <a class="nav-item {% if active_page == 'meals' %}active{% endif %}" href="/meal-drops"><span class="ms">restaurant</span>Meal Drops</a>
      <a class="nav-item {% if active_page == 'trust' %}active{% endif %}" href="/trust-profile"><span class="ms">verified_user</span>Trust Profile</a>
    </nav>
    <div class="side-user">
      <span class="av {{ user.avatar_class }}">{{ user.initials }}</span>
      <div><b>{{ user.name }}</b>
      {% if user.is_verified %}<span class="vrf"><span class="ms">verified</span>Verified</span>{% endif %}
      </div>
    </div>
  </aside>

  <main class="main">
    <!-- Profile Header -->
    <div class="profile-header">
      <div class="profile-av {{ user.avatar_class }}">{{ user.initials }}</div>
      <div class="profile-info">
        <h1>{{ user.name }} {% if user.is_verified %}<span class="ms" style="color: #10B981; font-size: 28px; font-variation-settings:'FILL' 1;">verified</span>{% endif %}</h1>
        <div class="profile-meta">
          <span><span class="ms ms-18" style="vertical-align: text-bottom;">badge</span> {{ user.student_id }}</span>
          <span>&middot;</span>
          <span><span class="ms ms-18" style="vertical-align: text-bottom;">school</span> {{ user.department }}</span>
          <span>&middot;</span>
          <span><span class="ms ms-18" style="vertical-align: text-bottom;">calendar_month</span> {{ user.trimester }}</span>
        </div>
        <div style="margin-top: 16px; display: flex; gap: 12px;">
          <button class="btn btn-secondary btn-sm" onclick="shareProfile()"><span class="ms ms-16">share</span> Share Profile</button>
          <button class="btn btn-quiet btn-sm" onclick="requestVouch()"><span class="ms ms-16">handshake</span> Request Vouch</button>
        </div>
      </div>
    </div>

    <div class="grid-2">
      
      <!-- Trust Score Card -->
      <div class="card">
        <div class="card-title"><span class="ms">verified_user</span> Trust Score</div>
        <div style="display: flex; gap: 32px; align-items: center;">
          <!-- Circular Gauge -->
          {% set offset = 326.7 * (1 - user.trust_score / 100) %}
          <svg width="140" height="140" viewBox="0 0 120 120" aria-label="Trust score {{ user.trust_score }} out of 100">
            <circle cx="60" cy="60" r="52" fill="none" stroke="#E2E8F0" stroke-width="12"/>
            <circle cx="60" cy="60" r="52" fill="none" stroke="#10B981" stroke-width="12"
              stroke-linecap="round" stroke-dasharray="326.7" stroke-dashoffset="{{ offset }}"
              transform="rotate(-90 60 60)" style="transition: stroke-dashoffset 1s ease-out;"/>
            <text x="60" y="58" text-anchor="middle" font-size="32" font-weight="800" fill="#0F172A" font-family="Inter">{{ user.trust_score }}</text>
            <text x="60" y="76" text-anchor="middle" font-size="13" fill="#64748B" font-family="Inter">/100</text>
          </svg>
          
          <div style="flex: 1;">
            {% set tier_color_class = 'tier-slate' %}
            {% if user.tier == 'Bronze' %}{% set tier_color_class = 'tier-bronze' %}{% endif %}
            {% if user.tier == 'Silver' %}{% set tier_color_class = 'tier-silver' %}{% endif %}
            {% if user.tier == 'Gold' %}{% set tier_color_class = 'tier-gold' %}{% endif %}
            {% if user.tier == 'Platinum' %}{% set tier_color_class = 'tier-platinum' %}{% endif %}
            <div style="font-size: 20px; font-weight: 800;" class="{{ tier_color_class }}">{{ user.tier }} Tier</div>
            <div style="font-size: 13.5px; color: var(--text2); margin-top: 4px;">
              {% if user.trust_score < 20 %} {{ 20 - user.trust_score }} points to Bronze {% endif %}
              {% if user.trust_score >= 20 and user.trust_score < 40 %} {{ 40 - user.trust_score }} points to Silver {% endif %}
              {% if user.trust_score >= 40 and user.trust_score < 60 %} {{ 60 - user.trust_score }} points to Gold {% endif %}
              {% if user.trust_score >= 60 and user.trust_score < 90 %} {{ 90 - user.trust_score }} points to Platinum {% endif %}
              {% if user.trust_score >= 90 %} Max Tier reached! {% endif %}
            </div>
            
            <div class="tier-progress-track">
              <div class="tier-segment {% if user.trust_score >= 20 %}past{% elif user.trust_score >= 0 %}active{% endif %}">New</div>
              <div class="tier-segment {% if user.trust_score >= 40 %}past{% elif user.trust_score >= 20 %}active{% endif %}">Brz</div>
              <div class="tier-segment {% if user.trust_score >= 60 %}past{% elif user.trust_score >= 40 %}active{% endif %}">Slv</div>
              <div class="tier-segment {% if user.trust_score >= 90 %}past{% elif user.trust_score >= 60 %}active{% endif %}">Gld</div>
              <div class="tier-segment {% if user.trust_score >= 90 %}active{% endif %}">Plt</div>
            </div>
          </div>
        </div>
        
        <hr class="divider">
        
        <div style="font-size: 12px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--text2); margin-bottom: 10px;">Trust Score Breakdown</div>
        <div class="breakdown-bar">
          <div class="breakdown-label">Repayment History</div>
          <div class="breakdown-bg"><div class="breakdown-fill" style="width: {{ (points_repayment/total_calculated_points)*100 }}%;"></div></div>
          <div class="breakdown-val">{{ points_repayment }}</div>
        </div>
        <div class="breakdown-bar">
          <div class="breakdown-label">Gig Completion</div>
          <div class="breakdown-bg"><div class="breakdown-fill" style="width: {{ (points_gig/total_calculated_points)*100 }}%;"></div></div>
          <div class="breakdown-val">{{ points_gig }}</div>
        </div>
        <div class="breakdown-bar">
          <div class="breakdown-label">Community Giveback</div>
          <div class="breakdown-bg"><div class="breakdown-fill" style="width: {{ (points_giveback/total_calculated_points)*100 }}%;"></div></div>
          <div class="breakdown-val">{{ points_giveback }}</div>
        </div>
        <div class="breakdown-bar">
          <div class="breakdown-label">Vouch Network</div>
          <div class="breakdown-bg"><div class="breakdown-fill" style="width: {{ (points_vouch/total_calculated_points)*100 }}%;"></div></div>
          <div class="breakdown-val">{{ points_vouch }}</div>
        </div>
      </div>

      <div class="stack">
        <!-- Financial Snapshot -->
        <div class="card">
          <div class="card-title"><span class="ms">account_balance</span> Financial Snapshot</div>
          <div class="grid-3">
            <div>
              <div style="font-size: 13px; color: var(--text2); font-weight: 500;">Borrowing Limit</div>
              <div class="money" style="font-size: 22px; font-weight: 800; margin-top: 4px;">{{ user.borrowing_limit }} Tk</div>
            </div>
            <div>
              <div style="font-size: 13px; color: var(--text2); font-weight: 500;">Amount Borrowed</div>
              <div class="money" style="font-size: 22px; font-weight: 800; margin-top: 4px;">{{ user.borrowed_amount }} Tk</div>
            </div>
            <div>
              <div style="font-size: 13px; color: var(--text2); font-weight: 500;">Amount Lent</div>
              <div class="money" style="font-size: 22px; font-weight: 800; color: var(--emerald); margin-top: 4px;">{{ user.lent_amount }} Tk</div>
            </div>
          </div>
        </div>

        <!-- Earned Badges -->
        <div class="card">
          <div class="card-title"><span class="ms">workspace_premium</span> Earned Badges</div>
          <div style="display: flex; gap: 12px; flex-wrap: wrap;">
            {% if user.is_verified %}
            <div class="badge-card" style="border-color: #10B981; background: rgba(16,185,129,0.05); color: #065F46;">
              <span class="ms" style="color: #10B981;">verified</span> Verified Student
            </div>
            {% endif %}
            
            {% if has_loan_repaid %}
            <div class="badge-card">
              <span class="ms" style="color: var(--amber);">payments</span> Reliable Repayer
            </div>
            {% endif %}
            
            {% if has_meal_drop %}
            <div class="badge-card">
              <span class="ms" style="color: var(--emerald);">favorite</span> Good Samaritan
            </div>
            {% endif %}
            
            {% if user.lent_amount > 0 %}
            <div class="badge-card">
              <span class="ms" style="color: var(--navy);">handshake</span> Active Lender
            </div>
            {% endif %}
          </div>
        </div>
      </div>

    </div>

    <!-- Trust Timeline -->
    <div class="card mt24">
      <div class="card-title"><span class="ms">history</span> Trust History</div>
      <div class="tl">
        {% for ev in events %}
        <div class="trust-event">
          {% set icon = 'info' %}
          {% set icon_cls = 'navy' %}
          {% if ev.event_type == 'loan_repaid' %}{% set icon = 'payments' %}{% set icon_cls = 'emerald' %}{% endif %}
          {% if ev.event_type == 'vouch_received' %}{% set icon = 'handshake' %}{% set icon_cls = 'navy' %}{% endif %}
          {% if ev.event_type == 'gig_completed' %}{% set icon = 'work' %}{% set icon_cls = 'emerald' %}{% endif %}
          {% if ev.event_type == 'meal_drop' %}{% set icon = 'restaurant' %}{% set icon_cls = 'emerald' %}{% endif %}
          {% if ev.points_delta < 0 %}{% set icon_cls = 'crimson' %}{% endif %}
          
          <div class="trust-event-icon {{ icon_cls }}"><span class="ms">{{ icon }}</span></div>
          <div class="trust-event-details">
            <div class="trust-event-title">{{ ev.description }}</div>
            <div class="trust-event-meta">{{ ev.created_at }} &middot; {{ ev.event_type | replace('_', ' ') | title }}</div>
          </div>
          <div class="trust-event-points {% if ev.points_delta > 0 %}pos{% elif ev.points_delta < 0 %}neg{% endif %}">
            {% if ev.points_delta > 0 %}+{% endif %}{{ ev.points_delta }}
          </div>
        </div>
        {% endfor %}
        {% if not events %}
        <div class="muted" style="padding: 24px 0;">No trust events yet.</div>
        {% endif %}
      </div>
      <div class="center mt16">
        <a href="#" class="btn btn-quiet">Request your trust score review</a>
      </div>
    </div>

  </main>
</div>

<!-- Vouch Modal -->
<div class="modal-overlay" id="vouch-modal">
  <div class="modal-content">
    <div style="width: 64px; height: 64px; background: rgba(30,58,138,0.1); color: var(--navy); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px;">
      <span class="ms" style="font-size: 32px;">handshake</span>
    </div>
    <h3 style="font-size: 20px; font-weight: 700; margin-bottom: 8px;">Request a Vouch</h3>
    <p style="font-size: 14.5px; color: var(--text2); margin-bottom: 24px;">Ask a peer to vouch for your reliability. This boosts your trust score.</p>
    
    <div class="field" style="text-align: left; margin-bottom: 24px;">
      <label style="font-size: 13.5px; font-weight: 600; display: block; margin-bottom: 6px;">Peer Student ID</label>
      <input type="text" class="input" id="vouch-id" placeholder="e.g. 011234567" style="height: 44px; border: 1px solid var(--border); border-radius: var(--r); padding: 0 14px; font-family: inherit; font-size: 15px; color: var(--text); background: #fff; width: 100%; outline: none; box-sizing: border-box;">
    </div>

    <button class="btn btn-primary btn-block" onclick="sendVouch()">Send Request</button>
    <button class="btn btn-quiet btn-block modal-close" style="margin-top: 8px;" onclick="closeVouchModal()">Cancel</button>
  </div>
</div>

<div class="toast-container" id="toast-container"></div>

<script>
function showToast(msg) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<span class="ms">check_circle</span> ${msg}`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(20px)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function shareProfile() {
  const text = `Check out my UIU Aid Trust Profile! Score: {{ user.trust_score }}/100 ({{ user.tier }} Tier)`;
  navigator.clipboard.writeText(text).then(() => {
    showToast('Trust Profile link & score copied to clipboard!');
  }).catch(() => {
    showToast('Trust Profile link & score copied to clipboard!');
  });
}

function requestVouch() {
  document.getElementById('vouch-modal').classList.add('active');
}
function closeVouchModal() {
  document.getElementById('vouch-modal').classList.remove('active');
  document.getElementById('vouch-id').value = '';
}
function sendVouch() {
  const id = document.getElementById('vouch-id').value;
  if (!id) return;
  closeVouchModal();
  showToast(`Vouch request sent to ${id}!`);
}
</script>
</body>
</html>
"""

meal_drops_html = meal_drops_html.replace('__CSS__', css)
trust_profile_html = trust_profile_html.replace('__CSS__', css)

with open('d:/uiuCrowdFunding/templates/meal_drops.html', 'w', encoding='utf-8') as f:
    f.write(meal_drops_html)

with open('d:/uiuCrowdFunding/templates/trust_profile.html', 'w', encoding='utf-8') as f:
    f.write(trust_profile_html)

print("Generated templates successfully.")
