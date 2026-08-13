# Aegis360AI Framework Factory

Aegis Framework Factory converts researched regulatory and standards material into governed framework packages that Aegis360AI can consume without building a separate application for every framework.

## What it does

A source pack moves through six controlled stages:

1. Source verification and fingerprinting
2. Requirement extraction and classification
3. Mapping to the Aegis Universal Control Library
4. Assessment question and evidence generation
5. Independent QA challenge
6. Human GRC review before publication

The generated package keeps the original source wording, source reference, interpretation, mapping type and confidence, evidence expectations, QA findings and agent execution trace.

Publication is deliberately gated. A package with blocking QA findings cannot be approved, and a package cannot be published until a human reviewer records an approval decision.

## Repository layout

- `src/aegis_factory` – FastAPI service, data model, agents, persistence and publisher
- `web` – React/Vite reviewer console
- `fixtures` – safe example source material used by tests
- `tests` – pipeline, review, publishing and API tests

## Run the backend

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
uvicorn aegis_factory.api:app --reload
```

API documentation is then available at `http://127.0.0.1:8000/docs`.

## Run the reviewer console

```bash
cd web
npm install
npm run dev
```

Vite proxies `/api` to the local FastAPI service.

## Test

```bash
pytest
```

For the web client:

```bash
cd web
npm run build
```

## Production integration

The current publisher writes an immutable JSON framework package after GRC approval. The final Aegis360AI import adapter should be connected only after the production Aegis framework-import contract, authentication method and versioning rules are confirmed.

The included regulatory fixture is synthetic test material. It is not legal guidance and is not treated as an authoritative regulatory source.
