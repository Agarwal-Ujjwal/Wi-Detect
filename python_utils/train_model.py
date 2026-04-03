"""
Wi-Detect — CSI-based Activity Classifier
Sliding window feature extraction + Random Forest
"""

import os
import glob
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import pickle
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── Config ────────────────────────────────────────────────────────────────────
DATASET_DIR = os.path.expanduser("~/esp/Wi-Detect/dataset")
MODEL_DIR   = os.path.expanduser("~/esp/Wi-Detect/model")
WINDOW_SIZE = 50   # frames per sample (1 second at 100 Hz)
STEP_SIZE   = 25    # 50% overlap
AMP_COLS    = [f"amp_{i}" for i in range(49)]
os.makedirs(MODEL_DIR, exist_ok=True)

# ── 1. Load all CSVs ──────────────────────────────────────────────────────────
print("Loading dataset...")
dfs = []
for f in glob.glob(os.path.join(DATASET_DIR, "*.csv")):
    try:
        df = pd.read_csv(f)
        if "label" in df.columns and len(df) > 10:
            dfs.append(df)
            print(f"  {os.path.basename(f):50s} {len(df):5d} rows  label={df['label'].iloc[0]}")
    except Exception as e:
        print(f"  Skipping {f}: {e}")

data = pd.concat(dfs, ignore_index=True)
data = data.dropna(subset=AMP_COLS)
print(f"\nTotal frames: {len(data)}")
print(data["label"].value_counts().to_string())

# ── 2. Sliding window feature extraction ─────────────────────────────────────
def extract_features(window):
    """Extract 7 statistical features per subcarrier = 49 × 7 = 343 features."""
    feats = []
    for col in AMP_COLS:
        s = window[col].values.astype(np.float32)
        feats += [
            np.mean(s),
            np.std(s),
            np.min(s),
            np.max(s),
            np.max(s) - np.min(s),          # range
            float(stats.skew(s)),
            float(stats.kurtosis(s)),
        ]
    return feats

print("\nExtracting features with sliding window...")
X, y = [], []

for label in data["label"].unique():
    subset = data[data["label"] == label].reset_index(drop=True)
    amps   = subset[AMP_COLS].values.astype(np.float32)
    n      = len(amps)
    wins   = 0
    for start in range(0, n - WINDOW_SIZE + 1, STEP_SIZE):
        window_df = subset.iloc[start:start + WINDOW_SIZE]
        X.append(extract_features(window_df))
        y.append(label)
        wins += 1
    print(f"  {label:10s}: {n} frames → {wins} windows")

X = np.array(X, dtype=np.float32)
y = np.array(y)
print(f"\nFeature matrix: {X.shape}  (samples × features)")

# ── 3. Encode labels ─────────────────────────────────────────────────────────
le = LabelEncoder()
y_enc = le.fit_transform(y)
print(f"Classes: {list(le.classes_)}")

# ── 4. Train / test split ─────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
)
print(f"\nTrain: {len(X_train)}  Test: {len(X_test)}")

# ── 5. Train Random Forest ────────────────────────────────────────────────────
print("\nTraining Random Forest...")
clf = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)
clf.fit(X_train, y_train)

# ── 6. Evaluate ───────────────────────────────────────────────────────────────
y_pred = clf.predict(X_test)
print("\n── Classification Report ──────────────────────────")
print(classification_report(y_test, y_pred, target_names=le.classes_))

cv_scores = cross_val_score(clf, X, y_enc, cv=5, scoring="f1_weighted", n_jobs=-1)
print(f"5-fold CV F1 (weighted): {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

# ── 7. Confusion matrix plot ──────────────────────────────────────────────────
cm = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(cm, cmap="Blues")
ax.set_xticks(range(len(le.classes_)))
ax.set_yticks(range(len(le.classes_)))
ax.set_xticklabels(le.classes_, fontsize=12)
ax.set_yticklabels(le.classes_, fontsize=12)
ax.set_xlabel("Predicted", fontsize=13)
ax.set_ylabel("Actual", fontsize=13)
ax.set_title("Wi-Detect Confusion Matrix", fontsize=14)
for i in range(len(le.classes_)):
    for j in range(len(le.classes_)):
        ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=14)
plt.colorbar(im)
plt.tight_layout()
plot_path = os.path.join(MODEL_DIR, "confusion_matrix.png")
plt.savefig(plot_path, dpi=150)
print(f"\nConfusion matrix saved → {plot_path}")

# ── 8. Feature importance plot ────────────────────────────────────────────────
importances = clf.feature_importances_
# Average over 7 features per subcarrier
subcarrier_imp = importances.reshape(49, 7).mean(axis=1)
fig2, ax2 = plt.subplots(figsize=(12, 4))
ax2.bar(range(49), subcarrier_imp, color="#1D9E75")
ax2.set_xlabel("Subcarrier index", fontsize=12)
ax2.set_ylabel("Mean importance", fontsize=12)
ax2.set_title("CSI Subcarrier Importance", fontsize=13)
plt.tight_layout()
imp_path = os.path.join(MODEL_DIR, "subcarrier_importance.png")
plt.savefig(imp_path, dpi=150)
print(f"Subcarrier importance saved → {imp_path}")

# ── 9. Save model ─────────────────────────────────────────────────────────────
model_path = os.path.join(MODEL_DIR, "wi_detect_model.pkl")
with open(model_path, "wb") as f:
    pickle.dump({"model": clf, "label_encoder": le,
                 "window_size": WINDOW_SIZE, "amp_cols": AMP_COLS}, f)
print(f"Model saved → {model_path}")
print("\nDone.")
