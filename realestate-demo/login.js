const overlay = document.getElementById('overlay');
const loginBtn = document.getElementById('loginBtn');
const closeBtn = document.getElementById('closeBtn');
const refreshCaptcha = document.getElementById('refreshCaptcha');
const captchaText = document.getElementById('captchaText');
const nextBtn = document.getElementById('nextBtn');
const googleLogin = document.getElementById('googleLogin');
const registerLink = document.getElementById('registerLink');
const whoButtons = document.querySelectorAll('.who-btn');
// Use the demo auth server for OTP/Google flows (runs on port 3000)
const authBase = 'http://127.0.0.1:3000/api';

const captchaValues = ['AB9K2', 'G7H3M', 'P2L9Q', 'Z4Y6T', 'RX1N8'];
function randomCaptcha() {
  return captchaValues[Math.floor(Math.random() * captchaValues.length)];
}

function setCaptcha() {
  if (captchaText) {
    captchaText.textContent = randomCaptcha();
  }
}

function normalizeMobile(value) {
  if (!value) return '';
  let mobile = value.toString().trim();
  mobile = mobile.replace(/[^0-9]/g, '');
  if (mobile.length === 12 && mobile.startsWith('91')) {
    mobile = mobile.slice(2);
  }
  return mobile;
}

if (loginBtn && overlay) {
  loginBtn.addEventListener('click', () => {
    overlay.classList.add('show');
    setCaptcha();
  });
}

if (closeBtn && overlay) {
  closeBtn.addEventListener('click', () => {
    overlay.classList.remove('show');
  });
}

if (overlay) {
  overlay.addEventListener('click', (event) => {
    if (event.target === overlay) {
      overlay.classList.remove('show');
    }
  });
}

if (refreshCaptcha) {
  refreshCaptcha.addEventListener('click', setCaptcha);
}

whoButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    whoButtons.forEach((item) => item.classList.remove('active'));
    btn.classList.add('active');
  });
});

