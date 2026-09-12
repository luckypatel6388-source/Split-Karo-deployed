# SplitKaro Deployment

## Recommended layout

- Render Web Service: FastAPI backend
- Render PostgreSQL: application database
- Netlify or Render Static Site: Vite frontend

## Render backend

1. Push the repository to GitHub.
2. In Render, choose **New > Blueprint** and select the repository.
3. Render will read `render.yaml` from the repository root.
4. Set `FRONTEND_URL` to the final frontend origin. Multiple origins may be
   supplied as a comma-separated value for a production site and preview site.
5. Set `AI_API_KEY` only if bill scanning is enabled.
6. Deploy and check `https://<backend-host>/health`.

The backend build runs migrations before starting Uvicorn:

```text
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Frontend

For Netlify, use the repository root as the base directory. The included
`netlify.toml` sets the frontend base to `frontend`, builds with `npm run build`,
and publishes `dist`.

Set this environment variable in the hosting dashboard:

```text
VITE_API_BASE_URL=https://<backend-host>/api/v1
```

Do not set this to `/api/v1` when the frontend is hosted separately from the
backend. That relative value is only for local Vite development through the
proxy in `vite.config.ts`.

The same value can be used for a Render Static Site. Do not use `/api/v1` for a
separately hosted frontend unless a reverse proxy is configured.

## Required backend variables

Copy `backend/.env.example` as a reference. In production, set:

- `DATABASE_URL` to the Render PostgreSQL connection string
- `SECRET_KEY` to a long random value
- `FRONTEND_URL` to the deployed frontend URL
- `COOKIE_SECURE=true`
- `COOKIE_SAMESITE=none` when the frontend is hosted on Netlify or another
   different domain
- `DEBUG=false`
- `AI_API_KEY` and `AI_MODEL` when bill scanning is enabled

Never commit `.env` files or paste real credentials into this document.

## Release checks

```text
cd backend
alembic upgrade head
python -m compileall app migrations

cd ../frontend
npm ci
npm run build
```

After deployment, verify `/health`, registration/login, group creation, and a
complete expense-to-settlement flow using a non-production test account.