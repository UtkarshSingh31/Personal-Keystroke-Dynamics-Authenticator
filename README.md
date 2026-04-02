# DynamoAuth Backend

A real-time keystroke authentication system using machine learning models (RNN, LSTM, GRU) to detect if the user typing is the legitimate owner.

## Features

- WebSocket-based real-time keystroke detection
- Multiple ML models: RNN, LSTM, GRU
- Data collection and storage via Supabase
- Scalable preprocessing with StandardScaler

## Setup

### Environment Variables

Set the following secrets in your Hugging Face Space:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key

### Files Structure

- `app.py`: Main entry point for the FastAPI application
- `app/main.py`: FastAPI app definition
- `app/api/websockets.py`: WebSocket endpoint for detection
- `app/core/model_manager.py`: ML model management and prediction
- `config.py`: Configuration settings
- `data/raw_supabase_data.json`: Training data for scaler fitting
- `models/`: Pre-trained PyTorch models (RNN, LSTM, GRU)

## API Endpoints

- `GET /`: Health check
- `WebSocket /ws/detect`: Real-time keystroke authentication

### WebSocket Usage

Connect to `/ws/detect` and send JSON messages with keystroke data:

```json
{
  "event": {
    "hold_time": 0.085,
    "flight_time": 0.123
  }
}
```

Response:
```json
{
  "status": "success",
  "is_owner": true,
  "probability": 0.87
}
```

## Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables in `.env`
3. Run: `python app.py`

## Deployment

This app is configured for deployment on Hugging Face Spaces as an API space.