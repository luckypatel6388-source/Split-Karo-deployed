# SplitKaro

AI-powered group expense splitting and UPI settlement PWA.

## Problem

Splitting bills manually is tedious...

## Solution

Scan → Verify → Split → Settle → Pay

## Features

- AI bill scanning
- Bill verification
- Group expenses
- Automatic balance calculation
- Settlement optimization
- UPI ID management
- Idempotent payment initiation
- PWA frontend

## Architecture

Frontend
↓
FastAPI
↓
MySQL
↓
AI / Payment services

## Tech Stack

Frontend:
...

Backend:
FastAPI
SQLAlchemy
MySQL
Alembic

AI:
...

Payments:
UPI URI / payment flow

## Running locally

### Backend

...

### Frontend

...

## Environment Variables

See `.env.example`.

## Demo Flow

1. Login
2. Open group
3. Scan bill
4. Review AI result
5. Confirm expense
6. View balance
7. View optimized settlement
8. Initiate payment