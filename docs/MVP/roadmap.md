# AI-Assisted Development Roadmap

## Phase 1 — Backend Foundation

1. Set up Flask backend structure:

   * `app/__init__.py`
   * `config.py`
   * `extensions.py`
   * `models/`
   * `routes/`
   * `services/`
   * `utils/`
2. Configure:

   * Flask app factory
   * SQLAlchemy
   * Flask-Migrate
   * JWT authentication
   * CORS
   * environment variables
3. Add PostgreSQL connection using `DATABASE_URL`.
4. Add health check route.

## Phase 2 — Backend Models

1. Create `User` model:

   * id
   * email
   * password_hash
   * created_at
2. Create `Expense` model:

   * id
   * user_id
   * amount
   * title
   * expense_date
   * category
   * notes
   * created_at
3. Add relationship:

   * One user has many expenses.
4. Add category validation using fixed values:

   * Transport
   * Accommodation
   * Food
   * Activities
   * Other
5. Generate and run migrations.

## Phase 3 — Backend Services

1. Create `auth_service.py`:

   * register user
   * validate unique email
   * hash password
   * login user
   * verify password
   * generate JWT
   * get current user
2. Create `expense_service.py`:

   * create expense
   * get user expenses ordered newest first
   * get single expense by id and user
   * update expense
   * delete expense
3. Add validation helpers:

   * required fields
   * amount greater than 0
   * valid date
   * valid category
   * ownership checks

## Phase 4 — Backend Routes

1. Add auth routes:

   * `POST /api/register`
   * `POST /api/login`
   * `GET /api/me`
2. Add expense routes:

   * `GET /api/expenses`
   * `POST /api/expenses`
   * `PUT /api/expenses/:id`
   * `DELETE /api/expenses/:id`
3. Protect private routes with JWT.
4. Ensure users can only access their own expenses.
5. Return consistent JSON responses and errors.

## Phase 5 — Backend Testing / Manual Verification

1. Test auth endpoints with Postman.
2. Test expense CRUD with valid JWT.
3. Verify:

   * duplicated emails fail
   * invalid login fails
   * expired/missing token fails
   * user cannot access another user’s expenses
   * expenses persist after logout/login
4. Fix backend issues before starting frontend.

## Phase 6 — Frontend Foundation

1. Set up React + Vite frontend.
2. Add project structure:

   * `components/`
   * `pages/`
   * `services/`
   * `context/`
   * `router/`
   * `styles/`
3. Install and configure:

   * React Router
   * Bootstrap
4. Add frontend `.env` with API base URL.
5. Create global API client helper.

## Phase 7 — Frontend Auth

1. Create auth service:

   * register
   * login
   * get current user
   * logout
2. Store JWT in `localStorage`.
3. Create auth context/state.
4. Create protected routes.
5. Build screens:

   * Login
   * Register
6. Redirect authenticated users to expenses list.
7. Redirect unauthenticated users to login.

## Phase 8 — Frontend Expense Management

1. Create expense service:

   * get expenses
   * create expense
   * update expense
   * delete expense
2. Build pages:

   * Expenses List
   * Add Expense
   * Edit Expense
3. Build reusable components:

   * ExpenseCard
   * ExpenseForm
   * EmptyState
   * Navbar
4. Implement newest-first display.
5. Add empty state with CTA.
6. Default expense date to today.
7. Add delete confirmation.

## Phase 9 — UI Polish and UX

1. Apply mobile-first layout.
2. Keep forms short and fast to use.
3. Use clear buttons:

   * Add
   * Save
   * Cancel
   * Delete
   * Logout
4. Improve loading states.
5. Improve error messages.
6. Check desktop responsiveness.

## Phase 10 — Final MVP Verification

Confirm the success criteria:

1. User can register.
2. User can log in.
3. User can log out.
4. User can add expenses.
5. User can view expenses after logging in.
6. User can edit expenses.
7. User can delete expenses.
8. Expense data persists after logout/login.
9. Each user only sees their own expenses.
10. App works on mobile and desktop.

## Phase 11 — Deployment Prep

1. Prepare backend for Render.
2. Prepare PostgreSQL database on Supabase and configure its Session Pooler.
3. Add backend environment variables:

   * `DATABASE_URL`
   * `JWT_SECRET_KEY`
4. Prepare frontend for Vercel.
5. Add frontend environment variable:

   * `VITE_API_BASE_URL`
6. Confirm deployed frontend connects to deployed backend.
7. Run final production smoke test.

## Development Rule for Codex

Implement one phase at a time.

For each phase:

1. Inspect the existing codebase.
2. Make the smallest coherent implementation.
3. Keep the structure modular.
4. Avoid adding out-of-scope features.
5. Explain what was changed.
6. Suggest the next phase only after the current one is complete.
