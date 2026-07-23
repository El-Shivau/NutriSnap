# NutriSnap – API Reference

> **Note:** This document describes the planned API endpoints. Full implementation begins in Phase 5.

## Base URL

- Development: `http://127.0.0.1:5000`
- Production: `https://your-domain.com`

---

## Authentication

### POST /auth/register
Register a new user account.

**Request Body (form data)**
| Field | Type | Required |
|-------|------|----------|
| username | string | ✅ |
| email | string | ✅ |
| password | string | ✅ |
| confirm_password | string | ✅ |

**Responses**
- `302` → Redirect to `/auth/login` on success
- `200` → Re-render form with errors on failure

---

### POST /auth/login
Authenticate a user.

**Request Body (form data)**
| Field | Type | Required |
|-------|------|----------|
| email | string | ✅ |
| password | string | ✅ |
| remember | boolean | ❌ |

**Responses**
- `302` → Redirect to `/dashboard` on success
- `200` → Re-render form with error on failure

---

### GET /auth/logout
Log out the current user.

**Responses**
- `302` → Redirect to `/`

---

## Food Recognition

### POST /food/upload
Upload a food image for recognition.

**Request Body (multipart/form-data)**
| Field | Type | Required |
|-------|------|----------|
| food_image | file | ✅ |

**Constraints**
- Max file size: 16 MB
- Allowed types: PNG, JPG, JPEG, WebP

**Responses**
- `302` → Redirect to `/food/prediction` with results in session
- `400` → Invalid file type or size

---

### GET /food/prediction
Display prediction results (reads from session).

**Response** `200` — Renders `food/prediction.html` with:
- Top-1 food name and confidence
- Top-3 predictions
- Nutritional information

---

### POST /food/log
Save a confirmed food log entry.

**Request Body (form data)**
| Field | Type | Required |
|-------|------|----------|
| food_name | string | ✅ |
| confidence | float | ✅ |
| notes | string | ❌ |

**Responses**
- `302` → Redirect to `/food/history` on success

---

### GET /food/history
Display the user's food log history.

**Response** `200` — Renders `food/history.html`

---

## Dashboard

### GET /dashboard
User dashboard with today's summary.

**Response** `200` — Renders `dashboard/dashboard.html`

---

### GET /profile
User profile page.

**Response** `200` — Renders `user/profile.html`

### POST /profile
Update user profile.

**Response** `302` → Redirect to `/profile` after update
