# RadCrew Unveiled

Marketing site for RadCrew with a FAQ chatbot.

## Frontend

- Install dependencies: `yarn install`
- Start dev server: `yarn dev`
- Frontend env: copy `.env.example` to `.env`

## Chatbot Backend

- Move to backend folder: `cd backend`
- Install dependencies: `yarn install`
- Configure env: copy `backend/.env.example` to `backend/.env`
- Start backend dev server: `yarn dev`

### Required backend env vars

- `GEMINI_API_KEY`: Google Gemini API key
- `FRONTEND_ORIGIN`: frontend origin (default `http://localhost:8080`)
- `CONTENTFUL_SPACE_ID` and `CONTENTFUL_DELIVERY_TOKEN` (optional but recommended for richer FAQ context)

## Chatbot flow

- Frontend sends user question to `POST /chat`
- Backend retrieves matching snippets from static site content + Contentful entries
- Gemini generates a grounded answer from those snippets
- If retrieval confidence is too low, backend returns a safe fallback with contact guidance

## Tests

- Frontend tests: `yarn test`
- Backend tests: `cd backend && yarn test`
