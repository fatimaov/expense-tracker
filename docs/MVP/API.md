# Backend API Reference

## Overview

- Base URL: `http://localhost:5000`
- Request and response format: JSON
- Protected endpoints require `Authorization: Bearer <access_token>`.
- Access tokens expire after 24 hours.
- Dates use `YYYY-MM-DD`; timestamps use ISO 8601.

## Common Objects

### User

```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-06-29T10:30:00"
}
```

### Expense

```json
{
  "id": 1,
  "title": "Lunch",
  "amount": 12.5,
  "category": "Food",
  "expense_date": "2026-06-29",
  "notes": "Lunch with coworkers",
  "created_at": "2026-06-29T10:35:00"
}
```

### Error

```json
{
  "error": {
    "message": "Expense not found.",
    "code": "EXPENSE_NOT_FOUND"
  }
}
```

## Authentication

### Register user

`POST /api/auth/register`

Authentication: Public.

Request:

```json
{
  "email": "user@example.com",
  "password": "secure-password"
}
```

Success — `201 Created`:

```json
{
  "message": "User registered successfully.",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "created_at": "2026-06-29T10:30:00"
    }
  }
}
```

Errors:

- `400 VALIDATION_ERROR`: malformed JSON, invalid email, or password shorter than 8 characters.
- `409 EMAIL_ALREADY_EXISTS`: the normalized email is already registered.

### Login

`POST /api/auth/login`

Authentication: Public.

Request:

```json
{
  "email": "user@example.com",
  "password": "secure-password"
}
```

Success — `200 OK`:

```json
{
  "message": "Login successful.",
  "data": {
    "access_token": "<jwt>",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "created_at": "2026-06-29T10:30:00"
    }
  }
}
```

Errors:

- `400 VALIDATION_ERROR`: malformed or invalid credentials input.
- `401 INVALID_CREDENTIALS`: the email/password combination is incorrect.

## User

### Get current user

`GET /api/users/me`

Authentication: Required.

Request body: None.

Success — `200 OK`:

```json
{
  "message": "User retrieved successfully.",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "created_at": "2026-06-29T10:30:00"
    }
  }
}
```

Errors:

- `401 AUTHORIZATION_REQUIRED`: token is missing.
- `401 INVALID_TOKEN`: token is malformed or invalid.
- `401 TOKEN_EXPIRED`: token has expired.
- `401 INVALID_TOKEN_IDENTITY`: token identity cannot be used as a user ID.
- `404 USER_NOT_FOUND`: the token's user no longer exists.

## Categories

### List categories

`GET /api/categories`

Authentication: Public.

Request body: None.

Success — `200 OK`:

```json
{
  "categories": [
    {
      "key": "FOOD",
      "label": "Food",
      "value": "Food"
    }
  ]
}
```

The complete values are `Transport`, `Accommodation`, `Food`, `Activities`, and `Other`.

## Expenses

All expense endpoints require authentication. An expense that does not exist and an expense owned by another user both return `404 EXPENSE_NOT_FOUND`.

### List expenses

`GET /api/expenses`

Request body: None.

Success — `200 OK`:

```json
{
  "expenses": []
}
```

Expenses are scoped to the authenticated user and ordered by `expense_date` descending.

Errors: common `401` token errors.

### Create expense

`POST /api/expenses`

Request:

```json
{
  "title": "Lunch",
  "amount": 12.5,
  "category": "Food",
  "expense_date": "2026-06-29",
  "notes": "Lunch with coworkers"
}
```

`title`, `amount`, `category`, and `expense_date` are required. `notes` is optional.

Success — `201 Created`:

```json
{
  "expense": {
    "id": 1,
    "title": "Lunch",
    "amount": 12.5,
    "category": "Food",
    "expense_date": "2026-06-29",
    "notes": "Lunch with coworkers",
    "created_at": "2026-06-29T10:35:00"
  }
}
```

Errors:

- `400 VALIDATION_ERROR`: malformed JSON or invalid/missing expense fields.
- Common `401` token errors.

### Get expense

`GET /api/expenses/<id>`

Request body: None.

Success — `200 OK`:

```json
{
  "expense": {
    "id": 1,
    "title": "Lunch",
    "amount": 12.5,
    "category": "Food",
    "expense_date": "2026-06-29",
    "notes": null,
    "created_at": "2026-06-29T10:35:00"
  }
}
```

Errors:

- `404 EXPENSE_NOT_FOUND`: expense is missing or owned by another user.
- Common `401` token errors.

### Update expense

`PUT /api/expenses/<id>`

Request: the complete mutable expense representation is required.

```json
{
  "title": "Dinner",
  "amount": 18.75,
  "category": "Activities",
  "expense_date": "2026-06-30",
  "notes": null
}
```

