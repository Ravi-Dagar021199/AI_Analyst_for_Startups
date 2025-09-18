import express from 'express';

const app = express();
const port = process.env.PORT || 3002;

app.get('/', (req, res) => {
  res.send('Reporting Service is running');
});

app.listen(port, () => {
  console.log(`Reporting service listening at http://localhost:${port}`);
});