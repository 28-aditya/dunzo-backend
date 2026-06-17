<div align="center">

```
██████╗ ██╗   ██╗███╗   ██╗███████╗ ██████╗ 
██╔══██╗██║   ██║████╗  ██║╚══███╔╝██╔═══██╗
██║  ██║██║   ██║██╔██╗ ██║  ███╔╝ ██║   ██║
██║  ██║██║   ██║██║╚██╗██║ ███╔╝  ██║   ██║
██████╔╝╚██████╔╝██║ ╚████║███████╗╚██████╔╝
╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚══════╝ ╚═════╝ 
```

**dunzo backend**

*A secure FastAPI backend powering authentication, user accounts, and PostgreSQL data storage with Google & GitHub OAuth.*

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat-square&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)

</div>

---

## What is this?

Backend service for **dunzo** built with FastAPI + PostgreSQL.

Handles authentication, users, and future data sync for tasks, notes, and settings.

---

## Features

### Authentication
- Google OAuth login
- GitHub OAuth login
- Secure callback handling
- JWT/session authentication
- Auto user creation on first login

### User System
- OAuth-based signup/login only
- User profiles (name, email, avatar)
- Provider tracking
- Persistent sessions

### Database (PostgreSQL)
- User storage
- Ready for:
  - task sync
  - notes sync
  - settings sync

### API
- FastAPI REST backend
- CORS configured for frontend
- Environment-based config

---

## Architecture

```
Frontend (Cloudflare Pages)
        ↓
FastAPI Backend (Render)
        ↓
PostgreSQL Database (Neon / Supabase / Render)
        ↓
Google / GitHub OAuth
```

---

## Project Structure

```
app/
├── main.py
├── core/
│   ├── config.py
│   ├── security.py
├── auth/
│   ├── google.py
│   ├── github.py
├── db/
│   ├── models.py
│   ├── session.py
├── routes/
│   ├── user.py
└── utils/
    ├── helpers.py
```

---

## Environment Variables

```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

DATABASE_URL=postgresql://user:password@host:port/db

SECRET_KEY=your_secret_key

FRONTEND_URL=https://your-frontend.pages.dev
BACKEND_URL=https://your-backend.onrender.com
```

⚠️ Never commit `.env`.

---

## API Flow

### Google Login
```
Frontend → /auth/google/login
        → Google OAuth
        → /auth/google/callback
        → Create/FETCH user
        → Issue session/JWT
        → Redirect frontend
```

### GitHub Login
Same flow via `/auth/github/*`

---

## CORS

```python
origins = [
    "https://your-frontend.pages.dev"
]
```

---

## Status

### Completed
- Project setup
- OAuth design
- DB schema planning

### In Progress
- Google OAuth implementation
- GitHub OAuth implementation
- Auth system

### Planned
- Task sync
- Notes sync
- Settings sync
- Multi-device support

---

## Notes

- Backend is fully separate from frontend
- Frontend never handles secrets
- OAuth is fully server-side
- Designed for Render + PostgreSQL deployment

---

<div align="center">
<sub>Secure. Minimal. Scalable.</sub>
</div>
