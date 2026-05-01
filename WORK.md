# user-service — what to build

## Responsibility
Owns user **profile** data (NOT auth — auth lives in registration-service).
Database: `user_db` on the shared Mongo.

## Endpoints to implement (mounted under `/users`)
| Method | Path             | Purpose                                  | Auth |
|--------|------------------|------------------------------------------|------|
| POST   | `/users`         | Create profile (called by registration-service after signup, or admin) | service/admin |
| GET    | `/users/{id}`    | Get profile by id                        | JWT |
| GET    | `/users/me`      | Get profile of caller (from JWT)         | JWT |
| PATCH  | `/users/{id}`    | Update profile (name, bio, avatar URL…)  | JWT (self) |
| DELETE | `/users/{id}`    | Delete profile                           | JWT (self/admin) |
| GET    | `/healthz`       | Liveness/readiness (already done)        | none |

## What it stores in Mongo
Collection `profiles`: `_id` (== user id from registration-service), `email`, `name`, `bio`, `avatar_url`, `created_at`, `updated_at`.

## How it talks to other services
- **Sync (HTTP)** — none required outbound. Other services call **into** it.
- **Async (RabbitMQ)** — exchange `events.exchange` (topic, durable, already declared on startup):
  - **Consume**: `user.registered` (published by registration-service) → create a profile row.
  - **Publish**: `user.profile.updated`, `user.profile.deleted` (notification-service consumes).
- **JWT validation**: read `JWT_SECRET` from env, verify the bearer token on every protected route. Do not re-issue tokens.

## Env you already have
`MONGO_URL`, `DB_NAME=user_db`, `JWT_SECRET`, `RABBITMQ_URL`, `PORT=8000`. Don't add new env without updating `infra/compose/docker-compose.yml` and the k8s ConfigMap/Secret.

---

## How to run locally

You need the infra stack up (Mongo + RabbitMQ + sibling services). The infra repo orchestrates everything — you do **not** run user-service alone.

### Option A — run the whole stack via infra (recommended)
```
cd ../infra
bash scripts/up-dev.sh
```
This builds + starts user-service on **http://localhost:8001** along with mongo, rabbit, and the other services.
Logs: `docker compose -p events-dev logs -f user-service`
Tear down: `bash scripts/down-all.sh`

### Option B — code-reload while iterating
1. Start only the deps from infra:
   ```
   cd ../infra
   docker compose -p events-dev -f compose/docker-compose.yml -f compose/docker-compose.dev.yml up -d mongo rabbitmq
   ```
2. Run user-service on the host:
   ```
   cd ../user-service
   python -m venv .venv && source .venv/Scripts/activate    # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   # point at host-mapped ports:
   export MONGO_URL=mongodb://localhost:27017
   export RABBITMQ_URL=amqp://guest:guest@localhost:5672/
   export DB_NAME=user_db JWT_SECRET=supersecret SERVICE_NAME=user-service
   uvicorn app.main:app --reload --port 8000
   ```

## After you change code
Rebuild only this service in the running stack:
```
cd ../infra
docker compose -p events-dev -f compose/docker-compose.yml -f compose/docker-compose.dev.yml up -d --build user-service
```

## Definition of done
- All endpoints above return correct status codes and JSON.
- `user.registered` consumer creates a profile.
- `user.profile.updated` / `user.profile.deleted` events appear in RabbitMQ UI (`http://localhost:15672`, guest/guest).
- `/healthz` returns 200; service appears Healthy in `docker ps`.