Success — `200 OK`: `{ "expense": <Expense> }`.

Errors:

- `400 VALIDATION_ERROR`: malformed JSON or invalid/missing expense fields.
- `404 EXPENSE_NOT_FOUND`: expense is missing or owned by another user.
- Common `401` token errors.

### Delete expense

`DELETE /api/expenses/<id>`

Request body: None.

Success — `200 OK`:

```json
{
  "message": "Expense deleted successfully."
}
```

Errors:

- `404 EXPENSE_NOT_FOUND`: expense is missing or owned by another user.
- Common `401` token errors.

## Error Codes

| HTTP | Code | Meaning |
| --- | --- | --- |
| 400 | `VALIDATION_ERROR` | Request JSON or field values are invalid. |
| 401 | `AUTHORIZATION_REQUIRED` | A protected endpoint was called without a token. |
| 401 | `INVALID_TOKEN` | The token is malformed or has an invalid signature. |
| 401 | `TOKEN_EXPIRED` | The access token has expired. |
| 401 | `INVALID_TOKEN_IDENTITY` | The token identity is not a usable user ID. |
| 401 | `INVALID_CREDENTIALS` | Login credentials are incorrect. |
| 404 | `USER_NOT_FOUND` | The authenticated user no longer exists. |
| 404 | `EXPENSE_NOT_FOUND` | The expense is absent or inaccessible. |
| 409 | `EMAIL_ALREADY_EXISTS` | Registration email is already in use. |

## Postman Testing Checklist

Create collection variables:

- `base_url`: `http://localhost:5000`
- `access_token`: initially empty
- `expense_id`: initially empty
- `other_access_token`: initially empty

### Happy path

- [ ] Register with `POST {{base_url}}/api/auth/register`; expect `201`.
- [ ] Login with `POST {{base_url}}/api/auth/login`; expect `200`.
- [ ] Save `data.access_token` as `access_token`.
- [ ] Call `GET {{base_url}}/api/users/me` with Bearer token; expect `200` and the registered email.
- [ ] Call `GET {{base_url}}/api/categories` without a token; expect `200` and five categories.
- [ ] Create an expense with `POST {{base_url}}/api/expenses`; expect `201`.
- [ ] Save `expense.id` as `expense_id`.
- [ ] List expenses with `GET {{base_url}}/api/expenses`; expect `200` and the created expense.
- [ ] Retrieve `GET {{base_url}}/api/expenses/{{expense_id}}`; expect `200`.
- [ ] Update `PUT {{base_url}}/api/expenses/{{expense_id}}`; expect `200` and updated fields.
- [ ] Delete `DELETE {{base_url}}/api/expenses/{{expense_id}}`; expect `200`.
- [ ] Retrieve the deleted expense; expect `404 EXPENSE_NOT_FOUND`.

### Failure and isolation checks

- [ ] Register with an existing email; expect `409 EMAIL_ALREADY_EXISTS`.
- [ ] Register with malformed JSON, invalid email, or short password; expect `400 VALIDATION_ERROR`.
- [ ] Login with an incorrect password; expect `401 INVALID_CREDENTIALS`.
- [ ] Call each protected endpoint without a token; expect `401 AUTHORIZATION_REQUIRED`.
- [ ] Call a protected endpoint with a malformed token; expect `401 INVALID_TOKEN`.
- [ ] Create expenses with zero/negative amount, invalid date, invalid category, or missing required fields; expect `400 VALIDATION_ERROR`.
- [ ] Update an expense with invalid data; expect `400 VALIDATION_ERROR` and unchanged stored data.
- [ ] Register/login a second user and save `other_access_token`.
- [ ] Use `other_access_token` to get, update, and delete the first user's expense; expect `404 EXPENSE_NOT_FOUND` each time.
- [ ] Verify each user's expense list contains only their own records.

## Review Notes and Known Gaps

- `SPEC.md` lists `/api/register`, `/api/login`, and `/api/me`; the implemented and documented routes are `/api/auth/register`, `/api/auth/login`, and `/api/users/me` based on the later route requirements.
- `expense_date` is required by the API. The frontend may prefill it with today's date for convenience, but clients should always send it in create requests.
- Success responses do not all use the same JSON shape. Auth and profile endpoints return `message` plus `data`, while category and expense endpoints return resource keys such as `categories`, `expenses`, or `expense` directly.
- `PUT` is a full replacement of mutable expense fields; partial updates are not supported.
- Database column limits and `Numeric(10, 2)` precision are not fully validated before persistence.
- Unexpected server errors use Flask's default handling because global exception middleware is intentionally outside the current scope.
- Logout is client-side token removal; there is no token revocation endpoint.
