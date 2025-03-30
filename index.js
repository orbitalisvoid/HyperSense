const express = require("express");
const app = express();

const port = 9001;

app.use(express.json());

const subscriptionData = {
  kalman_filter: false,
  optical_flow: false,
  face_detection: false,
};

app.get("/api/get_subscription", (req, res) => {
  console.log("GET /api/get_subscription");
  return res.json(subscriptionData);
});

app.listen(port, () => {
  console.log(`Feature management API running at http://localhost:${port}`);
});
