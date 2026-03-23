import torch
import torch.nn as nn
from config import MODELS_DIR, JSON_FILE
import json
import numpy as np
from sklearn.preprocessing import StandardScaler

class Keystroke_Model(nn.Module):
    def __init__(self, model_type, dropout=0.3, input_size=2, hidden_size=128, num_layers=2):
        super().__init__()
        if model_type == "RNN":
            self.rnn = nn.RNN(input_size, hidden_size, num_layers, batch_first=True, bidirectional=True)
        elif model_type == "LSTM":
            self.rnn = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, bidirectional=True)
        elif model_type == "GRU":
            self.rnn = nn.GRU(input_size, hidden_size, num_layers, batch_first=True, bidirectional=True)
        else:
            raise ValueError("Invalid Model Type")
            
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size * 2, 1)

    def forward(self, X):
        out, _ = self.rnn(X)
        out = self.dropout(out[:, -1, :])
        out = self.fc(out)
        return out


class ModelManager:
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self._load_scaler()
        self._load_models()

    def _load_scaler(self):
        try:
            with open(JSON_FILE, 'r') as f:
                data = json.load(f)
            sequences = []
            for entry in data:
                seq = entry['data']['sequence']
                features = []
                for event in seq:
                    hold = event['hold_time']
                    flight = max(event['flight_time'], 0)
                    features.append([hold, flight])
                if len(features) >= 10:
                    sequences.append(np.array(features))
            if sequences:
                all_features = np.vstack(sequences)
                self.scaler.fit(all_features)
                print("Scaler successfully fitted.")
        except Exception as e:
            print(f"Failed to load scaler data: {e}")

    def _load_models(self):
        for m_type in ["RNN", "LSTM", "GRU"]:
            model = Keystroke_Model(model_type=m_type)
            model_path = MODELS_DIR / f"{m_type}_seed42.pth"
            if model_path.exists():
                try:
                    model.load_state_dict(torch.load(model_path, weights_only=True))
                    model.eval()
                    self.models[m_type] = model
                    print(f"Loaded {m_type} from {model_path}")
                except Exception as e:
                    print(f"Could not load state dict for {m_type}: {e}")
            else:
                print(f"Model file not found: {model_path}")

    def predict(self, model_type, sequence_features):
        """
        sequence_features: shape (100, 2) array of [hold, flight]
        Returns: True if owner, False if not, and probability.
        """
        if model_type not in self.models:
            raise ValueError(f"Model {model_type} not loaded.")
        
        # scale features exactly as during training
        scaled_seq = self.scaler.transform(sequence_features)
        tensor_seq = torch.tensor(scaled_seq, dtype=torch.float32).unsqueeze(0) # shape: (1, 100, 2)
        
        model = self.models[model_type]
        with torch.no_grad():
            logits = model(tensor_seq).squeeze()
            prob = torch.sigmoid(logits).item()
        
        # Typically > 0.5 is owner
        return prob > 0.5, prob

model_manager = ModelManager()
