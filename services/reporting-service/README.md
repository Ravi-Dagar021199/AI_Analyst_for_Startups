# Reporting Service

This service is responsible for fetching and formatting the analysis results from the database.

## Environment Variables

- `FIREBASE_PROJECT_ID`: The ID of your Firebase project.
- `FIREBASE_CLIENT_EMAIL`: The client email from your Firebase service account.
- `FIREBASE_PRIVATE_KEY`: The private key from your Firebase service account.

## Endpoints

- `GET /reports`: Fetches all analysis reports.
- `GET /reports/:id`: Fetches a single analysis report by ID.

## Running Locally

```bash
npm install
npm run start
```
