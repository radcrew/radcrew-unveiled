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

- `HUGGINGFACE_API_KEY`: Hugging Face access token ([hf.co/settings/tokens](https://huggingface.co/settings/tokens)); you can use `HF_TOKEN` instead if you already have that set
- `HUGGINGFACE_MODEL`: Hub model id for chat (default `Qwen/Qwen2.5-1.5B-Instruct`—pick any model your account can run on [Inference Providers](https://huggingface.co/docs/inference-providers))
- `FRONTEND_ORIGIN`: frontend origin (default `http://localhost:8080`)
- `CONTENTFUL_SPACE_ID` and `CONTENTFUL_DELIVERY_TOKEN` (optional but recommended for richer FAQ context)

## Chatbot flow

- Frontend sends user question to `POST /chat`
- Backend retrieves matching snippets from static site content + Contentful entries
- Hugging Face Inference (`chatCompletion`) generates a grounded answer from those snippets
- If retrieval confidence is too low, backend returns a safe fallback with contact guidance

## Tests

- Frontend tests: `yarn test`
- Backend tests: `cd backend && yarn test`
