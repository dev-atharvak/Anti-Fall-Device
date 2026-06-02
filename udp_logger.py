import socket, json, csv, time, os

PORT = 4210
OUTDIR = "data_wifi"
os.makedirs(OUTDIR, exist_ok=True)

label = input("Label (normal / fall): ").strip()
fname = os.path.join(OUTDIR, f"{label}_{int(time.time())}.csv")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))
sock.settimeout(2)

print("Listening on UDP port", PORT)
print("Saving to:", fname)
print("Start moving/falling. Press Ctrl+C to stop.")

with open(fname, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["t","ax","ay","az","gx","gy","gz","label"])

    try:
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                d = json.loads(data.decode("utf-8"))
                writer.writerow([d["t"], d["ax"], d["ay"], d["az"], d["gx"], d["gy"], d["gz"], label])
            except socket.timeout:
                pass
            except:
                continue
    except KeyboardInterrupt:
        print("Saved:", fname)
