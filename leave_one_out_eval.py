# leave_one_out_eval.py
import pandas as pd, numpy as np, joblib, os
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support

df = pd.read_csv("data/processed/features.csv")
print("Loaded features:", df.shape)
files = sorted(df['source_file'].unique())
print("Files:", files)

results = []
overall_cm = np.zeros((2,2), dtype=int)

for held in files:
    train = df[df['source_file'] != held].reset_index(drop=True)
    test  = df[df['source_file'] == held].reset_index(drop=True)
    if len(test) == 0 or len(train) == 0:
        print("Skipping", held, " (no data )")
        continue

    Xtr = train.drop(columns=['label','source_file','start_idx'])
    ytr = (train['label'] == 'fall').astype(int)
    Xte = test.drop(columns=['label','source_file','start_idx'])
    yte = (test['label'] == 'fall').astype(int)

    clf = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)
    clf.fit(Xtr, ytr)
    preds = clf.predict(Xte)

    p,r,f,_ = precision_recall_fscore_support(yte, preds, average='binary', zero_division=0)
    rep = classification_report(yte, preds, digits=3, zero_division=0)
    cm = confusion_matrix(yte, preds)
    overall_cm += cm

    print("=== Held-out file:", held, " ===")
    print("Test size:", len(yte), "  falls:", int(yte.sum()), " normals:", int((1-yte).sum()))
    print(rep)
    results.append((held, len(yte), int(yte.sum()), p, r, f))
    print("Confusion matrix:\n", cm)
    print("\n")

# Summary across files
print("=== Summary per-file ===")
for r in results:
    print("File:", r[0], " n:",r[1], "falls:",r[2], "  precision:", round(r[3],3), " recall:", round(r[4],3), " f1:", round(r[5],3))
print("\nOverall confusion matrix across all held-out tests:\n", overall_cm)
