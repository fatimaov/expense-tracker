## 1. Product Overview

This product is a simple web application that helps users quickly record and review their personal expenses in one place.

The MVP focuses on daily personal expense tracking, allowing users to manually add expenses and view them in a chronological list.

The core value of the product is simplicity and speed: users can log expenses quickly through a minimal form and immediately see all their records without complex filtering or configuration.

The application includes a basic categorization system with a fixed set of categories: Transport, Accommodation, Food, Activities, and Other.

Each expense contains the following fields: amount (in euros), title/description, date, category, and optional notes.

Expenses are displayed in a single list ordered by newest first. Users can create, edit, and delete expense records.

User authentication is required (email and password) to ensure that each user’s data is private and isolated.

The system is designed to remain minimal in the MVP while allowing future expansion, such as grouping expenses by tags (e.g., trips or events), without introducing that complexity in the initial version.


## 2. Goals and Objectives

### Primary Goal

Enable users to register, log in, and efficiently track their personal expenses by creating, viewing, editing, and deleting expense records in a simple interface.

### User Goal

Users want a fast and straightforward way to record their expenses and see all of them in one place without complexity or additional features.

### Product / Learning Goals

* Build a complete full-stack application (frontend + backend + database).
* Demonstrate product thinking through a well-scoped MVP.
* Implement authentication and CRUD operations in a real-world use case.

### Key Objectives

* Users can register and log in successfully.
* Users see a clear empty state when no expenses exist.
* Users can add a new expense in less than 10 seconds.
* Users can view all their expenses in a single list (newest first).
* Users can edit and delete existing expenses.
* The “Add Expense” flow is simple and requires minimal input friction.
* The expense date defaults to the current date but can be modified by the user.


## 3. Target Users

### Primary User

An adult individual (mid-20s to 40s), organized and comfortable with technology, who wants a simple way to keep track of personal expenses without using complex tools like spreadsheets.

The initial target user is the product creator, ensuring the app is tailored to real, practical usage.

### Usage Context

Users primarily interact with the app immediately after making a payment, aiming to log expenses in real time. Secondary usage may occur later when reviewing or completing missing entries using receipts.

### Devices

The application is designed primarily for mobile usage, enabling quick and frictionless expense entry on the go. It is also accessible on desktop, although advanced desktop-specific features are not part of the MVP.



## 4. Problem Statement

Many users do not consistently track their expenses, even though they are aware of its importance. Existing alternatives such as banking apps or spreadsheets present several limitations.

Banking applications only reflect transactions made with a card, excluding cash payments, and do not allow users to customize or edit expense information in a meaningful way. Additionally, they often include many unrelated features, making the experience slow and inefficient for quick expense tracking.

Manual tools like notes or spreadsheets require too much effort and discipline, leading to low consistency over time.

As a result, users either do not track their expenses at all or do so incompletely, which reduces their ability to understand their spending habits and maintain control over their finances.

Speed is a critical factor: after making a payment, users want to register the expense immediately with minimal friction. If the process is slow or cumbersome, they are less likely to do it.

### Core Problem

Users struggle to consistently and quickly record all their expenses in a simple and controlled way, leading to incomplete tracking and lack of visibility over their spending.


## 5. MVP Scope

The MVP includes the minimum set of features required to allow users to register, log in, and manage their personal expenses.

### Authentication

* User registration (email and password)
* User login
* User logout

### Expense Management

* Create a new expense
* View all expenses in a single list (newest first)
* Edit an existing expense
* Delete an expense

### Expense Attributes

Each expense includes:

* Amount (in euros)
* Title/description
* Date (defaults to current date but editable)
* Category (fixed list)
* Optional notes

### Categories

The system provides a fixed set of categories:

* Transport
* Accommodation
* Food
* Activities
* Other

### UI Behavior

* Users see an empty state message when no expenses exist
* A clear call-to-action is displayed to add a new expense
* A simple form is used to create and edit expenses

No additional features such as filtering, analytics, budgeting, tagging, or external integrations are included in the MVP.


## 6. Out of Scope

The following features are intentionally excluded from the MVP and may be considered for future versions:

