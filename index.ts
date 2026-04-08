import { Container, getRandom } from "@cloudflare/containers";
import { Hono } from "hono";

export class RemoveBgContainer extends Container<Env> {
  // Port the container listens on
  defaultPort = 8080;
  // Time before container sleeps due to inactivity
  sleepAfter = "10m";
  // Pass environment variables to the container
  envVars = {
    ETHGLOBAL_API_KEY: process.env.ETHGLOBAL_API_KEY,
  };

  // Optional lifecycle hooks
  onStart() {
    console.log("Container successfully started");
  }

  onStop() {
    console.log("Container successfully shut down");
  }

  onError(error: unknown) {
    console.log("Container error:", error);
  }
}

const app = new Hono<{ Bindings: Env }>();

// Forward all requests to container
app.all("*", async (c) => {
  // Load balance across containers
  const container = await getRandom(c.env.REMOVE_BG_CONTAINER, 3);
  return container.fetch(c.req.raw);
});

export default app;
