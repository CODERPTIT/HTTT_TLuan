import { spawn } from "node:child_process";
import { mkdtemp, mkdir, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const chrome = process.env.CHROME_PATH || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const python = process.env.ABC_PYTHON || "python";
const temporary = await mkdtemp(path.join(tmpdir(), "abc-browser-"));
const artifacts = path.join(root, "artifacts");
await mkdir(artifacts, { recursive: true });
const server = spawn(python, ["-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8765"], {
  cwd: root, windowsHide: true, stdio: "ignore", env: { ...process.env, ABC_RUNTIME: path.join(temporary, "data") }
});
const browser = spawn(chrome, ["--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
  "--remote-debugging-port=9228", "--remote-allow-origins=http://localhost:9228",
  "--user-data-dir=" + path.join(temporary, "chrome"), "about:blank"], { windowsHide: true, stdio: "ignore" });
let socket;
const pending = new Map();
let counter = 0;
const errors = [];
const results = [];

async function ready(url) {
  for (let attempt = 0; attempt < 100; attempt++) {
    try {
      const response = await fetch(url);
      if (response.ok) return response;
    } catch {}
    await new Promise(resolve => setTimeout(resolve, 150));
  }
  throw new Error("Server did not become ready: " + url);
}

function call(method, params = {}) {
  const id = ++counter;
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => { pending.delete(id); reject(new Error(method + " timed out")); }, 15000);
    pending.set(id, { resolve: value => { clearTimeout(timeout); resolve(value); }, reject });
    socket.send(JSON.stringify({ id, method, params }));
  });
}

async function evaluate(expression) {
  const result = await call("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
}

async function navigate(url) {
  await call("Page.navigate", { url: "http://127.0.0.1:8765" + url });
  for (let attempt = 0; attempt < 100; attempt++) {
    const loaded = await evaluate("document.readyState === 'complete' && location.pathname === " + JSON.stringify(url.split("?")[0]));
    if (loaded) break;
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  await evaluate("Promise.all(Array.from(document.images).map(image => { image.loading = 'eager'; return image.decode().catch(() => {}); }))");
}

async function inspect(label, screenshot = false) {
  const state = await evaluate(`({
    title: document.title,
    overflow: document.documentElement.scrollWidth > innerWidth,
    brokenImages: Array.from(document.images).filter(image => image.getAttribute('src') && (!image.complete || image.naturalWidth === 0)).map(image => image.src),
    heading: document.querySelector("h1")?.textContent,
    width: innerWidth
  })`);
  if (state.overflow || state.brokenImages.length) throw new Error(label + ": " + JSON.stringify(state));
  results.push({ label, ...state });
  if (screenshot) {
    const shot = await call("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
    await writeFile(path.join(artifacts, label + ".png"), Buffer.from(shot.data, "base64"));
  }
}

try {
  await ready("http://127.0.0.1:8765/");
  const response = await ready("http://127.0.0.1:9228/json");
  const targets = await response.json();
  socket = new WebSocket(targets.find(target => target.type === "page").webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  socket.onmessage = event => {
    const message = JSON.parse(event.data);
    if (message.id && pending.has(message.id)) {
      const task = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) task.reject(new Error(JSON.stringify(message.error)));
      else task.resolve(message.result);
    }
    if (message.method === "Runtime.exceptionThrown") errors.push(message.params.exceptionDetails.text);
  };
  await call("Page.enable");
  await call("Runtime.enable");
  await call("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
  await navigate("/");
  await inspect("home-desktop", true);
  await evaluate("document.querySelector('.add-cart button').click()");
  for (let attempt = 0; attempt < 50; attempt++) {
    if (await evaluate("document.getElementById('cart-count').textContent === '1'")) break;
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  if (!await evaluate("document.getElementById('cart-count').textContent === '1'")) throw new Error("Add-to-cart UI failed");
  await navigate("/cart");
  await inspect("cart-desktop", true);
  await evaluate("const input = document.querySelector('.cart-quantity'); input.value = '2'; input.dispatchEvent(new Event('change'))");
  await new Promise(resolve => setTimeout(resolve, 700));
  if (!await evaluate("document.querySelector('.cart-quantity').value === '2'")) throw new Error("Quantity UI failed");
  await navigate("/checkout");
  await inspect("checkout-desktop", true);
  await evaluate("document.querySelector('#checkout-form button').click()");
  for (let attempt = 0; attempt < 100; attempt++) {
    if (await evaluate("location.pathname.endsWith('/success') && document.readyState === 'complete'")) break;
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  await inspect("order-success-desktop", true);
  if (!await evaluate("document.body.textContent.includes('Order confirmed')")) throw new Error("Checkout UI failed");
  for (const url of ["/search?q=gaming+laptop", "/products/1", "/orders/1", "/orders/1/tracking"]) {
    await navigate(url);
    await inspect("desktop-" + url.replace(/[^a-z0-9]/gi, "-"));
  }
  for (const width of [390, 768]) {
    await call("Emulation.setDeviceMetricsOverride", { width, height: 844, deviceScaleFactor: 1, mobile: false });
    for (const [label, url] of [["home", "/"], ["search", "/search?q=electronics"], ["product", "/products/1"],
      ["cart-empty", "/cart"], ["tracking", "/orders/1/tracking"]]) {
      await navigate(url);
      await inspect(label + "-" + width, width === 390 && ["home", "search", "tracking"].includes(label));
    }
  }
  await navigate("/");
  await evaluate("document.getElementById('voice-open').click()");
  if (!await evaluate("document.getElementById('voice-dialog').open")) throw new Error("Voice dialog failed");
  await evaluate("document.getElementById('transcript').value='wireless headphones'; document.querySelector('#voice-dialog form[action]').requestSubmit()");
  for (let attempt = 0; attempt < 100; attempt++) {
    if (await evaluate("location.pathname === '/search' && document.readyState === 'complete'")) break;
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  if (!await evaluate("document.body.textContent.includes('Voice search')")) throw new Error("Voice fallback failed");
  if (errors.length) throw new Error(errors.join("\n"));
  await writeFile(path.join(artifacts, "browser-report.json"), JSON.stringify({ checks: results, javascriptErrors: errors }, null, 2));
  process.stdout.write(JSON.stringify({ passed: results.length, javascriptErrors: errors.length, artifacts }) + "\n");
} finally {
  if (socket) socket.close();
  browser.kill();
  server.kill();
}

