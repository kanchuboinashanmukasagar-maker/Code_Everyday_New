# Code Everyday 🚀

A production-ready daily coding platform and competitive programming dashboard built with **Python Flask**, **SQLite**, **Gemini 2.5 Flash AI**, and a multilingual test runner supporting **Python 3**, **C (GCC)**, **C++ (G++)**, and **Java (OpenJDK)**.

---

## ✨ Features

- **Daily Coding Challenge & Streaks**:
  - Automatically serves a synchronized daily coding problem refreshed every midnight (UTC/local).
  - All users receive the exact same problem each day, persisted in SQLite.
  - Solving today's problem successfully increments the user's daily streak (+1).
  - Missing a day gracefully resets the active streak back to 1.
  - Interactive streak flame badge in the navbar and celebration modal on challenge completion.
- **Multilingual Code Execution**:
  - Users write their own solutions from scratch across **Python 3**, **C**, **C++**, and **Java**.
  - **No Pre-filled Solutions**: Starter templates provide only clean scaffolding stubs (function/class signatures), ensuring users solve problems independently.
  - Language switcher dropdown on the editor toolbar updates the starter template dynamically.
- **Strict Public & Secret Hidden Test Cases**:
  - Test suites include both visible public cases (for basic verification and input/output debugging) and **confidential hidden test cases** (boundary constraints, negative numbers, edge cases, large arrays).
  - Code is only marked **Accepted** and streak updated if **ALL** public AND hidden test cases pass.
  - Secret edge inputs are guarded server-side and never leaked in client responses.
- **Gemini AI Problem Generation**:
  - Automated generation of fresh algorithmic challenges with comprehensive public and edge hidden test cases via Gemini 2.5 Flash.
  - Fallback deterministic seed library ensures the platform never goes down if offline.
- **Interactive UI & 60 FPS Moving Visuals**:
  - Responsive dark/light theme toggle.
  - GPU-accelerated HTML5 Canvas particle constellation background.
  - Smooth 3D card tilt physics and glassmorphic translucent panels.
  - Practice problems library with category tags, difficulty filters (Easy/Medium/Hard), and search.
  - User profile with difficulty progress bars and recent multilingual submission history.
- **Production & Deployment Ready**:
  - Docker container with pre-installed Python 3.12, GCC, G++, and OpenJDK headless.
  - `docker-compose.yml` with persistent volume management.
  - Production WSGI deployment via Gunicorn (Linux/Containers) and Waitress (Windows).
  - Cloud PaaS ready (`Procfile`, `runtime.txt`, `.env.example`).

---

## 🚀 Quick Start

### Option 1: Local Development (Python)

1. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

2. **Start the Application**:
   ```powershell
   python run.py
   ```

3. **Open in Browser**:
   Navigate to **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

4. **Demo Account**:
   - **Email**: `alex.taylor@example.com`
   - **Password**: `ApexGuard#2026!`
   *(Or click "Auto-fill Demo" on the login screen)*

---

### Option 2: Run with Docker & Docker Compose (Recommended for Full Multilingual Support)

Running Code Everyday in Docker includes the complete GCC, G++, and OpenJDK toolchain out of the box:

```bash
# Build and run the container
docker compose up --build -d

# View application logs
docker compose logs -f

# Stop the container
docker compose down
```

The application will be accessible at **http://localhost:5000**.

---

## 🐳 Production Deployment

### 1. Standalone Docker Run
```bash
docker build -t code-everyday .
docker run -d -p 5000:5000 --name code-everyday -e SECRET_KEY="your-secret-key" code-everyday
```

### 2. Linux VPS with Systemd + Gunicorn
Run using Gunicorn with 3 workers and 2 threads:
```bash
gunicorn --bind 0.0.0.0:5000 --workers 3 --threads 2 --timeout 120 app:app
```

### 3. Cloud PaaS (Render, Heroku, Railway)
The repository includes:
- `Procfile`: Configured with Gunicorn entrypoint
- `runtime.txt`: Pins Python 3.12
- `.env.example`: Template for environment variables

Set your environment variables in your cloud dashboard:
- `SECRET_KEY`: A random cryptographic string
- `GEMINI_API_KEY`: (Optional) Your Gemini API Key for automated problem generation

---

## 💻 Supported Compilers & Languages

| Language | Engine | Sandboxing / Timeout | Notes |
| :--- | :--- | :--- | :--- |
| **Python 3** | Python 3.12 AST & isolated scope | 3000ms | Restricted builtins & exec sandbox |
| **Java** | `javac` & `java` (OpenJDK) | 5000ms | Dynamic class reflection harness |
| **C** | GCC (`gcc -O2`) | 5000ms | Harness injection with typed stdout protocol |
| **C++** | G++ (`g++ -O2`) | 5000ms | STL vector, string, stream comparison |

*Note: On native Windows without MinGW, Python and Java run out of the box. For local C/C++ compilation on Windows, install MinGW-w64 or use the provided Docker container.*

---

## 🔒 API Endpoints

### Authentication
- `POST /api/auth/register` — Create a new account with strength validation
- `POST /api/auth/login` — Sign in and create signed session
- `POST /api/auth/logout` — End session
- `POST /api/auth/forgot-password` — Password recovery simulation
- `GET /api/auth/me` — Current session user info

### Problems & Submissions
- `GET /api/daily-problem` — Get today's synchronized challenge
- `GET /api/problems` — List all practice problems with solved indicators
- `GET /api/problems/<id>` — Get specific problem details & multilingual starter stubs
- `POST /api/submit-solution` — Submit solution in Python, C, C++, or Java; tests public & hidden cases
- `GET /api/user/stats` — Streak details, difficulty breakdown, and recent submissions
- `POST /api/settings/gemini-key` — Save user Gemini API key
- `POST /api/problems/generate-now` — Immediately generate a challenge with Gemini

---

## 🛡️ License
MIT License. Built with ❤️ by the Code Everyday Team.

