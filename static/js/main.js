// UIU Aid - Global Client Helper
function showToast(message, type = 'success') {
  let toast = document.getElementById('uiu-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'uiu-toast';
    toast.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      padding: 14px 22px;
      background: #1E3A8A;
      color: #fff;
      border-radius: 8px;
      font-family: 'Inter', sans-serif;
      font-size: 14.5px;
      font-weight: 600;
      box-shadow: 0 10px 25px rgba(0,0,0,0.18);
      z-index: 9999;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all 0.3s ease;
      opacity: 0;
      transform: translateY(20px);
    `;
    document.body.appendChild(toast);
  }
  
  const icon = type === 'success' ? 'check_circle' : (type === 'error' ? 'error' : 'info');
  const bg = type === 'success' ? '#059669' : (type === 'error' ? '#DC2626' : '#1E3A8A');
  toast.style.background = bg;
  toast.innerHTML = `<span class="ms ms-20" style="font-size:20px;">${icon}</span> <span>${message}</span>`;
  toast.style.opacity = '1';
  toast.style.transform = 'translateY(0)';
  
  clearTimeout(toast.__timer);
  toast.__timer = setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(20px)';
  }, 4000);
}

// Modal helper
function openModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) {
    m.style.display = 'flex';
  }
}

function closeModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) {
    m.style.display = 'none';
  }
}
