# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working on code in this repository.

---

## 🤝 Collaboration Note

**You are working with another AI agent (Clawdbot) on this project!**

This is a multi-agent collaboration:
- **Clawdbot** (main agent): Handles planning, user communication, documentation
- **You (Claude Code)**: Handles implementation, bug fixes, technical details

### How to Collaborate

1. **Read the Plan**: Check `TEMP_PLAN.md` regularly to understand current tasks
2. **Implement Tasks**: Work on tasks listed in `TEMP_PLAN.md`
3. **Update Progress**: Record your work in `TEMP_PLAN.md` when complete
4. **Sync Info**: Update relevant documentation (`MEMORY.md`, `CLAUDE.md`) when needed

### Key Files to Monitor

- **`TEMP_PLAN.md`**: Current work plan, tasks, and progress (READ THIS FIRST!)
- **`MEMORY.md`**: Project decisions, lessons learned, workflow rules
- **This file (`CLAUDE.md`)**: Technical reference for code work

### Communication Style

- **User**: Mainly Chinese, technical terms in English
- **Documentation**: Mixed Chinese and English for clarity
- **Code**: English with Chinese comments where helpful

---

## Project Overview

SEU News is a campus information aggregation and publishing platform for Southeast University. The system consists of:

- **Flask Backend** (port 42610): Legacy template rendering system
- **Django REST API** (port 42611): Modern JSON API for Vue.js frontend
- **Vue.js Frontend** (port 24610): User interface using Vue 3 with Composition API

The project is in an active migration phase from Flask templates to Vue.js + Django REST API.

## Development Commands

### Environment Setup

**重要：本项目使用 Conda 环境 `seu-news`**

```bash
# 激活 Conda 环境
conda activate seu-news

# 或者在 Windows 上使用批处理文件
C:\Users\HUAWEI\miniconda3\Scripts\activate.bat seu-news
```

### Backend (Django API)

```bash
# 激活环境后进入项目目录
conda activate seu-news
cd D:\pythonProj\seu-news

# 安装依赖（首次使用）
pip install djangorestframework django-cors-headers

# Start Django API server (port 42611)
python django_server.py

# Or specify custom port
python django_server.py --port 8000

# Test API endpoints
python test_api.py
```

### Backend (Flask - Legacy)

```bash
# Start Flask server (port 42610)
python cmd.py
```

### Frontend (Vue.js)

```bash
cd front-vue

# Install dependencies
npm install

# Development server (port 24610)
npm run dev

# Build for production
npm run build

# Linting
npm run lint

# Unit tests
npm run test:unit

# E2E tests
npm run test:e2e
```

## Architecture

### Dual Backend System

The project uses two backends:
1. **Flask** (`cmd.py`): Legacy backend serving HTML templates from `templates/` directory
2. **Django REST API** (`django_server.py`): New JSON API at `/api/` for Vue.js frontend

Django API endpoints are defined in `api/urls.py` and implemented in `api/views.py`.

### Frontend Structure

- **API Layer** (`front-vue/src/api/`): Modular API clients using axios
  - `index.js`: Axios instance with interceptors, 30s timeout, `withCredentials: true`
  - `auth.js`: Authentication endpoints
  - `content.js`: Content CRUD operations
  - `publish.js`: Publishing and document generation
  - `review.js`: Content review workflow
  - `user.js`: User management

- **Router** (`front-vue/src/router/index.ts`): Vue Router 4 with history mode, lazy-loaded routes, comprehensive error pages

- **State Management**: Pinia is used for authentication state
  - `stores/auth.js`: Auth store with user, token, permissions

### Export Service

Export functionality is separated into a dedicated service layer:
- **ExportService** (`api/services/export_service.py`): Handles document generation
  - `generate_pdf()`: PDF generation (supports date-based or content-based)
  - `generate_typst()`: Typst format generation
  - `generate_latex()`: LaTeX format generation
  - `get_export_data()`: Export data retrieval

**Design Principle**: Export operations are independent of publishing operations, allowing for cleaner separation of concerns.

### Permission System

User permissions use a bitmask system (`django_models/models.py`):
- `0 (0b00)`: Regular user
- `1 (0b01)`: Editor (can create/edit/delete content)
- `2 (0b10)`: Admin (can manage users, deadlines)
- `3 (0b11)`: Super admin

Permission checks use properties like `is_editor`, `is_admin`, `has_editor_perm`, `has_admin_perm`.

### Content Workflow

Content flows through these states:
1. **Draft** → Created by Editor
2. **Pending** → Awaiting review
3. **Reviewed** → Approved/rejected by Admin
4. **Published** → Published to system

