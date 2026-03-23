import json
import numpy as np
from sklearn.preprocessing import StandardScaler
from config import DATA_DIR

DATA_PATH=DATA_DIR / "response_2.json"

with open(DATA_PATH, 'r') as f:
    data = json.load(f)

sequences = []
labels = []

for entry in data:
    seq = entry['data']['sequence']
    features = []
    for event in seq:
        hold = event['hold_time']
        flight = max(event['flight_time'], 0)  
        features.append([hold, flight])
    if len(features) >= 10:  
        sequences.append(np.array(features))
        labels.append(entry['label'])  


all_features = np.vstack(sequences)
scaler = StandardScaler()
scaler.fit(all_features)

normalized_sequences = [scaler.transform(s) for s in sequences]


window_size = 100
stride = 50
X = []
y = []

for seq, lbl in zip(normalized_sequences, labels):
    for start in range(0, len(seq) - window_size + 1, stride):
        window = seq[start:start + window_size]
        X.append(window)
        y.append(lbl)

X = np.array(X) 
y = np.array(y)  


np.save(DATA_DIR/ 'X.npy', X)
np.save(DATA_DIR/ 'y.npy', y)

print(f"Processed {len(X)} windows (features shape: {X.shape}, labels shape: {y.shape})")
print(f"Balance: {np.sum(y==1)} positive (you), {np.sum(y==0)} negative (others)")