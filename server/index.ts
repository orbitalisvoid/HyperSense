import express, { type Response, type Request, type Express } from "express";
import dotenv from "dotenv";

dotenv.config();

const app: Express = express();

const port = process.env.PORT || 9001;

app.use(express.json());

const subscriptionData = {
  kalman_filter: false,
  optical_flow: false,
  face_detection: false,
};

app.get(
  "/api/get_subscription",
  async (req: Request, res: Response): Promise<void> => {
    console.log("GET /api/get_subscription");
    res.json(subscriptionData);
  }
);

app.listen(port, () => {
  console.log(`Feature management API running at http://localhost:${port}`);
});
