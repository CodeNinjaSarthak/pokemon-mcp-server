# Pokémon MCP Server + Frontend

A Pokémon battle simulator with a **FastAPI backend** and a **React + Vite frontend**.  
Simulate battles between any two Pokémon and view the battle log in real-time.

---

## 🔗 Project Source

You can get the project from:  
[https://github.com/CodeNinjaSarthak/pokemon-mcp-server](https://github.com/CodeNinjaSarthak/pokemon-mcp-server)

## 🖥️ Backend (FastAPI)

### Setup

1. (Optional) Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
# On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the FastAPI server:

```bash
uvicorn server:app --reload --host 127.0.0.1 --port 8000
```

## 🌐 Frontend (Vite + React + TypeScript)

Setup

```bash
cd frontend
npm install
npm run dev
```

Open your browser at:
http://localhost:5173

## Features

- Enter two Pokémon names and a battle level.
- Click **Battle!** to simulate a fight.
- View the winner and turn-by-turn battle log.
- Frontend fetches results from the FastAPI backend (`/mcp/tools/battle_simulator`).

---

## ⚡ Notes

- Run the **backend first**, then the frontend.
- The frontend dev server proxies `/mcp/*` requests to the backend (`127.0.0.1:8000`).

---

## 📦 Requirements

- **Python 3.9+**
- **Node.js 18+**

**Dependencies:**

- **Backend:** `fastapi`, `uvicorn[standard]`
- **Frontend:** React, Vite, TypeScript (installed via `npm install`)