* Expense filtering (by date, category, or other criteria)
* Analytics and reporting (e.g., spending by day, category, month, or year)
* Budget tracking and spending limits
* Tagging system for grouping expenses (e.g., trips, events)
* AI-based features such as receipt scanning and auto-completion
* Bank or card integrations (automatic transaction import or notifications)
* User profile editing (change email, password)
* Account deletion
* Multi-user or shared expenses

## 7. User Stories

* As a user, I want to register an account so that I can securely store my personal expenses.

* As a user, I want to log in so that I can access my saved expenses.

* As a user, I want to log out so that my data remains private when I stop using the app.

* As a user, I want to see an empty state when I have no expenses so that I understand I need to add my first expense.

* As a user, I want to see all my expenses in a single list so that I can quickly review them.

* As a user, I want to add a new expense so that I can keep track of my spending.

* As a user, I want the expense date to default to today so that I can log expenses faster.

* As a user, I want to edit an existing expense so that I can correct or update its information.

* As a user, I want to delete an expense so that I can remove incorrect or unnecessary records.

* As a user, I want to categorize my expenses so that I can better understand how I spend money.

## 8. Functional Requirements

### Authentication

* The system must allow users to register using an email and password.
* The system must ensure that each email is unique.
* The system must securely store user passwords using hashing.
* The system must allow users to log in with valid credentials.
* The system must allow users to log out.

### User Data Isolation

* The system must ensure that each user can only access their own expense data.
* The system must prevent access to other users' data.

### Expense Creation

* The system must allow users to create a new expense.
* The system must require the following fields:

  * Amount (must be greater than 0)
  * Title/description
  * Date
  * Category
* The system must allow an optional notes field.
* The system must default the expense date to the current date while allowing user modification.

### Expense Retrieval

* The system must retrieve all expenses belonging to the authenticated user.
* The system must display expenses in a single list ordered by newest first.

### Expense Update

* The system must allow users to edit existing expenses.
* The system must enforce the same validation rules as creation.

### Expense Deletion

* The system must allow users to delete expenses.
* The system must permanently remove the expense from the database (hard delete).

### Categories

* The system must use a fixed set of predefined categories:

  * Transport
  * Accommodation
  * Food
  * Activities
  * Other
* The system must enforce category selection from this predefined list.


## 9. User Flows

### 1. Register Flow

1. User navigates to the registration page.
2. User enters email and password.
3. User submits the form.
4. System validates input and creates account.
5. User is redirected to the main expenses view.

### 2. Login Flow

1. User navigates to the login page.
2. User enters email and password.
3. User submits the form.
4. System validates credentials.
5. User is redirected to the main expenses view.

### 3. View Expenses (Main Flow)

1. Authenticated user accesses the app.
2. System retrieves user expenses.
3. If no expenses exist:

   * Display empty state message.
   * Display CTA to add first expense.
4. If expenses exist:

   * Display list of expenses ordered by newest first.

### 4. Add Expense Flow

1. User clicks “Add Expense” button.
2. System displays expense form.
3. Date field is pre-filled with current date.
4. User fills required fields and optional notes.
5. User submits the form.
6. System validates input and creates expense.
7. User is redirected to the updated expenses list.

### 5. Edit Expense Flow

1. User selects an existing expense.
2. System displays pre-filled edit form.
3. User updates fields.
4. User submits the form.
5. System validates input and updates expense.
6. User is redirected to the updated expenses list.

### 6. Delete Expense Flow

1. User selects an existing expense.
2. User clicks delete action.
3. System optionally asks for confirmation.
4. System deletes the expense.
5. User is redirected to the updated expenses list.

### 7. Logout Flow

1. User clicks logout.
2. System clears session/token.
3. User is redirected to login page.

## 10. Screens and UI Requirements

### 1. Login Screen (Landing Page)

* This is the default entry point of the application.
* Contains:

  * Email input
  * Password input
  * Login button
  * Link to navigate to the registration screen
* On successful login, user is redirected to the main expenses screen.

### 2. Register Screen

* Accessible from the login screen.
* Contains:

  * Email input
  * Password input
  * Register button
* On successful registration, user is redirected to the main expenses screen.

