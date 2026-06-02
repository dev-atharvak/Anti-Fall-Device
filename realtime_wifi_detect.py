# realtime_wifi_detect.py (with Telegram alerts)
import socket, json, joblib, numpy as np, collections, time, os, requests
from scipy.signal import butter, filtfilt, welch

PORT = 4210               
MODEL = "model/rf_model.pkl"

# Telegram bot config
TELEGRAM_TOKEN = "ADD YOUR TELEGRAM BOT TOKEN HERE"
TELEGRAM_CHAT_ID = "ADD YOUR TELEGRAM CHAT ID HERE"

# Fall detection settings
FS = 50               # sampling rate (Hz)
WIN = int(1.0 * FS)   # 1-second window
STEP = WIN // 2       # 50% overlap
FALL_THRESHOLD = 0.60
CONSECUTIVE = 3       # require 3 windows above threshold
ALERT_COOLDOWN = 8.0  # seconds between alerts

# File setup
os.makedirs("logs", exist_ok=True)
os.makedirs("alerts_raw", exist_ok=True)
logfile = os.path.join("logs", f"realtime_log_{int(time.time())}.csv")
with open(logfile, "w") as f:
    f.write("ts,prob,reason\n")

def telegram_alert(text):
    """Send Telegram message"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        requests.post(url, data=payload)
        print("Telegram alert sent!")
    except Exception as e:
        print("Telegram error:", e)

def lowpass(sig, fs=FS, cutoff=20):
    b, a = butter(4, cutoff / (0.5 * fs), btype='low')
    return filtfilt(b, a, sig)

def magnitude(a, b, c):
    return np.sqrt(a*a + b*b + c*c)

def save_alert_window(arr):
    ts = int(time.time())
    fname = os.path.join("alerts_raw", f"alert_fall_{ts}.csv")
    with open(fname, "w") as f:
        f.write("i,ax,ay,az,gx,gy,gz\n")
        for i, row in enumerate(arr):
            f.write(f"{i},{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]}\n")
    print("Saved alert window:", fname)
clf = joblib.load(MODEL)
print("Loaded model:", MODEL)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))
sock.settimeout(2)

print("Listening for UDP packets on port", PORT)

buf = collections.deque(maxlen=WIN)
consec = 0
last_alert = 0

try:
    while True:
        try:
            data, addr = sock.recvfrom(2048)
            d = json.loads(data.decode('utf-8'))

            ax, ay, az = float(d['ax']), float(d['ay']), float(d['az'])
            gx, gy, gz = float(d['gx']), float(d['gy']), float(d['gz'])

            buf.append((ax, ay, az, gx, gy, gz))

        except socket.timeout:
            pass
        except Exception:
            continue

        if len(buf) >= WIN:
            arr = np.array(buf)
            axs, ays, azs = arr[:,0], arr[:,1], arr[:,2]
            gxs, gys, gzs = arr[:,3], arr[:,4], arr[:,5]

            mag = magnitude(axs, ays, azs)

            try:
                lin_mag = mag - lowpass(mag, fs=FS, cutoff=0.5)
            except:
                lin_mag = mag - np.mean(mag)

            feats = []

            for sig in (axs,ays,azs, gxs,gys,gzs, lin_mag):
                feats += [
                    float(np.mean(sig)),
                    float(np.std(sig)),
                    float(np.max(sig)),
                    float(np.min(sig)),
                    float(np.median(sig)),
                ]

            jerk = np.diff(mag) * FS
            feats += [
                float(np.mean(jerk)),
                float(np.std(jerk)),
                float(np.max(jerk)),
            ]

            f_spec, P_spec = welch(lin_mag, fs=FS, nperseg=min(256,len(lin_mag)))
            feats += [
                float(f_spec[np.argmax(P_spec)]) if len(P_spec)>0 else 0,
                float(np.sum(P_spec))
            ]

            X = np.array(feats).reshape(1,-1)
            prob = float(clf.predict_proba(X)[0][1])

            ts = time.time()

            print("Prob fall:", round(prob,3))

            with open(logfile, "a") as f:
                f.write(f"{ts},{prob},-\n")

            if prob >= FALL_THRESHOLD:
                consec += 1
            else:
                consec = 0

            if consec >= CONSECUTIVE and (time.time() - last_alert) > ALERT_COOLDOWN:
                last_alert = time.time()
                consec = 0

                print("=== FALL CONFIRMED ===", time.ctime())

                save_alert_window(arr)

                telegram_alert(
                    f"⚠ FALL DETECTED!\n"
                    f"Probability: {prob:.2f}\n"
                    f"Time: {time.ctime()}"
                )

            for _ in range(STEP):
                if len(buf)>0:
                    buf.popleft()

except KeyboardInterrupt:
    print("Exiting gracefully.")
