export async function checkUrl(url) {
  let response;

  try {
    response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ urls: [url] }),
    });
  } catch {
    throw new Error("Could not reach the backend. Is it running on port 8000?");
  }

  if (response.status === 501) {
    const error = await response.json();
    throw new Error(`Model not ready: ${error.detail}`);
  }

  if (!response.ok) {
    throw new Error("Something went wrong on the server.");
  }

  const result = await response.json();
  return result.data[0].probability;
}