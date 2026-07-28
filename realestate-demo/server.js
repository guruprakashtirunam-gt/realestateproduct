const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
app.use(cors());
app.options('*', cors());
app.use(bodyParser.json());

// Debugging middleware: log incoming requests and payloads
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  if (req.body && Object.keys(req.body).length) {
    console.log('  body:', req.body);
  }
  next();
});

const PORT = process.env.PORT || 3000;

// Simple in-memory OTP store for demo purposes
const otps = new Map(); // mobile -> { otp, expires }

function generateOtp() {
  return Math.floor(1000 + Math.random() * 9000).toString();
}

app.post('/api/send-otp', (req, res) => {
  const { mobile } = req.body;
  if (!mobile || !/^\d{10}$/.test(mobile)) {
    return res.status(400).json({ success: false, message: 'Invalid mobile' });
  }
  const otp = generateOtp();
  const expires = Date.now() + 5 * 60 * 1000; // 5 minutes
  otps.set(mobile, { otp, expires });
  console.log(`Demo OTP for ${mobile}: ${otp}`);
  return res.json({ success: true, message: 'OTP sent (demo)' });
});

app.post('/api/verify-otp', (req, res) => {
  const { mobile, otp } = req.body;
  if (!mobile || !otp) return res.status(400).json({ success: false, message: 'Missing fields' });
  const record = otps.get(mobile);
  if (!record) return res.status(400).json({ success: false, message: 'No OTP requested for this number' });
  if (Date.now() > record.expires) {
    otps.delete(mobile);
    return res.status(400).json({ success: false, message: 'OTP expired' });
  }
  if (record.otp !== otp) return res.status(400).json({ success: false, message: 'Incorrect OTP' });
  otps.delete(mobile);
  // For demo, return a fake token
  return res.json({ success: true, token: 'demo-token-123', message: 'Login successful (demo)' });
});

app.post('/api/google', (req, res) => {
  // Demo endpoint — in production you'd implement OAuth flow
  return res.json({ success: true, token: 'demo-google-token', message: 'Google login (demo)'});
});

app.post('/api/register', (req, res) => {
  // Simple demo register endpoint
  const { mobile } = req.body;
  console.log('Register (demo) for', mobile || 'n/a');
  return res.json({ success: true, token: 'demo-register-token', message: 'Register (demo) — account created' });
});

// Simple index route to show available endpoints
app.get('/', (req, res) => {
  res.send(`
  <!doctype html>
  <html>
  <head>
    <meta charset="utf-8" />
    <title>Demo Auth Server - Test Page</title>
    <style>
      body{font-family:Inter,Arial,Helvetica,sans-serif;background:#0f1720;color:#e6eef8;padding:20px}
      .card{background:#0b1220;border:1px solid rgba(255,255,255,0.04);padding:18px;border-radius:8px;max-width:640px}
      input{padding:8px 10px;border-radius:6px;border:1px solid rgba(255,255,255,0.06);background:transparent;color:#e6eef8;width:100%}
      button{margin-top:8px;padding:8px 12px;border-radius:6px;border:none;background:#D9A552;color:#1a1305;cursor:pointer}
      .muted{color:#9fb0c9;font-size:13px}
      .row{margin-top:12px}
    </style>
  </head>
  <body>
    <div class="card">
      <h2>Demo Auth Server — Interactive Test</h2>
      <p class="muted">Use these controls to call the demo endpoints from your browser.</p>

      <div class="row">
        <label>Mobile (10 digits)</label>
        <input id="mobile" placeholder="9876543210" />
        <button id="send">Send OTP</button>
      </div>

      <div class="row">
        <label>OTP</label>
        <input id="otp" placeholder="1234" />
        <button id="verify">Verify OTP</button>
      </div>

      <div class="row">
        <button id="google">Demo Google Login</button>
        <button id="register">Demo Register</button>
      </div>

      <pre id="out" style="margin-top:12px;background:#07101a;padding:12px;border-radius:6px;color:#bfe3ff;max-height:240px;overflow:auto"></pre>
    </div>

    <script>
      const out = document.getElementById('out');
      function log(...args){ out.textContent += args.map(a=> typeof a === 'object' ? JSON.stringify(a,null,2) : String(a)).join(' ') + '\n'; out.scrollTop = out.scrollHeight; }

      document.getElementById('send').addEventListener('click', async ()=>{
        const mobile = document.getElementById('mobile').value.trim();
        log('POST /api/send-otp', { mobile });
        try{
          const r = await fetch('/api/send-otp', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ mobile }) });
          const j = await r.json(); log('→', r.status, j);
        }catch(e){ log('ERR', e.message); }
      });

      document.getElementById('verify').addEventListener('click', async ()=>{
        const mobile = document.getElementById('mobile').value.trim();
        const otp = document.getElementById('otp').value.trim();
        log('POST /api/verify-otp', { mobile, otp });
        try{
          const r = await fetch('/api/verify-otp', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ mobile, otp }) });
          const j = await r.json(); log('→', r.status, j);
        }catch(e){ log('ERR', e.message); }
      });

      document.getElementById('google').addEventListener('click', async ()=>{
        log('POST /api/google');
        try{ const r = await fetch('/api/google', { method:'POST' }); const j = await r.json(); log('→', r.status, j); }catch(e){ log('ERR', e.message); }
      });

      document.getElementById('register').addEventListener('click', async ()=>{
        const mobile = document.getElementById('mobile').value.trim();
        log('POST /api/register', { mobile });
        try{ const r = await fetch('/api/register', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ mobile }) }); const j = await r.json(); log('→', r.status, j); }catch(e){ log('ERR', e.message); }
      });
    </script>
  </body>
  </html>
  `);
});

app.listen(PORT, () => {
  console.log(`Demo auth server running on http://localhost:${PORT}`);
});
