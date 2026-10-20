# SplitKaro

SplitKaro is a group expense-sharing web app that helps people record shared bills, calculate fair balances, and organize repayment. It brings bill capture, expense tracking, and settlement suggestions into one workflow for roommates, friends, families, and travel groups.

Web Link: https://splitkarodeployed.onrender.com

It is deployed on render,so it can take around 50-55 sec to fetch.

## Product Overview

Shared expenses are easy to create and surprisingly difficult to settle. People often track payments in chats or notes, calculate balances by hand, and rely on memory to follow up. That creates avoidable mistakes, delays, and uncomfortable conversations.

SplitKaro aims to make the process clear and accountable: record an expense, confirm each person's share, see the resulting balances, and use a suggested settlement plan. Bill scanning can extract visible details from a bill image, while users review the result before it is saved.

## How It Works

1. Create an account and create or join an expense group.
2. Add an expense manually or upload a bill image for AI-assisted extraction.
3. Review and correct extracted details before confirming the expense.
4. Split costs among group members and calculate each member's net balance.
5. View suggested transfers and initiate a payment through a supported UPI flow.

## Key Capabilities

- Group-based expense tracking
- AI-assisted bill detail extraction with warnings and confidence information
- User review before scanned bill data is saved
- Expense and participant shares
- Group balance calculation
- Settlement suggestions designed to reduce the number of transfers
- UPI payment initiation flow; SplitKaro does not hold user funds
- Installable Progressive Web App (PWA)

## Technology

| Area | Technologies |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| UI and forms | Radix UI, Lucide, React Hook Form, Zod |
| Client state and requests | Zustand, TanStack Query |
| Progressive web app | `vite-plugin-pwa`, Workbox |
| Backend API | Python, FastAPI, Pydantic, Uvicorn |
| Persistence and migrations | SQLAlchemy 2, Alembic, PostgreSQL or MySQL |
| Bill extraction | Google Gemini API via the Google Gen AI SDK |
| Payments | UPI URI/payment initiation flow |

## Calculation Approach

Expense shares are recorded for participants and aggregated into each member's net balance. The settlement optimizer separates members who are owed money from members who owe money, then matches the two groups using a greedy two-pointer approach. Each transfer is the smaller of the remaining debt and credit. This produces a straightforward settlement plan with fewer transfers than asking every participant to repay every other participant separately; it is not a guarantee of the globally minimum number of transfers for every possible balance set.

Bill scanning uses an AI model to extract fields such as merchant, date, items, and totals. Because image extraction can be uncertain, the result includes warnings and confidence information and should be reviewed by the user before confirmation.

## Performance and Device Support

The frontend is a client-rendered React app built with Vite. Production builds use Vite's asset bundling, and the PWA service worker caches the application shell and static assets. This keeps repeat visits to the interface responsive and makes the app installable on supported browsers.

The app is designed to be practical on lower-end phones by keeping the core interface browser-based and avoiding a native-app installation requirement. Bill recognition and account-backed expense operations require a network connection; AI scan time also depends on the image, connection, and external service. No device-specific performance benchmark is published yet, so actual performance should be measured on representative devices before making a universal speed guarantee.

## Security and Payments

The backend uses authenticated sessions and is configured to use HTTP-only cookies. Production deployments should use HTTPS, a strong secret key, secure cookie settings, and correctly scoped frontend origins. Never commit environment files or API credentials.

UPI support is a payment initiation flow. Users complete payment through their supported payment app; SplitKaro is not a bank, wallet, or payment processor and does not itself guarantee that a transfer has settled. Confirm payment status using the application's supported flow and do not rely on a generated payment link alone as proof of payment.

## Local Development

### Requirements

- Python version compatible with the backend dependencies
- Node.js and npm
- A PostgreSQL 
- A Gemini API key for bill scanning


### Frontend

In a second terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Open the local URL printed by Vite. The development server proxies `/api` requests to the backend at `http://localhost:8000`.

### Checks

```powershell
cd frontend
npm run build
npm run lint
```

For deployment configuration, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Prototype Scope

SplitKaro is a working prototype. AI extraction depends on an external model and should be checked by the user. Production readiness requires deployment-specific security review, payment-provider and regulatory review where applicable, and performance testing on target devices and networks.

## Demo Flow

Register or log in, create or open a group, add or scan an expense, review the details, inspect balances and settlement suggestions, and initiate a UPI payment flow.
