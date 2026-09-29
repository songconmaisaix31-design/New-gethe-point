import { writeFileSync } from "node:fs";


const [port, url, screenshotPath] = process.argv.slice(2);
if (!port || !url || !screenshotPath) {
  throw new Error("Usage: node verify_responsive.mjs <port> <url> <screenshot-path>");
}

const targets = await fetch(`http://127.0.0.1:${port}/json/list`).then((response) => response.json());
const page = targets.find((target) => target.type === "page");
if (!page) throw new Error("Chrome DevTools Protocol exposed no page target");

const socket = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  socket.addEventListener("open", resolve, { once: true });
  socket.addEventListener("error", reject, { once: true });
});

let nextId = 1;
const pending = new Map();
socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  if (!message.id) return;
  const request = pending.get(message.id);
  if (!request) return;
  pending.delete(message.id);
  if (message.error) request.reject(new Error(message.error.message));
  else request.resolve(message.result);
});

function send(method, params = {}) {
  const id = nextId++;
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    socket.send(JSON.stringify({ id, method, params }));
  });
}

await send("Page.enable");
await send("Runtime.enable");
await send("Emulation.setDeviceMetricsOverride", {
  width: 390,
  height: 844,
  deviceScaleFactor: 1,
  mobile: true,
  screenWidth: 390,
  screenHeight: 844,
});
await send("Page.navigate", { url });
await new Promise((resolve) => setTimeout(resolve, 1000));

const evaluation = await send("Runtime.evaluate", {
  expression: `JSON.stringify({
    viewportWidth: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    cardCount: document.querySelectorAll('.card').length,
    objectCount: document.querySelectorAll('object').length
  })`,
  returnByValue: true,
});
const metrics = JSON.parse(evaluation.result.value);
if (metrics.viewportWidth !== 390 || metrics.scrollWidth > metrics.viewportWidth) {
  throw new Error(`Responsive layout failed: ${JSON.stringify(metrics)}`);
}
if (metrics.cardCount !== 24 || metrics.objectCount !== 24) {
  throw new Error(`Preview content failed: ${JSON.stringify(metrics)}`);
}

const screenshot = await send("Page.captureScreenshot", {
  format: "png",
  captureBeyondViewport: false,
});
writeFileSync(screenshotPath, Buffer.from(screenshot.data, "base64"));
console.log(JSON.stringify({ status: "passed", horizontalOverflow: false, ...metrics }, null, 2));
socket.close();
