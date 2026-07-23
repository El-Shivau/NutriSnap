# NutriSnap – Database Schema

## Entity Relationship Diagram

```
┌──────────────┐        ┌──────────────────┐        ┌───────────────┐
│    users     │        │   food_logs       │        │   nutrition   │
├──────────────┤        ├──────────────────┤        ├───────────────┤
│ id (PK)      │──────┐ │ id (PK)          │        │ id (PK)       │
│ username     │      └─│ user_id (FK)     │        │ food_name (UQ)│
│ email        │        │ food_name        │        │ display_name  │
│ password_hash│        │ display_name     │        │ calories      │
│ created_at   │        │ confidence       │        │ protein_g     │
│ is_active    │        │ calories         │        │ fat_g         │
│ bio          │        │ protein_g        │        │ carbs_g       │
│ avatar_url   │        │ fat_g            │        │ fiber_g       │
└──────────────┘        │ carbs_g          │        │ serving_size_g│
                        │ fiber_g          │        │ notes         │
                        │ serving_size_g   │        └───────────────┘
                        │ image_filename   │
                        │ logged_at        │
                        │ notes            │
                        └──────────────────┘
```

---

## Table Definitions

### `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Primary key |
| username | VARCHAR(80) | UNIQUE, NOT NULL, INDEX | Login display name |
| email | VARCHAR(120) | UNIQUE, NOT NULL, INDEX | Login email |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hash — NEVER plaintext |
| created_at | DATETIME | NOT NULL | UTC account creation time |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft-disable accounts |
| bio | TEXT | NULL | Optional profile bio |
| avatar_url | VARCHAR(512) | NULL | URL to profile image |

---

### `food_logs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Primary key |
| user_id | INTEGER | FK→users.id, NOT NULL, INDEX | Owning user |
| food_name | VARCHAR(100) | NOT NULL | Food-101 class name |
| display_name | VARCHAR(100) | NOT NULL | Human-readable name |
| confidence | FLOAT | NOT NULL | ML confidence 0.0–1.0 |
| calories | FLOAT | NOT NULL | Snapshot of calories |
| protein_g | FLOAT | NOT NULL | Snapshot of protein |
| fat_g | FLOAT | NOT NULL | Snapshot of fat |
| carbs_g | FLOAT | NOT NULL | Snapshot of carbohydrates |
| fiber_g | FLOAT | NOT NULL | Snapshot of fibre |
| serving_size_g | FLOAT | NOT NULL | Snapshot of serving size |
| image_filename | VARCHAR(255) | NULL | Filename in uploads/ |
| logged_at | DATETIME | NOT NULL, INDEX | UTC log timestamp |
| notes | TEXT | NULL | Optional user notes |

> **Design Decision — Snapshot Pattern**: Nutritional values are copied from the `nutrition` table at log time rather than using a foreign key. This preserves historical accuracy — if you update nutritional data later, old log entries remain correct.

---

### `nutrition`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Primary key |
| food_name | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | Food-101 class name |
| display_name | VARCHAR(100) | NOT NULL | Human-readable name |
| calories | FLOAT | NOT NULL | kcal per serving |
| protein_g | FLOAT | NOT NULL | Protein in grams |
| fat_g | FLOAT | NOT NULL | Fat in grams |
| carbs_g | FLOAT | NOT NULL | Carbohydrates in grams |
| fiber_g | FLOAT | NOT NULL | Fibre in grams |
| serving_size_g | FLOAT | NOT NULL | Standard serving in grams |
| notes | TEXT | NULL | Optional curation notes |

---

## Relationships

- `users` → `food_logs` : **One-to-Many** (cascade delete)
- `nutrition` : **Standalone** — not FK-linked to food_logs (snapshot pattern)

## Future Tables (Phase 2+)

| Table | Purpose |
|-------|---------|
| `friends` | Social following |
| `leaderboards` | Weekly/monthly rankings |
| `recommendations` | AI meal suggestions |
| `meal_plans` | Weekly meal planning |
