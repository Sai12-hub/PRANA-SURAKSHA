import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ----- Sample dataset -----
# Format: [age, condition_numeric, checkup_gap]
X = np.array([
    [25, 0, 30],
    [70, 2, 90],
    [55, 1, 200],
    [40, 0, 60],
    [30, 1, 15],
    [60, 2, 150],
    [80, 2, 300],
    [20, 0, 10],
    [45, 1, 90],
    [65, 2, 180],
    [50, 1, 60],
    [35, 0, 20],
])

# 1 = High Risk, 0 = Low Risk
y = np.array([0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0])

# ----- Train-test split -----
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# ----- Train model -----
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ----- Evaluate -----
y_pred = model.predict(X_test)
print("📊 Classification Report:\n", classification_report(y_test, y_pred))

# ----- Save model -----
with open("emergency_risk_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model saved as 'emergency_risk_model.pkl'")
