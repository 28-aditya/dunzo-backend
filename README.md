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

- Email/password authentication + Google & GitHub OAuth
- JWT/session-based auth with refresh tokens
- Fully separated service layer (no business logic in routes)
- Resource-based REST API design
- PostgreSQL persistence via SQLAlchemy
- Clean frontend/backend separation
- On-read notification generation (overdue / due-soon task alerts)
- Auto-archiving of completed tasks

Frontend is completely decoupled and consumes only HTTP APIs.

---

## Try dunzo

  https://dunzo-two.vercel.app/

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
- Email/password registration and login, plus Google & GitHub OAuth
- User profile:
  - name
  - email
  - avatar (from provider, when applicable)
- Provider tracking (local / Google / GitHub)
- Persistent sessions across requests
- Central `/api/me` snapshot endpoint (also runs the auto-archive sweep)

---

## 📦 Data Modules (Fully Implemented)

### ✅ Tasks System
Core productivity module for user task management.

**Capabilities:**
- Create tasks
- Update tasks
- Delete tasks
- Mark complete / incomplete
- Archive / unarchive tasks (manual, via `is_archived` on update)
- Auto-archive: tasks completed 5+ days ago are archived automatically on `/api/me` reads, when the user's `auto_archive` setting is enabled
- User-scoped isolation (strict per-user data)

**Stored data:**
- title
- description
- completion state
- archive state
- timestamps

---

### 🔔 Notifications System
Alerts users when a task is overdue or about to be due, computed on read rather than via a background scheduler.

**Capabilities:**
- List notifications (triggers a sync pass first)
- Unread count for the bell badge
- Mark one / mark all as read
- Delete a notification
- Auto-creates a notification when a task becomes overdue or is due within 30 minutes
- Auto-cleans up notifications whose task is completed, rescheduled, archived, or deleted

**Stored data:**
- type (`overdue` | `due_soon`)
- message
- read state
- linked task
- timestamp

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

### 🔔 Notifications API
```
        GET /api/notifications/ → List notifications (runs sync first)
        GET /api/notifications/unread-count → Unread count for the bell badge
        PUT /api/notifications/{id}/read → Mark one notification read
        PUT /api/notifications/read-all → Mark all notifications read
        DELETE /api/notifications/{id} → Delete a notification
```

No scheduler process — overdue / due-soon notifications are generated and cleaned up as a side effect of the GET calls above.

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

-        app/
-        ├── main.py
-        ├── core/
-        │   ├── config.py
-        │   ├── security.py
-        │   ├── auth.py
-        ├── auth/
-        │   ├── google_oauth.py
-        ├── routes/
-        │   ├── me.py
-        │   ├── tasks.py
-        │   ├── notes.py
-        │   ├── settings.py
-        │   ├── notifications.py
-        ├── services/
-        │   ├── user_service.py
-        │   ├── task_service.py
-        │   ├── note_service.py
-        │   ├── settings_service.py
-        │   ├── data_service.py
-        │   ├── notification_service.py
-        ├── schemas/
-        │   ├── user.py
-        │   ├── task.py
-        │   ├── note.py
-        │   ├── settings.py
-        ├── db/
-        │   ├── models.py
-        │   ├── session.py
-        │   ├── deps.py
-        ├── utils/
-        │   ├── helpers.py


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
- Email/password authentication
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
- Notifications system (overdue / due-soon, read/unread, delete)
- Auto-archiving of completed tasks

### 🔜 Planned
- WebSockets for real-time sync (would replace the on-read notification sync)
- Offline-first support
- Background job processing
- Rate limiting & API hardening
- Analytics tracking layer

### ⚠️ Known production hardening items
- Password hashing uses SHA-256; should move to bcrypt/argon2
- Cookie `domain` is hardcoded to `localhost`
- OAuth flow is missing a `state` parameter
- No rate limiting on auth endpoints
- SQLAlchemy engine has `echo=True`
- Task due dates/times are stored as naive local strings with no timezone conversion (notification overdue/due-soon checks share this assumption)



<div align="center">
<sub>Secure. Minimal. Scalable.</sub>
</div>
