# Demo auth server for realestate-demo

This folder contains a tiny Express backend to demonstrate OTP login and a mock Google endpoint.

Files:
- `server.js` — demo Express server with `/api/send-otp`, `/api/verify-otp`, `/api/google`, `/api/register`.
- `login.js` — frontend updated to call the demo endpoints.
- `login.css`, `UI.html` — updated UI.

Run locally:

1. Install dependencies

```bash
cd realestate-demo
npm install
```

2. Start the demo server

```bash
npm start
```

3. Open `UI.html` in your browser and click Login. When you click Next, the server console will print the OTP.

Notes:
- This is a demo-only implementation. Do not use in production.
# Indian Realty Hub — Demo

A self-contained static demo page (`demo.html`). It has no build step and no local
dependencies — fonts and images are loaded from Google Fonts and Unsplash over the
internet.

## How to run

### Option 1 — Open directly
Double-click `demo.html`, or open this in a browser:

```
file:///C:/ElvixIT/realestate/realestateproduct/realestate-demo/demo.html
```

### Option 2 — Local web server (recommended)
Run from **this** folder so `demo.html` sits at the server root:

```bash
cd realestate-demo
python -m http.server 8000
```

Then open:

```
http://localhost:8000/demo.html
```

On Windows you can just double-click `start-server.bat`, which starts the server and
opens the URL automatically.

> Note: a `404` almost always means the server was started from the wrong folder, or
> the URL was missing the path segment. Serve from `realestate-demo/` and use the URL
> above.