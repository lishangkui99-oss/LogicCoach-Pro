# Frontend Environment Check

Use this checklist before running the React frontend.

## 1) Verify Node and npm

```powershell
node -v
npm -v
```

Recommended:
- Node.js >= 20
- npm >= 10

## 2) Install dependencies

```powershell
cd frontend
npm install
```

## 3) Type check and build

```powershell
npm run type-check
npm run build
```

## 4) Start dev server

```powershell
npm run dev
```

Default URL:
- http://127.0.0.1:3000/

## 5) Backend integration check

Make sure backend is running first:
- http://127.0.0.1:8000/

If API calls fail in browser, check:
- backend process is alive
- request target is 127.0.0.1:8000
- CORS settings in backend app