### 3. Main Screen (Expenses List)

* Displays all user expenses in a vertical list ordered by newest first.
* Includes a top navigation bar with:

  * Logout button
  * “Add Expense” button (visible when expenses exist)
* Empty state:

  * Message indicating no expenses are available
  * Call-to-action button to add the first expense

### 4. Add Expense Screen

* Accessible via “Add Expense” button or empty state CTA.
* Contains a form with:

  * Amount input
  * Title/description input
  * Date input (pre-filled with current date)
  * Category selector (fixed list)
  * Notes input (optional)
* Actions:

  * Submit (create expense)
  * Cancel (return to main screen)

### 5. Edit Expense Screen

* Accessible from an existing expense item.
* Same structure as Add Expense screen, pre-filled with existing data.
* Actions:

  * Submit (update expense)
  * Cancel (return to main screen)
  * Delete (remove expense)

### UI Principles

* Mobile-first design for quick interaction.
* Minimal and clean interface to reduce friction.
* Clear primary actions (Add, Save, Delete).
* No modals; all interactions occur through dedicated screens/routes.


## 11. Data Model

### User

Represents an authenticated user of the application.

Fields:

* id (primary key)
* email (string, unique, required)
* password_hash (string, required)
* created_at (timestamp)

### Expense

Represents a single expense record created by a user.

Fields:

* id (primary key)
* user_id (foreign key → User.id, required)
* amount (decimal, required, must be greater than 0)
* title (string, required)
* expense_date (date, required)
* category (string, required, enum: Transport, Accommodation, Food, Activities, Other)
* notes (text, optional)
* created_at (timestamp)

### Relationships

* A User can have many Expenses.
* Each Expense belongs to one User.

### Future Considerations

* Tag model (for grouping expenses by trips/events)
* Relationship between Expense and Tag (likely one-to-many or many-to-many depending on future scope)


## 12. API Requirements

All endpoints are prefixed with `/api`.

### Authentication Endpoints

#### POST /api/auth/register

* Description: Register a new user.
* Request body:

  * email
  * password
* Behavior:

  * Validates input
  * Ensures email is unique
  * Hashes password
  * Creates user
* Response:

  * Success message or user data

#### POST /api/auth/login

* Description: Authenticate user.
* Request body:

  * email
  * password
* Behavior:

  * Validates credentials
  * Returns authentication token
* Response:

  * Token (e.g., JWT)

#### GET /api/users/me

* Description: Retrieve authenticated user information.
* Headers:

  * Authorization: Bearer token
* Response:

  * User data (id, email)

---

### Expense Endpoints

#### GET /api/expenses

* Description: Retrieve all expenses for the authenticated user.
* Headers:

  * Authorization: Bearer token
* Behavior:

  * Returns expenses ordered by newest first
* Response:

  * List of expense objects

#### POST /api/expenses

* Description: Create a new expense.
* Headers:

  * Authorization: Bearer token
* Request body:

  * amount
  * title
  * expense_date
  * category
  * notes (optional)
* Behavior:

  * Validates input
  * Creates expense linked to user
* Response:

  * Created expense object

#### PUT /api/expenses/:id

* Description: Update an existing expense.
* Headers:

  * Authorization: Bearer token
* Request body:

  * amount
  * title
  * expense_date
  * category
  * notes (optional)
* Behavior:

  * Validates ownership and input
  * Updates expense
* Response:

  * Updated expense object

#### DELETE /api/expenses/:id

* Description: Delete an expense.
* Headers:

  * Authorization: Bearer token
* Behavior:

  * Validates ownership
  * Deletes expense (hard delete)
* Response:

  * Success message


## 13. Authentication and Authorization

### Authentication Method

* The system uses JSON Web Tokens (JWT) for authentication.
* Upon successful login, the server generates and returns a JWT.

### Token Storage

* The JWT is stored in the browser's localStorage on the client side.
* The token is included in the Authorization header for all protected requests:

  * Authorization: Bearer <token>

### Protected Endpoints

* All expense-related endpoints (`/api/expenses`) require authentication.
* The `/api/users/me` endpoint requires authentication.

### Authorization Rules

