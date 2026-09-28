import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import RISK_BINS, RISK_ORDER, SAMPLE_PATH  # noqa: E402

N_PATIENTS = 40
rng = np.random.default_rng(7)

FIRST = ["Ayesha", "Omar", "Sara", "Hamza", "Nida", "Bilal", "Zainab", "Usman",
         "Hina", "Farhan", "Maryam", "Ali", "Sana", "Imran", "Laiba", "Kamran"]
LAST = ["Khan", "Ahmed", "Malik", "Sheikh", "Raza", "Butt", "Iqbal", "Chaudhry",
        "Hussain", "Qureshi", "Siddiqui", "Mirza"]


def patient_rows(i):
    pid = f"P{i:03d}"
    name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
    age = int(rng.integers(28, 86))
    gender = str(rng.choice(["F", "M"]))

    base_sys = rng.normal(124, 19) + (age - 50) * 0.3
    base_glu = rng.normal(102, 24) + (age - 50) * 0.25
    base_hr = rng.normal(74, 8)
    sys_drift = rng.normal(0.4, 1.4)    # mmHg per visit
    glu_drift = rng.normal(0.5, 1.8)    # mg/dL per visit

    n_visits = int(rng.integers(6, 13))
    days = np.sort(rng.choice(np.arange(0, 330), n_visits, replace=False))
    dates = pd.Timestamp("2025-01-06") + pd.to_timedelta(days, unit="D")

    rows = []
    for k, date in enumerate(dates):
        sys_bp = base_sys + sys_drift * k + rng.normal(0, 4)
        dia_bp = 0.6 * sys_bp + rng.normal(0, 3)
        hr = base_hr + rng.normal(0, 4)
        glucose = base_glu + glu_drift * k + rng.normal(0, 6)
        temp = rng.normal(36.8, 0.25)
        spo2 = np.clip(rng.normal(97.2, 1.1), 90, 100)
        score = 0.4 * (age - 30) + 0.8 * (sys_bp - 100) + 0.35 * (glucose - 80) + 0.15 * (hr - 60)
        score = float(np.clip(score + rng.normal(0, 3), 0, 100))
        rows.append({
            "patient_id": pid,
            "patient_name": name,
            "age": age,
            "gender": gender,
            "visit_date": date.strftime("%Y-%m-%d"),
            "systolic_bp": round(sys_bp),
            "diastolic_bp": round(dia_bp),
            "heart_rate": round(hr),
            "glucose": round(glucose),
            "temperature": round(temp, 1),
            "spo2": round(spo2),
            "risk_score": round(score, 1),
        })
    return rows


def main():
    rows = [r for i in range(1, N_PATIENTS + 1) for r in patient_rows(i)]
    df = pd.DataFrame(rows)
    df["risk_level"] = pd.cut(df["risk_score"], bins=RISK_BINS, labels=RISK_ORDER, right=False).astype(str)

    SAMPLE_PATH.parent.mkdir(exist_ok=True)
    df.to_csv(SAMPLE_PATH, index=False)

    latest = df.sort_values("visit_date").groupby("patient_id").tail(1)
    print(f"wrote {len(df)} rows for {N_PATIENTS} patients -> {SAMPLE_PATH}")
    print("latest-visit risk mix:", latest["risk_level"].value_counts().to_dict())


if __name__ == "__main__":
    main()
