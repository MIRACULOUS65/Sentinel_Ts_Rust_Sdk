# Frontend Dashboard

## 🖥️ What is this?
The visual interface for the Sentinel System.
Currently running as a lightweight **HTML/JS** dashboard, but optimized for porting to **Next.js**.

## 📊 Features
1.  **Time Series Chart**: Visualizes transaction volume (orange bars).
2.  **Live Ledger**: Real-time table of Contract/Payment operations.
3.  **Risk Indicators**: (Coming Soon) Displays AI Risk Scores from Service 3.

## 🧱 Next.js Migration
To port this to a full Next.js application:
1.  Create standard app: `npx create-next-app@latest`
2.  Copy `index.html` logic into `app/page.tsx` (using `useEffect` for fetching).
3.  Use `Chart.js` via `react-chartjs-2`.
4.  Connect to Service 2 API (`http://localhost:8009`).

## 🏃 Running (Current Version)
Simply open `index.html` in your browser.
*(Requires Service 2 to be running on port 8009)*
