# train_rf_fix.py
import pandas as pd, joblib, os, numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix

os.makedirs("model", exist_ok=True)
df = pd.read_csv("data/processed/features.csv")
X = df.drop(columns=['label','source_file','start_idx'])
y = (df['label']=='fall').astype(int)
groups = df['source_file']

unique_groups = df['source_file'].nunique()
print("Unique groups (files):", unique_groups)
print("Total windows:", len(df))
print("Fall windows:", int(y.sum()), "Normal windows:", int((1-y).sum()))

clf = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)

# Decide CV strategy
use_group_cv = (unique_groups >= 4)  # require >=4 groups for group CV
if use_group_cv:
    print("Using GroupKFold with 4 splits (by source_file).")
    cv = GroupKFold(n_splits=4)
    splits = cv.split(X, y, groups)
else:
    # when groups are too few or grouped folds would be single-class, use StratifiedKFold on windows
    print("Using StratifiedKFold on windows (mix classes across folds).")
    cv = StratifiedKFold(n_splits=min(4, max(2, len(df)//50)), shuffle=True, random_state=42)
    splits = cv.split(X, y)

# Run CV and show reports
fold = 1
for tr_idx, te_idx in splits:
    clf.fit(X.iloc[tr_idx], y.iloc[tr_idx])
    preds = clf.predict(X.iloc[te_idx])
    print(f"--- Fold {fold} ---")
    print(classification_report(y.iloc[te_idx], preds, digits=3))
    fold += 1

# Final train on all data
clf.fit(X, y)
joblib.dump(clf, "model/rf_model.pkl")
print("Saved model/rf_model.pkl")
