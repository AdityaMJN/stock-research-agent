# Frontend

## Run locally

From this folder:

```bash
npm install
npm run dev
```

The Vite dev server will start at http://localhost:5173/.

## Environment

Copy `.env.example` to `.env` if you need to override defaults:

```bash
cp .env.example .env
```

Default settings:
- `VITE_API_BASE_URL=http://localhost:8000/api/v1`
- `VITE_USE_MOCKS=true`

To use live API data, set:

```env
VITE_USE_MOCKS=false
```
