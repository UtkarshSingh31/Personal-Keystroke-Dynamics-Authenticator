# DynamoAuth Backend

A real-time keystroke authentication system using machine learning models (RNN, LSTM, GRU) to detect if the user typing is the legitimate owner.

## Features

- WebSocket-based real-time keystroke detection
- Multiple ML models: RNN, LSTM, GRU
- Data collection and storage via Supabase
- Scalable preprocessing with StandardScaler

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

## Deployment on Hugging Face Spaces

### Prerequisites
- Hugging Face account
- Repository on GitHub

### Steps

1. **Create a Hugging Face Space**
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Select **SDK: API**
   - Choose appropriate license and visibility

2. **Add Secrets**
   - In Space Settings → Secrets, add:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anonymous key

3. **Push Code via Git**
   ```bash
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/dynamoauth-backend
   git push hf main
   ```

4. **Use Backend-Specific Requirements**
   - For Hugging Face, use `requirements-hf.txt` instead of the full `requirements.txt`
   - This includes only essential dependencies and avoids conflicts

### Troubleshooting

**Config Error on Hugging Face?**
- Check Space Logs for the specific error
- Ensure `SUPABASE_URL` and `SUPABASE_KEY` are set
- Verify `app.py` is in the root directory
- Make sure all model files exist in `models/` directory
- Check that `data/raw_supabase_data.json` exists

**Space won't start?**
- Remove unnecessary heavy packages (streamlit, mlflow, dvc, pynput)
- Use pinned versions in requirements.txt
- Check if torch installation completes (it's large, may take time)

### API Documentation

Once deployed at `https://YOUR_USERNAME-dynamoauth-backend.hf.space`:

- **Health Check**: `GET /`
- **WebSocket**: `wss://YOUR_USERNAME-dynamoauth-backend.hf.space/ws/detect`

Example WebSocket connection:
```javascript
const ws = new WebSocket('wss://YOUR_USERNAME-dynamoauth-backend.hf.space/ws/detect');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Is Owner:', data.is_owner);
};
```