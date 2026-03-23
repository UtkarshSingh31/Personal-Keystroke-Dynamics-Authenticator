from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import numpy as np
from app.core.model_manager import model_manager

router = APIRouter()

@router.websocket("/ws/detect")
async def websocket_detect(websocket: WebSocket):
    await websocket.accept()
    
    model_type = "RNN" # default
    window_size = 100
    sequence_buffer = []

    try:
        while True:
            data = await websocket.receive_json()
            
            # Client can switch active model on the fly
            if "model_type" in data:
                model_type = data["model_type"]
                continue
                
            if "event" in data:
                evt = data["event"]
                sequence_buffer.append([evt["hold_time"], evt["flight_time"]])
                
                # Maintain sliding window of size exactly `window_size` (100).
                if len(sequence_buffer) > window_size:
                    sequence_buffer.pop(0) # remove oldest
                
                if len(sequence_buffer) < 2:
                    await websocket.send_json({
                        "status": "waiting",
                        "msg": "Waiting for at least 2 keystrokes..."
                    })
                    continue
                
                # For smooth real-time visualization when < 100 items, we zero-pad the sequence.
                # In training: constant 100 window size was used. 
                seq_array = np.array(sequence_buffer)
                if len(seq_array) < window_size:
                    pad_len = window_size - len(seq_array)
                    seq_array = np.pad(seq_array, ((pad_len, 0), (0, 0)), mode='constant')

                is_owner, prob = model_manager.predict(model_type, seq_array)
                
                await websocket.send_json({
                    "status": "success",
                    "is_owner": is_owner,
                    "probability": prob,
                    "model_used": model_type
                })
                
    except WebSocketDisconnect:
        print("Client disconnected from WebSocket")
    except Exception as e:
        print(f"WebSocket Error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
