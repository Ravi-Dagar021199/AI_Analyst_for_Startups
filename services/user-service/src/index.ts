import express from 'express';
import { auth } from './firebase';

const app = express();
app.use(express.json());

app.post('/register', async (req, res) => {
  const { email, password } = req.body;
  try {
    const userRecord = await auth.createUser({ email, password });
    res.status(201).send({ uid: userRecord.uid });
  } catch (error: any) {
    res.status(400).send({ error: error.message });
  }
});

app.post('/login', async (req, res) => {
  const { email, password } = req.body;
  try {
    const userRecord = await auth.getUserByEmail(email);
    const customToken = await auth.createCustomToken(userRecord.uid);
    res.status(200).send({ token: customToken });
  } catch (error: any) {
    res.status(400).send({ error: error.message });
  }
});

// Export the app for testing, and start the server if not in a test environment
if (process.env.NODE_ENV !== 'test') {
  const port = process.env.PORT || 3001;
  app.listen(port, () => {
    console.log(`User service listening at http://localhost:${port}`);
  });
}

export default app;
