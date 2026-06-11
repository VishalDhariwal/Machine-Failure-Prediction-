const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

/**
 * Send sensor data to ML backend for prediction
 */
export async function predict(sensorData) {
  const response = await fetch(`${BASE_URL}/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(sensorData),
  });

  if (!response.ok) {
    throw new Error(`Backend error: ${response.status}`);
  }

  return response.json();
}

/**
 * Upload CSV for batch prediction
 */
export async function predictCSV(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${BASE_URL}/predict_csv`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`CSV prediction failed: ${response.status}`);
  }

  return response.json();
}

export async function predictManual(payload) {
  const res = await fetch(`${BASE_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Manual prediction failed");
  }

  return res.json();
}

export async function chatWithBot(
  question,
  latest,
  prediction,
  history
) {
  const response = await fetch(
    `${BASE_URL}/chat`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        question,

        machine_state: {
          latest,
          prediction,
          history,
        },
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      `Chat failed: ${response.status}`
    );
  }

  return response.json();
}