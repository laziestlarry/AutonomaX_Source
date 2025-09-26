// Minimal Express server placeholder for legacy Commander integrations.
const express = require('express');
const app = express();
const PORT = process.env.PORT || 8080;

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', source: 'server.js', redirect: 'Use FastAPI service instead.' });
});

app.use((_req, res) => {
  res.status(501).json({ error: 'Commander server is now served by the FastAPI stack.' });
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Commander placeholder listening on ${PORT}`);
  });
}

module.exports = app;