Users can be: creator, describer, or reviewer for each piece of content.

**Important: submitter vs describer**
- **submitter**: The user who performs the "submit" action (clicks the submit button)
- **describer**: The user who actually described/edited the content details
- These can be different people! The `/submit/` endpoint only changes status, not describer_id
- Use `/describe/` endpoint if you want to set both describer_id AND status in one call

## Key Files

### Backend Configuration
- `config/django_config.py`: Django settings (programmatic config, not settings.py)
- `config/urls.py`: Root URL routing (all APIs under `/api/`)
- `config/load_config.py`: Thread-safe configuration management
- `django_models/models.py`: Database models (User_info, Content, Comment)

### API Implementation
- `api/views/content.py`: Content management views
- `api/views/auth.py`: Authentication views
- `api/views/admin.py`: Admin management views
- `api/views/publish.py`: Publishing views
- `api/views/export.py`: Export views (PDF, Typst, LaTeX, data)
- `api/views/utility.py`: Utility views (upload, search, preview)
- `api/serializers.py`: Data serialization (6 serializers)
- `api/permissions.py`: Custom permission classes (5 permission classes)
- `api/urls.py`: API endpoint routing

### Django Files
- `django_server.py`: Django API startup script
- `manage.py`: Django management commands
- `test_api.py`: API testing script

### Frontend Configuration
- `front-vue/vite.config.ts`: Vite build config, `@` alias for `src/`, dev server on port 24610
- `front-vue/.env.development`: API base URL configuration (`VITE_API_BASE_URL`)

## Authentication

Django API uses session-based authentication (not JWT):
- Login sets `sessionid` cookie
- Frontend must include cookies in requests (`withCredentials: true` in axios)
- Auto-redirect to `/login` on 401 responses (handled in `api/index.js` interceptor)

## Database

- MySQL backend with utf8mb4 charset
- Configuration loaded from external config file
- Models defined in `django_models/models.py`

## API Endpoints

### Base URL
```
http://localhost:42611/api/
```

### Authentication Endpoints (5)
| Endpoint | Method | Function | Status |
|----------|--------|----------|--------|
| `/api/auth/login/` | POST | User login | ✅ Complete |
| `/api/auth/logout/` | POST | User logout | ✅ Complete |
| `/api/auth/register/` | POST | User registration | ✅ Complete |
| `/api/auth/user/` | GET | Current user info | ✅ Complete |
| `/api/auth/password/` | POST | Change password | ✅ Complete |

### Content Endpoints (10)
| Endpoint | Method | Function | Permission | Status |
|----------|--------|----------|------------|--------|
| `/api/content/` | GET | Content list (paginated) | Editor+ | ✅ Complete |
| `/api/content/` | POST | Create content | Editor+ | ✅ Complete |
| `/api/content/<id>/` | GET | Content details | Editor+ | ✅ Complete |
| `/api/content/<id>/` | PUT/PATCH | Update content | Owner/Admin | ✅ Complete |
| `/api/content/<id>/submit/` | POST | Submit content (draft→pending) | Editor+ | ✅ Complete |
| `/api/content/<id>/describe/` | POST | Describe content (deprecated) | Editor+ | ✅ Complete |
| `/api/content/<id>/review/` | POST | Review content | Editor+ (not own) | ✅ Complete |
| `/api/content/<id>/recall/` | POST | Recall content | Creator/Admin | ✅ Complete |
| `/api/content/<id>/cancel/` | POST | Cancel content | Owner/Admin | ✅ Complete |
| `/api/content/<id>/admin_status/` | POST | Admin force status change | Admin (role >= 2) | ✅ Complete |

**Content List Query Parameters:**
- `status`: Filter by status (comma-separated for multiple values)
- `type`: Filter by type (comma-separated for multiple values)
- `q`: Search in title
- `publish_start_date`: Filter by publish date range start (YYYY-MM-DD)
- `publish_end_date`: Filter by publish date range end (YYYY-MM-DD)
- `deadline_end_date`: Filter DDL content after this date (YYYY-MM-DD)
- `only_published`: Return only published content (true/false)
- `page`: Page number
- `page_size`: Page size (10, 20, 50, 100)
- `sort`: Sort field (id, created_at, updated_at, deadline, title, publish_at)
- `order`: Sort order (asc/desc)

### File Upload (2)
| Endpoint | Method | Function | Permission | Status |
|----------|--------|----------|------------|--------|
| `/api/upload_image/` | POST | Upload image | Editor+ | ✅ Complete |
| `/api/paste/` | POST | Paste URL | Editor+ | ✅ Complete |

