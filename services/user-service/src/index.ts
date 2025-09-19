import express from 'express';
import bodyParser from 'body-parser';
import { auth } from './firebase';

const app = express();
const port = process.env.PORT || 3001;

app.use(bodyParser.json());

app.post('/register', async (req, res) => {
  const { email, password } = req.body;
  try {
    const userRecord = await auth.createUser({
      email,
      password,
    });
    res.status(201).send({ uid: userRecord.uid });
  } catch (error) {
    res.status(400).send({ error: error.message });
  }
});

app.post('/login', async (req, res) => {
  const { email, password } = req.body; // Note: In a real app, you'd validate the password
  try {
    const userRecord = await auth.getUserByEmail(email);
    // This is a simplified login. For a real app, you'd verify the password.
    // This example generates a custom token for a verified user.
    const customToken = await auth.createCustomToken(userRecord.uid);
    res.status(200).send({ token: customToken });
  } catch (error) {
    res.status(400).send({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`User service listening at http://localhost:${port}`);
});