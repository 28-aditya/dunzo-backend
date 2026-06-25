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

# 🚀 dunzo backend

Production-ready **FastAPI + PostgreSQL backend** built with OAuth authentication, a clean service-layer architecture, and fully modular REST APIs for tasks, notes, settings, user data, and UI state persistence.

---

## 🧠 Overview

dunzo backend is the server powering a productivity application with:

- Google & GitHub OAuth authentication
- JWT/session-based auth
- Fully separated service layer (no business logic in routes)
- Resource-based REST API design
- PostgreSQL persistence via SQLAlchemy
- Clean frontend/backend separation

Frontend is completely decoupled and consumes only HTTP APIs.

---

## ⚙️ Core Features

### 🔐 Authentication
- Google OAuth 2.0 login
- GitHub OAuth login
- Secure backend callback handling
- Automatic user creation on first login
- Session or JWT authentication
- Protected routes using dependency injection

---

### 👤 User System
- OAuth-only authentication (no passwords stored)
- User profile:
  - name
  - email
  - avatar (from provider)
- Provider tracking (Google / GitHub)
- Persistent sessions across requests
- Central `/api/me` snapshot endpoint

---

## 📦 Data Modules (Fully Implemented)

### ✅ Tasks System
Core productivity module for user task management.

**Capabilities:**
- Create tasks
- Update tasks
- Delete tasks
- Mark complete / incomplete
- Archive / unarchive tasks
- User-scoped isolation (strict per-user data)

**Stored data:**
- title
- description
- completion state
- archive state
- timestamps

---

### 📝 Notes System
Flexible note-taking module.

**Capabilities:**
- Create notes
- Edit notes
- Delete notes
- Persistent per-user storage

**Stored data:**
- title (optional)
- content
- timestamps

---

### ⚙️ Settings System
User preference management layer.

**Capabilities:**
- Update user settings
- Persist across sessions/devices

**Settings include:**
- dark mode toggle
- daily goals
- notification preferences
- auto-archive behavior
- UI preferences

---

### 🧭 UI State Persistence (Lightweight)
Stores temporary UI state separate from business data.

**Purpose:**
- Restore last active view on refresh/login
- Improve UX continuity

**Example:**
- current_view (dashboard, tasks, notes)

---

## 🌐 API DESIGN

Strict **resource-based REST architecture**.

---

### 🔐 Authentication Flow

Frontend → OAuth Provider (Google/GitHub) → Backend callback → User lookup/create → Session/JWT issued

---

### 📡 Endpoints

---

### 🧩 Tasks API
```
        POST /api/tasks → Create task
        PUT /api/tasks/{id} → Update task
        DELETE /api/tasks/{id} → Delete task
```
---

All operations:
- require authentication
- are user-scoped
- validated via Pydantic schemas
- handled via service layer

---

### 🧩 Notes API
```
        POST /api/notes → Create note
        PUT /api/notes/{id} → Update note
        DELETE /api/notes/{id} → Delete note
```

---

### 🧩 Settings API
```
        PUT /api/settings → Update user settings
```

---

### 👤 User API
```
        
        Returns:
        - user profile
        - tasks
        - notes
        - settings
        - categories (if used)
```

---

### 🧭 UI State API
```
        PUT /api/user/state → Persist UI state
        
        Example payload:
        ```json
        {
        "current_view": "dashboard"
        }
```
```md id="fullmd1"
# 🚀 dunzo backend

## 🏗 Architecture

Strict layered design:

```

Frontend (Cloudflare Pages)
↓
FastAPI Routes Layer
↓
Service Layer (Business Logic)
↓
SQLAlchemy ORM Layer
↓
PostgreSQL Database

```

### Why this matters
- Routes are thin (request handling only)
- Services contain all business logic
- DB access is centralized
- Easy to test, scale, and debug

---

## 📁 Project Structure

```

app/
├── main.py
├── core/
│   ├── config.py
│   ├── security.py
│   ├── auth_dependencies.py
├── auth/
│   ├── google_oauth.py
│   ├── github_oauth.py
├── routes/
│   ├── user.py
│   ├── tasks.py
│   ├── notes.py
│   ├── settings.py
├── services/
│   ├── user_service.py
│   ├── task_service.py
│   ├── note_service.py
│   ├── settings_service.py
│   ├── data_service.py
├── schemas/
│   ├── user.py
│   ├── task.py
│   ├── note.py
│   ├── settings.py
├── db/
│   ├── models.py
│   ├── session.py
│   ├── base.py
├── utils/
│   ├── helpers.py
│   ├── serialization.py

```

---

## 🔧 Environment Variables

```

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

DATABASE_URL=

SECRET_KEY=

FRONTEND_URL=
BACKEND_URL=

```

⚠️ Never commit `.env`.

---

## 🔒 Design Principles

- Strict separation of concerns (routes → services → db)
- Pydantic validation for all inputs
- Resource-based API design (no monolithic endpoints)
- Stateless frontend with backend persistence
- OAuth handled entirely server-side
- No frontend secrets exposed
- Clean scalable architecture

---

## 📊 Status

### ✅ Completed
- Google OAuth authentication
- GitHub OAuth authentication
- Full service-layer architecture
- Tasks CRUD system
- Notes CRUD system
- Settings system
- User snapshot endpoint (/api/me)
- UI state persistence endpoint
- PostgreSQL integration
- Modular route structure

### 🔜 Planned
- WebSockets for real-time sync
- Offline-first support
- Background job processing
- Rate limiting & API hardening
- Analytics tracking layer
```


<div align="center">
<sub>Secure. Minimal. Scalable.</sub>
</div>