### Search (1)
| Endpoint | Method | Function | Status |
|----------|--------|----------|--------|
| `/api/search/` | POST | Search content | ✅ Complete |

### Review (1)
| Endpoint | Method | Function | Status |
|----------|--------|----------|--------|
| `/api/preview/` | POST | Preview edit | ✅ Complete |

### Publishing Endpoints (1)
| Endpoint | Method | Function | Permission | Status |
|----------|--------|----------|------------|--------|
| `/api/publish/` | POST | Publish content (batch) | Editor+ | ✅ Complete |

### Export Endpoints (4)
| Endpoint | Method | Function | Permission | Status |
|----------|--------|----------|------------|--------|
| `/api/v1/export/pdf/` | POST | Generate PDF | Editor+ | ✅ Complete |
| `/api/v1/export/typst/` | GET | Generate Typst | Editor+ | ✅ Complete |
| `/api/v1/export/latex/` | GET | Generate LaTeX | Editor+ | ✅ Complete |
| `/api/v1/export/data/` | GET | Get export data | Editor+ | ✅ Complete |

**PDF Generation Parameters:**
- `date`: Generate PDF by date (YYYY-MM-DD)
- `content_ids`: Generate PDF from selected content IDs (array)

**Typst/LaTeX/Data Parameters:**
- `date`: Date to generate for (YYYY-MM-DD)

### User Management (4)
| Endpoint | Method | Function | Permission | Status |
|----------|--------|----------|------------|--------|
| `/api/admin/users/` | GET | User list | Admin | ✅ Complete |
| `/api/admin/users/<id>/role/` | POST | Edit role | Admin | ✅ Complete |
| `/api/admin/users/<id>/` | PATCH | Edit user | Admin or Self | ✅ Complete |
| `/api/admin/deadlines/` | POST | Add deadline | Admin | ✅ Complete |
| `/api/admin/dashboard/` | GET | Admin dashboard | Admin | ✅ Complete |

**Total:** 28 complete endpoints (removed 1 unpublish endpoint, 3 legacy query endpoints, 2 PDF endpoints, 3 typst/latex/data endpoints, added 1 admin_status endpoint)

## Permission Classes

| Class Name | Description |
|------------|-------------|
| `IsAuthenticated` | Requires user login |
| `IsEditorOrAdmin` | Requires editor or admin permission |
| `IsAdmin` | Requires admin permission |
| `IsOwnerOrAdmin` | Requires resource owner or admin |
| `IsCreatorOrAdmin` | Requires content creator or admin |

## Content Submission Behavior

| Endpoint | describer_id | status_change | Response | Use Case |
|----------|-------------|----------------|----------|-----------|
| `POST /content/<id>/submit/` | **Not modified** | draft → pending | success + message | Pure status transition, submitter ≠ describer |
| `POST /content/<id>/describe/` | **Set to caller** | draft → pending | Full content object | Describe AND submit in one call |

**Key Design Principle**: The `/submit/` endpoint separates the action of submitting from the role of describing content. Use `/submit/` when you only want to change status without claiming credit for the content description.

## Data Format Examples

### Login Response
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "winnower",
    "realname": "史蒂夫",
    "student_id": "123456",
    "avatar": "",
    "role": 3,
    "has_editor_perm": true,
    "has_admin_perm": true
  }
}
```

### Content List Response
```json
{
  "count": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10,
  "results": [
    {
      "id": 1,
      "title": "标题",
      "short_title": "短标题",
      "content": "内容",
      "link": "链接",
      "type": "教务",
      "status": "draft",
      "status_display": "草稿",
      "tag_list": ["标签1", "标签2"],
      "deadline": "2026-02-10",
      "creator_id": 1,
      "creator_username": "winnower",
      "describer_id": 2,
      "describer_username": "admin",
      "reviewer_id": null,
      "reviewer_username": "",
      "publish_at": null,
      "created_at": "2026-02-08T12:00:00Z",
      "formatted_created_at": "02-08 12:00",
      "updated_at": "2026-02-08T12:00:00Z",
      "formatted_updated_at": "02-08 12:00",
      "can_delete": true
    }
  ]
}
```

## Testing

### API Testing with curl

```bash
# Health check
curl http://localhost:42611/api/

# Login
curl -X POST http://localhost:42611/api/auth/login/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=123"

# Get user info (requires session cookie)
curl http://localhost:42611/api/auth/user/ \
  --cookie "sessionid=xxx"

# Content list (with publish date range)
curl "http://localhost:42611/api/content/?publish_start_date=2026-02-10&publish_end_date=2026-02-15&only_published=true" \
  --cookie "sessionid=xxx"

