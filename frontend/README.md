# Frontend

React/Vite operations dashboard for Vortex SICM.

## Run locally

```bash
npm install
npm run dev
```

Build for deployment:

```bash
npm run build
```

## Structure

- `src/App.jsx` — application composition and dashboard flow
- `src/components/` — operational dashboard components grouped by concern
- `src/services/api.js` — backend API client
- `src/utils/` — presentation/data helpers
- `src/mocks/` — development/demo mock data
- `src/index.css` and `src/app-overrides.css` — application styling
- `vite.config.js` — Vite configuration

The UI consumes the backend decision-support APIs; it should not duplicate simulation or optimization logic. Keep business decisions in the backend and presentation/state concerns in the frontend.