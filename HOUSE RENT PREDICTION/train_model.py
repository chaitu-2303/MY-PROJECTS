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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Use the new 10k dataset
DATASET_PATH = os.path.join(
    BASE_DIR,
    "House_Rent_10k_major_cities.csv"
)

# Where to save the trained model
MODEL_PATH = os.path.join(
    BASE_DIR,
    "house_rent_model.pkl"
)

# =========================
# LOAD DATA
# =========================

print("Loading data from:", DATASET_PATH)
df = pd.read_csv(DATASET_PATH)

print("Raw shape:", df.shape)

# Make sure expected columns exist
required_cols = [
    "Size",
    "BHK",
    "Bathroom",
    "City",
    "Furnishing Status",
    "Tenant Preferred",
    "Area Type",
    "Rent",
]
missing = [c for c in required_cols if c not in df.columns]

if missing:
    raise ValueError(f"Missing columns in CSV: {missing}")

# Ensure Rent is numeric (it already is from generator, but just in case)
df["Rent"] = pd.to_numeric(df["Rent"], errors="coerce")

# Drop rows with missing values in important columns
df = df.dropna(subset=required_cols)

print("Cleaned shape:", df.shape)

# =========================
# FEATURES / TARGET
# =========================

X = df[["Size", "BHK", "Bathroom", "City",
        "Furnishing Status", "Tenant Preferred", "Area Type"]]
y = df["Rent"]

numeric_features = ["Size", "BHK", "Bathroom"]
categorical_features = ["City", "Furnishing Status", "Tenant Preferred", "Area Type"]

# =========================
# PREPROCESSING PIPELINE
# =========================

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

# 100 trees is enough for 10k rows and still fast
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=None,
    n_jobs=-1,
    random_state=42,
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
# Compute RMSE manually to avoid signature differences across sklearn versions
rmse = mean_squared_error(y_test, y_pred) ** 0.5
r2 = r2_score(y_test, y_pred)

print(f"RMSE: {rmse:,.2f}")
print(f"R²: {r2:.4f}")

# =========================
# SAVE MODEL
# =========================

print("Saving model to:", MODEL_PATH)
joblib.dump(pipeline, MODEL_PATH)

print("Done. Trained model saved as 'house_rent_model.pkl'")
