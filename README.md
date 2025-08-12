# Recaller

**Recaller** is a privacy-first, open-source personal assistant app to help you manage your finances, communications, social activities, belongings, and recurring payments—all powered by on-device/self-hosted AI.

---

## 🚀 Features

- Unified dashboard for finances, reminders, belongings, and more
- FastAPI backend (Python) with PostgreSQL and Redis
- Modern React frontend (TypeScript, MUI)
- Privacy-first: No user data sent to third-party AI services
- Open-source, extensible, and community-driven

---

## 🗂️ Project Structure

    recaller/
    ├── backend/        # FastAPI app (Python)
    ├── frontend/       # React app (TypeScript)
    ├── docker-compose.yml
    ├── .gitignore
    └── README.md

---

## 🏁 Getting Started (Development)

### Prerequisites

- [Docker](https://www.docker.com/get-started) & [Docker Compose](https://docs.docker.com/compose/)
- (Optional) [Node.js](https://nodejs.org/) and [Python 3.10+](https://www.python.org/) for manual setup

---

### Quick Start (with Docker Compose)

1. **Clone the repository:**

        git clone https://github.com/yourusername/recaller.git
        cd recaller

2. **Start all services:**

        docker-compose up --build

3. **Access the apps:**
    - Frontend: http://localhost:3000
    - Backend API: http://localhost:8000
    - API Docs: http://localhost:8000/docs
    - PostgreSQL: localhost:5432 (user: `recaller`, password: `recaller`)
    - Redis: localhost:6379

---

### Manual Setup

#### Backend (FastAPI)

    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload

#### Frontend (React)

    cd frontend
    npm install
    npm start

---

## ⚙️ Environment Variables

- **Backend:** Set in `docker-compose.yml` or `.env` file (see `backend/.env.example`)
- **Frontend:** API URL set via `REACT_APP_API_URL` in `.env` or Docker Compose

---

## 🧪 Running Tests

- **Backend:**

        cd backend
        pytest

- **Frontend:**

        cd frontend
        npm test

- **Playwright Screenshots:**

        cd frontend
        npm run validate:playwright
        npm run screenshots:generate

---

## 🐳 Docker Compose Services

| Service   | Description      | Port  |
|-----------|------------------|-------|
| backend   | FastAPI API      | 8000  |
| frontend  | React UI         | 3000  |
| db        | PostgreSQL       | 5432  |
| redis     | Redis cache      | 6379  |

---

## 🛠️ Project Scripts

- `docker-compose up --build` — Build and start all services
- `docker-compose down` — Stop all services
- `docker-compose logs -f` — View logs

### Playwright Integration

- `npm run validate:playwright` — Validate Playwright setup
- `npm run screenshots:generate` — Generate screenshots manually
- `npm run test:playwright` — Run Playwright tests

For more details, see [PLAYWRIGHT_INTEGRATION.md](PLAYWRIGHT_INTEGRATION.md).

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

- Open issues for bugs or feature requests
- Fork and submit pull requests
- Join our community chat (Discord/Matrix/Slack) — link coming soon

---

## 📄 License

This project is licensed under the [AGPLv3](LICENSE) (or your chosen license).

---

## 📣 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)
- [MUI](https://mui.com/)

---

## 🌐 Links

- **Project Website:** https://recaller.app (coming soon)
- **Documentation:** docs/ (coming soon)
- **Community:** (coming soon)

---

*Built with ❤️ for privacy and productivity.*