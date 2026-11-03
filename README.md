# DynamoAuth

**DynamoAuth** is a real-time, AI-powered keystroke-dynamics authentication system. It learns how a person types from timing patterns rather than relying only on passwords or typed content.

## Live Demo

Try the deployed application here: **[dynammoauth.vercel.app](https://dynammoauth.vercel.app/)**

The dashboard captures typing events in the browser and displays authentication confidence in real time.

## What It Does

DynamoAuth measures two behavioral biometric signals:

- **Hold time** - how long a key is pressed.
- **Flight time** - the time between consecutive keystrokes.

These features are processed as fixed-length sequences and evaluated by recurrent neural-network models. The backend communicates with the frontend over a WebSocket so predictions can be updated while the user types.

## Binary Classification

This project performs **binary classification**:

| Class | Meaning |
| --- | --- |
| `1` / `true` | The typing pattern matches the legitimate owner |
| `0` / `false` | The typing pattern does not match the legitimate owner |

Each model returns an owner probability between `0` and `1`. A probability above `0.5` is classified as `owner`; otherwise, it is classified as `impostor`. The response also includes the selected model and the probability used by the dashboard.

## Models

The backend currently supports three bidirectional PyTorch sequence models:

- **RNN** - recurrent baseline for temporal patterns.
- **LSTM** - captures longer-term dependencies in typing behavior.
- **GRU** - a lighter recurrent alternative with strong sequence performance.

The active model can be selected from the dashboard or changed through the WebSocket connection.

## System Flow

```text
Browser keyboard events
        |
        v
WebSocket /ws/detect
        |
        v
Hold-time and flight-time features
        |
        v
StandardScaler preprocessing
        |
        v
RNN / LSTM / GRU inference
        |
        v
Owner probability and binary decision
        |
        v
Real-time dashboard
```

## Technology Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, FastAPI, Uvicorn, WebSockets
- **Machine learning:** PyTorch, NumPy, scikit-learn
- **Data storage:** Supabase
- **Deployment:** Docker and Hugging Face Spaces-compatible backend

## Project Structure

```text
app.py                       Application entry point
app/main.py                  FastAPI application
app/api/websockets.py       Real-time detection WebSocket
app/core/model_manager.py   Scaling, model loading, and prediction
frontend/                    Authentication dashboard
data/                        Training data and DVC metadata
models/                      Trained RNN, LSTM, and GRU weights
notebook/                    Data collection and model training workflows
server.py                    Separate Supabase data-collection API
```

## WebSocket API

Connect to:

```text
ws://<host>/ws/detect
```

Send keystroke timing events:

```json
{
  "event": {
    "hold_time": 0.085,
    "flight_time": 0.123
  }
}
```

The backend responds with a real-time classification result:

```json
{
  "status": "success",
  "is_owner": true,
  "probability": 0.87,
  "model_used": "LSTM"
}
```

The detector maintains a sliding window of up to 100 timing events and pads shorter sequences for inference.

## Run Locally

1. Clone the repository and enter the project directory.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the required environment variables in `.env` when using the Supabase data-collection path:

   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_key
   ```

5. Start the backend:

   ```bash
   python app.py
   ```

The API is served locally on port `7860` by default. Open the frontend separately or use the deployed demo.

## What This Project Demonstrates

DynamoAuth demonstrates practical experience with:

- Behavioral biometrics and keystroke-dynamics feature engineering.
- Binary classification and probability-based authentication decisions.
- Recurrent deep-learning architectures for time-series data.
- Real-time WebSocket inference with FastAPI.
- Data preprocessing, scaling, model loading, and deployment.
- Building an interactive authentication dashboard.

## Future Roadmap

The next version is planned to move from a single owner-versus-impostor model toward **multi-user authentication with learned embeddings**:

- Generate a compact typing embedding for each user.
- Store enrolled user profiles and compare new sessions against them.
- Support multiple authentication factors, such as password plus keystroke behavior.
- Add user enrollment, profile management, and re-enrollment workflows.
- Use metric learning or Siamese/triplet networks for similarity-based verification.
- Combine keystroke embeddings with device, session, and risk signals.
- Add adaptive thresholds, drift detection, and continuous re-authentication.
- Improve privacy with encrypted biometric templates and retention controls.
- Measure false-acceptance rate, false-rejection rate, equal-error rate, and latency across users.

## Important Note

Keystroke dynamics are behavioral biometric signals and should complement, not automatically replace, secure primary authentication. Production deployments should include consent, privacy safeguards, encrypted storage, rate limiting, and fallback authentication.
