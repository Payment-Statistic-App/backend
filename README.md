# Tuition Fee Tracking System API

REST API for control student tuition fees

## 📌 Base URL
`https://energy-cerber.ru`

This document provides an overview of the REST API endpoints available in this application. For **detailed information**, including request parameters, request bodies, and API response structures, please refer to the **full API documentation**

## 📄 DOCS
`https://energy-cerber.ru/docs`

## 🔐 Authentication
JWT token based authentication. Include token in header:
```http
Authorization: Bearer {<YOUR_TOKEN>}
```


## 📋 API Endpoints

### 👥 Users Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/users/self` | Get current user profile | ✅ |
| `GET` | `/users/students` | Get all users with role `student` | ✅ (admin, observer, accountant) |
| `POST` | `/users/login` | Authenticate user and get JWT tokens | ❌ |
| `POST` | `/users/refresh` | Refresh access token using refresh token | ✅ |
| `POST` | `/users/new` | Create new user | ✅ (admin) |
| `PUT` | `/users/edit/{user_id}` | Edit user | ✅ admin) |
| `DELETE` | `/users/delete/{user_id}` | Delete user | ✅ (admin) |

### 🏫 Infrastructure

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/infra/semesters` | Get all semesters | ❌ |
| `GET` | `/infra/groups` | Get all groups | ✅ (admin, accountant) |
| `POST` | `/infra/new_group` | Create new group | ✅ (admin) |
| `POST` | `/infra/new_semester` | Create new semester | ✅ (admin) |
| `PUT` | `/infra/edit_group/{group_id}` | Edit group info | ✅ (admin) |
| `PUT` | `/infra/edit_semester/{semester_id}` | Edit semester info | ✅ (admin) |
| `DELETE` | `/infra/delete_group/{group_id}` | Delete group | ✅ (admin) |
| `DELETE` | `/infra/delete_semester/{semester_id}` | Delete semester | ✅ (admin) |

### 💰 Operations

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/operations/new_transaction` | Record new semester payment | ✅ (student) |
| `PUT` | `/operations/add_to_group` | Add student to group | ✅ (admin) |

