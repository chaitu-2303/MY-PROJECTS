# train_model.py

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# =========================
# CONFIG
# =========================

# Change this if your file name is different
DATASET_PATH = os.path.join(
    os.path.dirname(__file__),
    "House_Rent_10M_balanced_40cities.csv"
)

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "house_rent_model.pkl"
)

# How many rows to use for training (10M is huge)
N_ROWS = 500_000   # you can increase if your PC is strong

# =========================
# LOAD DATA
# =========================

print("Loading data from:", DATASET_PATH)
df = pd.read_csv(DATASET_PATH, nrows=N_ROWS)

print("Shape used for training:", df.shape)

# Make sure column names match your generated dataset
# and your Flask app: Size, BHK, Bathroom, City, Furnishing Status,
# Tenant Preferred, Area Type, Rent

required_cols = [
    "Size",
    "BHK",
    "Bathroom",
    "City",
    "Furnishing Status",
    "Tenant Preferred",
    "Area Type",
    "Rent"
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns in CSV: {missing}")

# Drop rows with missing target
df = df.dropna(subset=["Rent"])

X = df[["Size", "BHK", "Bathroom", "City",
        "Furnishing Status", "Tenant Preferred", "Area Type"]]
y = df["Rent"]

# =========================
# PREPROCESSING PIPELINE
# =========================

numeric_features = ["Size", "BHK", "Bathroom"]
categorical_features = ["City", "Furnishing Status", "Tenant Preferred", "Area Type"]

numeric_transformer = Pipeline(
    steps=[("scaler", StandardScaler())]
)

categorical_transformer = Pipeline(
    steps=[("onehot", OneHotEncoder(handle_unknown="ignore"))]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ]
)

# =========================
# MODEL
# =========================

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=None,
    n_jobs=-1,
    random_state=42
)

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model),
    ]
)

# =========================
# TRAIN / TEST SPLIT
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Training shape:", X_train.shape)
print("Testing shape:", X_test.shape)

# =========================
# TRAIN
# =========================

print("Training model...")
pipeline.fit(X_train, y_train)

# =========================
# EVALUATE
# =========================

y_pred = pipeline.predict(X_test)
rmse = mean_squared_error(y_test, y_pred, squared=False)
r2 = r2_score(y_test, y_pred)

print(f"RMSE: {rmse:,.2f}")
print(f"R²: {r2:.4f}")

# =========================
# SAVE MODEL
# =========================

print("Saving model to:", MODEL_PATH)
joblib.dump(pipeline, MODEL_PATH)

print("Done. Trained model saved as 'house_rent_model.pkl'")
