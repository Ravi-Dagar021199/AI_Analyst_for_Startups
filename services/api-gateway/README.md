# API Gateway

This service acts as the single entry point for all frontend requests. It is responsible for routing traffic to the appropriate downstream microservice.

## Endpoints

- `/api/users/...` -> `user-service`
- `/api/reports/...` -> `reporting-service`
- `/api/ingest/...` -> `ingestion-service`

## Running Locally

```bash
npm install
npm run start
```
