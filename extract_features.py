# extract_features.py
import glob, os, pandas as pd, numpy as np
from scipy.signal import butter, filtfilt, welch

FS = 50  # sampling rate (esp sends ~50Hz)
WIN_SEC = 1.0
WIN = int(FS*WIN_SEC)
STEP = WIN//2  # 50% overlap

def lowpass(sig, fs=FS, cutoff=20):
    b,a = butter(4, cutoff/(0.5*fs), btype='low')
    return filtfilt(b,a,sig)

def magnitude(a,b,c):
    return (a*a + b*b + c*c)**0.5

os.makedirs("data/processed", exist_ok=True)
rows = []
files = glob.glob("data_wifi/*.csv") + glob.glob("data_raw/*.csv")
if not files:
    print("No raw files found in data_wifi/ or data_raw/. Record data first.")
    raise SystemExit(1)

for f in files:
    df = pd.read_csv(f)
    # enforce columns order if UDP logger used
    if set(['t','ax','ay','az','gx','gy','gz','label']).issubset(df.columns):
        pass
    else:
        print("Skipping", f, "- unexpected columns")
        continue

    data = df[['ax','ay','az','gx','gy','gz']].values
    n = len(data)
    for start in range(0, n - WIN + 1, STEP):
        win = data[start:start+WIN]
        ax,ay,az,gx,gy,gz = win[:,0],win[:,1],win[:,2],win[:,3],win[:,4],win[:,5]
        mag = magnitude(ax,ay,az)
        try:
            lin_mag = mag - lowpass(mag, fs=FS, cutoff=0.5)
        except:
            lin_mag = mag - np.mean(mag)
        feats = []
        for sig in (ax,ay,az,gx,gy,gz,lin_mag):
            feats += [np.mean(sig), np.std(sig), np.max(sig), np.min(sig), np.median(sig)]
        jerk = np.diff(mag)*FS
        feats += [np.mean(jerk) if len(jerk)>0 else 0, np.std(jerk) if len(jerk)>0 else 0, np.max(jerk) if len(jerk)>0 else 0]
        f_spec,P_spec = welch(lin_mag, fs=FS, nperseg=min(256,len(lin_mag)))
        feats += [f_spec[np.argmax(P_spec)] if len(P_spec)>0 else 0, np.sum(P_spec)]
        label = df['label'].iloc[start+WIN-1]
        rows.append(feats + [label, os.path.basename(f), start])

# build column names
cols = []
for sig in ['ax','ay','az','gx','gy','gz','linmag']:
    for s in ['mean','std','max','min','median']:
        cols.append(f"{sig}_{s}")
cols += ['jerk_mean','jerk_std','jerk_max','spec_domfreq','spec_energy','label','source_file','start_idx']

out = pd.DataFrame(rows, columns=cols)
out.to_csv("data/processed/features.csv", index=False)
print("Saved data/processed/features.csv -- rows:", len(out))