# Create content
curl -X POST http://localhost:42611/api/content/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=xxx" \
  -d '{"title":"测试","content":"测试内容","type":"教务"}'

# Generate PDF (from selection)
curl -X POST http://localhost:42611/api/v1/export/pdf/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=xxx" \
  -d '{"content_ids":[1,2,3]}'

# Generate PDF (from date)
curl -X POST http://localhost:42611/api/v1/export/pdf/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=xxx" \
  -d '{"date":"2026-02-11"}'
```

### Test Script

```bash
# Run automated API tests
python test_api.py

# Expected output:
# All tests pass
```

## API Refactoring (2026-02-15)

### Overview
The publish API has been refactored to separate concerns and improve maintainability:
- **Content queries** now use enhanced `ContentListAPIView`
- **Export operations** are separated into dedicated export endpoints
- **Unpublish functionality** has been removed (unused by frontend)

### Endpoint Changes

**Deprecated Endpoints (Removed):**
- `/api/publish/data/<date>/` → Use `/api/v1/export/data/`
- `/api/publish/pdf/` → Use `/api/v1/export/pdf/`
- `/api/publish/pdf_from_selection/` → Use `/api/v1/export/pdf/`
- `/api/publish/query/` → Use `/api/content/` with query parameters
- `/api/publish/query/<date>/` → Use `/api/content/` with query parameters
- `/api/publish/ddl/` → Use `/api/content/` with `deadline_end_date` parameter
- `/api/publish/unpublish/` → **Removed** (unused)
- `/api/typst/<date>/` → Use `/api/v1/export/typst/`
- `/api/latex/<date>/` → Use `/api/v1/export/latex/`

**New Endpoints:**
- `POST /api/v1/export/pdf/` - Generate PDF (supports date or content_ids)
- `GET /api/v1/export/typst/` - Generate Typst format
- `GET /api/v1/export/latex/` - Generate LaTeX format
- `GET /api/v1/export/data/` - Get export data

**Enhanced Content List:**
- `GET /api/content/` now supports:
  - `publish_start_date` & `publish_end_date` - Filter by publish date range
  - `deadline_end_date` - Filter DDL content
  - `only_published` - Return only published content

### Migration Notes

**Frontend API calls:**
- Content queries now use `/api/content/` with query parameters
- Export operations use `/api/v1/export/*` endpoints
- PDF generation merged into single endpoint with parameter-based mode selection

**Service Layer:**
- `ExportService` created for all export operations
- `PublishService` simplified (only batch publishing remains)
- `ContentListAPIView` enhanced for publish-related queries

## Important Notes

- **环境要求：必须激活 Conda 环境 `seu-news` 才能运行后端服务**
  ```bash
  conda activate seu-news
  ```
- Frontend dev server runs on port 24610 (not 5173)
- Django API runs on port 42611
- Legacy Flask runs on port 42610
- CORS is configured for Vue.js frontend
- Currently in development mode (`DEBUG=True`)
- Passwords stored with MD5 (security concern for production)
- RESTful API design is adopted
- All 27 endpoints are complete (no placeholders)

## Troubleshooting

### Django API won't start
```bash
# Check if port is in use
netstat -ano | findstr 42611

# Try a different port
python django_server.py --port 8000
```

### Database connection issues
```bash
# Check MySQL service
sc query MySQL

# Verify config file
cat config/config.txt
```

### CORS errors
- Verify `CORS_ALLOWED_ORIGINS` in `config/django_config.py`
- Ensure frontend is running on `http://localhost:24610`

---

## 📋 Frontend Refactor Complete (2026-02-09)

### Completed Changes

**Pinia Store Implementation:**
- Created `front-vue/src/stores/auth.js` for authentication state management
- Configured Pinia in `front-vue/src/main.ts`

**Route Restructuring:**
- Renamed `Main.vue` → `Manage.vue`
- All management pages moved to `/manage/*` structure
- Route guards implemented with permission checks
- Created error pages (403.vue, 404.vue)

**Authentication Flow:**
- Login page updated to use Pinia Store
- Redirect parameter support for post-login navigation
- 401 auto-logout with API interceptor

**Home Page:**
- Added management entry button with permission checking

**API Layer:**
- Updated all API calls to use RESTful endpoints
- Modified axios interceptors for better error handling
- Base URL changed to port 42611

## 📋 API Alignment Complete (2026-02-09)

### Completed Changes

**Frontend API Updates (3 files):**
- `front-vue/src/api/content.js` - 6 functions updated
- `front-vue/src/api/review.js` - 2 functions updated
- `front-vue/src/api/user.js` - 5 functions updated

**Backend API New Features (11 views):**
- ContentCreateAPIView - Create content
- UploadImageAPIView - Upload images
- PasteAPIView - Paste URL
- ContentCancelAPIView - Cancel content
- PreviewAPIView - Preview edit
- UserRoleEditAPIView - Edit user roles
- UserEditAPIView - Edit user info (PATCH)
- AdminDashboardAPIView - Admin dashboard stats
- PublishAPIView - Complete implementation
- TypstAPIView - Complete implementation
- LatexAPIView - Complete implementation

**URL Configuration:**
- Updated `api/urls.py` with all new routes
- Added DELETE method support to ContentDeleteAPIView

**All 27 API endpoints are now complete with RESTful design.**

---

## 📋 RESTful API Alignment Complete (2026-02-09)

### Completed Changes

**Frontend Fixes:**
- Fixed `front-vue/.env.development` - Added `/api` suffix to baseURL
- Fixed `front-vue/src/views/Login.vue` - Removed incorrect `.data` access from API responses
- Updated `front-vue/src/views/Admin.vue` - Changed API calls to RESTful endpoints:
  - `/api/admin/entries/` → `/api/content/`
  - `/api/recall/<id>/` → `/api/content/<id>/recall/`
  - `/api/delete/<id>/` (POST) → `/api/content/<id>/` (DELETE)

**Backend RESTful Cleanup:**
- Removed `/content/create/` route - POST to `/content/` now handles creation
- Removed `/delete/<int:pk>/` route - DELETE to `/content/<int:pk>/` handles deletion
- Removed duplicate view classes:
  - `ContentCreateAPIView` - Now handled by `ContentListAPIView` (ListCreateAPIView)
  - `ContentDeleteAPIView` - Now handled by `ContentDetailAPIView` (RetrieveUpdateDestroyAPIView)
  - Removed `destroy` method from `ContentDetailAPIView` - DELETE endpoint completely removed
- Added `perform_create` method to `ContentListAPIView` to auto-set creator ID

**Frontend Changes:**
- Removed `deleteEntry` function - use cancel/terminate instead
- Updated API calls to use RESTful endpoints
- Updated documentation to clarify DELETE is not available

**All 27 API endpoints are now complete with pure RESTful design.**

---

## 📋 API Authority Separation Complete (2026-02-15)

### Background
The `/modify/` endpoint had inconsistent behavior between frontend and backend:
- **Frontend expected**: Update content AND submit for review (atomic operation)
- **Backend implemented**: Only change status (draft → pending), ignored content data
- **Core conflict**: Frontend's `modifyEntry(id, { title, content, type... })` data was completely ignored

### Solution Implemented: Responsibility Separation

**New Endpoint:**
- `POST /api/content/<id>/submit/` - Pure status transition (draft → pending)
  - Permission: editor+
  - Request body: empty
  - **Does NOT modify describer_id** (submitter ≠ describer)
  - **Does NOT modify content fields**

**Deprecated Endpoint:**
- `POST /api/content/<id>/modify/` - Marked as deprecated, maintained for backward compatibility

### New Workflow

```
Edit content: PATCH /content/<id>/ (draft, rejected)
    ↓
Submit review: POST /content/<id>/submit/ (draft → pending)
    ↓
Review content: POST /content/<id>/review/ (pending → reviewed/rejected)
```

**Key Design Principle**: Content update and status submission are completely separated. No atomic operation endpoint provided.

### Backend Changes

**Files Modified:**
1. `api/services/content_service.py` - Added `submit_content()` method
2. `api/views/content.py` - Added `ContentSubmitAPIView` class
3. `api/urls.py` - Added `/submit/` route
4. `api/views/__init__.py` - Exported new view class

### Frontend Changes

**Files Modified:**
1. `front-vue/src/api/content.js`
   - Added `submitEntry()` function
   - Deprecated `modifyEntry()` with console warnings
2. `front-vue/src/components/ActionsDropdown.vue`
   - Updated import: `modifyEntry` → `submitEntry`
   - Updated `handleAction` to call `submitEntry()` without content data
3. `front-vue/src/api/review.js`
   - Removed duplicate `modifyEntry` definition

### Key Design Decision: submitter vs describer

**submitter**: The user who performs the "submit" action (clicks the submit button)
**describer**: The user who actually described/edited the content details

These can be different people! The `/submit/` endpoint:
- ✅ Changes status: draft → pending
- ✅ **Does NOT modify describer_id** (keeps original describer)
- ❌ **Does NOT modify content fields**

Use `/describe/` endpoint if you want to set both describer_id AND status in one call.

---

*Last updated: 2026-02-15*
