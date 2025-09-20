import express from 'express';
import cors from 'cors';
import { db } from './firebase';

const app = express();
const port = process.env.PORT || 3002;

app.use(cors()); // Enable CORS for all routes

// Get all reports
app.get('/reports', async (req, res) => {
  try {
    const snapshot = await db.collection('analysis_results').orderBy('created_at', 'desc').get();
    const reports = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    res.status(200).send(reports);
  } catch (error: any) {
    res.status(500).send({ error: error.message });
  }
});

// Get a single report by ID
app.get('/reports/:id', async (req, res) => {
  try {
    const docRef = db.collection('analysis_results').doc(req.params.id);
    const doc = await docRef.get();
    if (!doc.exists) {
      res.status(404).send({ error: 'Report not found' });
    } else {
      res.status(200).send({ id: doc.id, ...doc.data() });
    }
  } catch (error: any) {
    res.status(500).send({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Reporting service listening at http://localhost:${port}`);
});