if (nextBtn) {
  nextBtn.addEventListener('click', () => {
    const mobile = normalizeMobile(document.getElementById('mobileInput').value);
    const captchaEntry = document.getElementById('captchaInput').value.trim();
    const captchaValue = captchaText ? captchaText.textContent.trim() : '';

    if (!/^\d{10}$/.test(mobile)) {
      alert('Please enter a valid 10-digit mobile number.');
      return;
    }

    if (!captchaEntry) {
      alert('Please enter the captcha shown above.');
      return;
    }

    if (captchaEntry.toUpperCase() !== captchaValue) {
      alert('Captcha does not match. Please try again.');
      setCaptcha();
      return;
    }

    // call backend to send OTP and show OTP step on success
    fetch(`${authBase}/send-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mobile })
    }).then(async r => {
      const data = await r.json().catch(() => null);
      if (!r.ok) {
        console.error('send-otp HTTP error', r.status, data);
        alert('Failed to send OTP: ' + (data?.message || r.statusText || 'unknown'));
        return;
      }
      if (data && data.success) {
        document.getElementById('otpStep').style.display = '';
        document.getElementById('captchaInput').value = '';
        startOtpTimer(60);
        alert('OTP sent to ' + mobile + ' (demo, check server console)');
      } else {
        alert('Failed to send OTP: ' + (data?.message || 'unknown'));
      }
    }).catch(err => {
      console.error(err);
      alert('Could not contact demo auth server. Make sure it is running on port 3000.');
    });
  });
}

// OTP verification and resend
const verifyBtn = document.getElementById('verifyBtn');
const resendBtn = document.getElementById('resendBtn');
const otpInput = document.getElementById('otpInput');
const otpTimerEl = document.getElementById('otpTimer');

let otpTimerHandle = null;
function startOtpTimer(seconds){
  clearInterval(otpTimerHandle);
  let t = seconds;
  otpTimerEl.textContent = `Expires in ${t}s`;
  otpTimerHandle = setInterval(()=>{
    t--;
    if(t<=0){ clearInterval(otpTimerHandle); otpTimerEl.textContent='Expired'; }
    else otpTimerEl.textContent = `Expires in ${t}s`;
  },1000);
}

if (verifyBtn) {
  verifyBtn.addEventListener('click', ()=>{
    const mobile = normalizeMobile(document.getElementById('mobileInput').value);
    const otp = otpInput.value.trim();
    if (!/^[0-9]{10}$/.test(mobile)) {
      alert('Please enter a valid 10-digit mobile number before verifying OTP.');
      return;
    }
    if(!/^[0-9]{4,6}$/.test(otp)) { alert('Enter the 4-digit OTP'); return; }
    fetch(`${authBase}/verify-otp`, {
      method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ mobile, otp })
    }).then(async r => {
      const data = await r.json().catch(() => null);
      if (!r.ok) {
        console.error('verify-otp HTTP error', r.status, data);
        alert('Verify failed: ' + (data?.message || r.statusText || 'unknown'));
        return;
      }
      if(data && data.success){
        try{ localStorage.setItem('authToken', data.token); }catch(e){}
        alert(data.message || 'Logged in (demo)');
        document.getElementById('otpStep').style.display='none';
        overlay.classList.remove('show');
        if(typeof updateAuthUI === 'function') updateAuthUI();
      } else {
        alert('Verify failed: ' + (data?.message||'invalid'));
      }
    }).catch(err=>{ console.error(err); alert('Could not contact demo auth server.'); });
  });
}

if (resendBtn) {
  resendBtn.addEventListener('click', ()=>{
    const mobile = normalizeMobile(document.getElementById('mobileInput').value);
    if (!/^[0-9]{10}$/.test(mobile)) {
      alert('Please enter a valid 10-digit mobile number to resend OTP.');
      return;
    }
    fetch(`${authBase}/send-otp`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ mobile }) })
      .then(async r => {
        const data = await r.json().catch(() => null);
        if (!r.ok) {
          console.error('resend-otp HTTP error', r.status, data);
          alert('Could not resend OTP: ' + (data?.message || r.statusText || 'unknown'));
          return;
        }
        if(data && data.success){ startOtpTimer(60); alert('OTP resent (demo)'); }
        else alert('Could not resend: '+(data?.message||'error'));
      }).catch(err=>{ console.error(err); alert('Could not contact demo auth server.'); });
  });
}

if (googleLogin) {
  googleLogin.addEventListener('click', () => {
    // call demo google endpoint
    fetch(`${authBase}/google`, { method: 'POST' })
      .then(async r => {
        const data = await r.json().catch(() => null);
        if (!r.ok) {
          console.error('google HTTP error', r.status, data);
          alert('Google demo failed: ' + (data?.message || r.statusText || 'unknown'));
          return;
        }
        if (data && data.success) {
            try{ localStorage.setItem('authToken', data.token); }catch(e){}
            if(typeof updateAuthUI === 'function') updateAuthUI();
            alert('Google login (demo) — token: ' + data.token);
        } else {
          alert('Google demo failed');
        }
      }).catch(err => {
        console.error(err);
        alert('Could not contact demo auth server.');
      });
  });
}

if (registerLink) {
  registerLink.addEventListener('click', (event) => {
    event.preventDefault();
    const mobile = normalizeMobile(document.getElementById('mobileInput').value);
    if (!/^[0-9]{10}$/.test(mobile)) {
      alert('Please enter a valid 10-digit mobile number to register.');
      return;
    }
    fetch(`${authBase}/register`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ mobile })
    }).then(async r => {
      const data = await r.json().catch(() => null);
      if (!r.ok) {
        console.error('register HTTP error', r.status, data);
        alert('Register failed: ' + (data?.message || r.statusText || 'unknown'));
        return;
      }
      if(data && data.token){ try{ localStorage.setItem('authToken', data.token); }catch(e){}; if(typeof updateAuthUI === 'function') updateAuthUI(); }
      alert((data && data.message) || 'Registered (demo)');
    }).catch(err => { console.error(err); alert('Could not contact demo auth server.'); });
  });
}

setCaptcha();

// Auth UI: show logged-in state when token present
function updateAuthUI(){
  const token = localStorage.getItem('authToken');
  const userState = document.getElementById('userState');
  const loginBtnEl = document.getElementById('loginBtn');
  const userName = document.getElementById('userName');
  const logoutBtn = document.getElementById('logoutBtn');
  if(token){
    if(loginBtnEl) loginBtnEl.style.display = 'none';
    if(userState) userState.style.display = 'flex';
    if(userName) userName.textContent = 'Account';
  } else {
    if(loginBtnEl) loginBtnEl.style.display = '';
    if(userState) userState.style.display = 'none';
  }
  if(logoutBtn) logoutBtn.addEventListener('click', ()=>{ localStorage.removeItem('authToken'); updateAuthUI(); });
}

// initialize auth UI on load
updateAuthUI();
