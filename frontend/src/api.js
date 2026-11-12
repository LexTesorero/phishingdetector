// Set to false when your FastAPI model is ready
const USE_MOCK = true;

function fakeScore(url) {
  let score = 0.15;

  if (!url.startsWith("https")) score += 0.2;
  if (url.length > 60) score += 0.2;
  if (url.includes("-")) score += 0.15;
  if (/login|verify|secure|account|paypal/i.test(url)) score += 0.25;

  return Math.min(score, 0.98);
}

export async function checkUrl(url) {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 600));
    return fakeScore(url);
  }

  const response = await fetch("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ urls: [url] }),
  });

  if (!response.ok) {
    throw new Error("Could not reach the server.");
  }

  const result = await response.json();
  return result.data[0].probability;
}