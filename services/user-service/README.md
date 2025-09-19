# User Service

This service is responsible for all user-related functionality, including authentication and profile management.

## Environment Variables

- `FIREBASE_PROJECT_ID`: The ID of your Firebase project.
- `FIREBASE_CLIENT_EMAIL`: The client email from your Firebase service account.
- `FIREBASE_PRIVATE_KEY`: The private key from your Firebase service account.

## Endpoints

- `POST /register`: Creates a new user.
- `POST /login`: Logs in a user.

## Running Locally

```bash
npm install
npm run start
```