* Users can only access, modify, or delete their own expenses.
* The system must validate that the `user_id` associated with an expense matches the authenticated user.

### Token Expiration

* JWT tokens expire after 24 hours.
* After expiration, users must log in again to obtain a new token.

## 14. Non-Functional Requirements

### Performance

* No strict performance requirements are defined for the MVP.
* The application should provide a reasonably fast and responsive experience for basic operations (login, viewing, and managing expenses).

### Responsiveness

* The application must follow a mobile-first design approach.
* The UI must be usable and accessible on both mobile and desktop devices.

### Security

* User passwords must be securely stored using hashing.
* Authentication must be handled using JWT tokens.

### Availability

* No specific uptime or availability requirements are defined for the MVP.

### Usability

* The application should prioritize simplicity and ease of use.
* Core actions (add, edit, delete expenses) should be quick and require minimal user effort.

## 15. Technology Stack

### Frontend

* React
* Vite
* React Router
* Bootstrap (for basic styling and layout)

### Backend

* Python
* Flask
* SQLAlchemy (ORM)
* Flask-Migrate (database migrations)

### Database

* PostgreSQL

### Authentication

* JSON Web Tokens (JWT)

### Development Tools

* Git and GitHub (version control)
* Postman (API testing)

## 16. Deployment Architecture

### Frontend

* Deployed on Vercel.
* Built using React and Vite.
* Connects to backend via API requests.

### Backend

* Deployed on Render.
* Runs a Flask application serving REST API endpoints.

### Database

* PostgreSQL database hosted on Render.
* Connected to the backend via environment variables.

### Environment Variables

* Separate `.env` configurations for frontend and backend.
* Backend:

  * DATABASE_URL
  * JWT_SECRET_KEY
  * other sensitive credentials
* Frontend:

  * API base URL

## 17. Project Structure

The application follows a modular and well-structured architecture to ensure scalability and separation of concerns.

### Frontend Structure (React)

```
frontend/
│   src/
│   ├── assets/            # Static assets (images, icons)
│   ├── components/        # Reusable UI components
│   ├── pages/             # Route-based views (Login, Register, Expenses, Add/Edit)
│   ├── services/          # API calls (auth, expenses)
│   ├── context/           # Global state management (auth state, etc.)
│   ├── hooks/             # Custom React hooks (optional)
│   ├── router/            # Route definitions
│   ├── styles/            # Global styles / Bootstrap overrides
│   └── main.jsx           # App entry point
```

### Backend Structure (Flask)

```
backend/
├──app/
│   ├── __init__.py        # App factory and configuration
│   ├── config.py          # Environment configuration
│   ├── extensions.py      # DB, JWT, etc.
│   ├── models/
│   │   ├── user.py
│   │   └── expense.py
│   ├── routes/
│   │   ├── auth.py
│   │   └── expenses.py
│   ├── services/          # Business logic layer
│   │   ├── auth_service.py
│   │   └── expense_service.py
│   ├── utils/             # Helpers (validation, etc.)
│   └── migrations/        # Database migrations
│   
└── run.py                 # Application entry point
```

### Structure Principles

* Clear separation between routes, business logic, and data models.
* Reusable and maintainable components in the frontend.
* Scalable architecture prepared for future features (tags, analytics, integrations).

## 18. Future Enhancements (V2+)

The following features are planned for future iterations beyond the MVP:

* Tagging system to group expenses (e.g., trips, events, custom groups)
* Analytics and reporting (spending by day, category, month, year)
* Budget tracking and spending limits
* Bank and card integration for automatic transaction import
* AI-based receipt scanning and auto-completion of expense data

## 19. Success Criteria

### Functional Success

The MVP is considered successful if the following conditions are met:

* Users can register a new account.
* Users can log in and log out successfully.
* Users can view their expense list at any time after logging in.
* Users can create new expenses.
* Users can edit existing expenses.
* Users can delete expenses.
* Expense data persists and remains available after logging out and logging back in.

### Personal Success

* The application is fully functional as a complete full-stack project.
* The project can be used as part of a portfolio to demonstrate practical skills in building a real-world application.
* The developer gains confidence in implementing authentication, CRUD operations, and a structured application architecture.
