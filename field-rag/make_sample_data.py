"""Generate data/sample_tickets.xlsx with 200 fake field-work tickets.

Run from the project root:  python make_sample_data.py
All data is fake. Some rows intentionally contain fake phone numbers,
customer names, duplicates, blanks, and mixed date formats so that
preprocess.py (cleaning + masking) has something to work on.
"""
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

SEED = 42
N_ROWS = 200
OUTPUT_PATH = Path("data/sample_tickets.xlsx")

WILAYAH = [
    "Palembang Ilir Barat", "Palembang Kertapati", "Palembang Plaju",
    "Palembang Sukarami", "Ogan Ilir", "Banyuasin", "Muara Enim", "Lahat",
]
# Weighted so that some regions clearly have more disruptions (good for ranking questions)
WILAYAH_WEIGHTS = [20, 10, 12, 18, 8, 14, 10, 8]

TEKNISI = ["Andi", "Budi", "Citra", "Dedi", "Eko", "Fajar", "Gita", "Hendra"]
TEKNISI_WEIGHTS = [20, 15, 10, 10, 15, 10, 10, 10]

STATUS = ["Selesai", "Dalam Proses", "Pending", "Eskalasi"]
STATUS_WEIGHTS = [70, 12, 10, 8]

CUSTOMERS = ["Pak Slamet", "Bu Ratna", "Pak Joko", "Bu Dewi", "Pak Rahmat", "Bu Siti"]

# jenis_gangguan -> (min jam, max jam, list of note templates)
GANGGUAN = {
    "Kabel putus": (3.0, 10.0, [
        "Kabel drop putus akibat tertarik kendaraan. Dilakukan penyambungan ulang dan splicing.",
        "Kabel fiber putus di tiang {tiang}. Ganti kabel sepanjang {meter} meter, layanan normal kembali.",
        "Ditemukan kabel putus karena tergores ranting pohon. Kabel diganti dan dirapikan.",
    ]),
    "Redaman tinggi": (2.0, 6.0, [
        "Redaman terukur {db} dB, melebihi batas. Konektor dibersihkan dan diganti.",
        "Redaman tinggi akibat tekukan kabel di dalam rumah. Kabel diluruskan, redaman turun normal.",
        "Pengukuran OPM menunjukkan redaman tinggi di ODP. Dilakukan penggantian pigtail.",
    ]),
    "ONT mati": (1.0, 4.0, [
        "ONT tidak menyala. Adaptor rusak, diganti adaptor baru. Pelanggan {cust} sudah dikonfirmasi.",
        "ONT mati total setelah listrik padam. Dilakukan penggantian ONT baru.",
        "ONT restart terus-menerus. Dilakukan reset dan update konfigurasi, kembali normal.",
    ]),
    "Internet lambat": (1.0, 5.0, [
        "Pelanggan mengeluh internet lambat. Hasil cek, banyak perangkat terhubung. Disarankan atur ulang WiFi.",
        "Kecepatan di bawah paket. Ditemukan konfigurasi port salah, sudah diperbaiki.",
        "Internet lambat pada jam malam. Dilakukan pengecekan jalur, ditemukan kepadatan di ODP.",
    ]),
    "LOS": (2.0, 8.0, [
        "Lampu LOS menyala merah. Ditemukan konektor longgar di ODP, dikencangkan dan layanan pulih.",
        "LOS akibat kabel feeder terganggu pekerjaan galian. Dikoordinasikan dengan tim jaringan.",
        "LOS di beberapa pelanggan satu ODP. Penyebab splitter rusak, dilakukan penggantian.",
    ]),
    "Port OLT bermasalah": (4.0, 12.0, [
        "Port OLT mengalami error, beberapa pelanggan terdampak. Eskalasi ke tim NOC.",
        "Port OLT flapping. Dilakukan pemindahan pelanggan ke port cadangan.",
    ]),
    "Konektor longgar": (1.0, 3.0, [
        "Konektor longgar di rosette. Dilakukan pemasangan ulang konektor, layanan normal.",
        "Konektor kotor dan longgar. Dibersihkan dan dipasang ulang, hubungi pelanggan {cust} sudah normal.",
    ]),
}
GANGGUAN_WEIGHTS = [18, 16, 15, 14, 18, 6, 13]


def fake_phone() -> str:
    """Return a fake Indonesian mobile number."""
    return "08" + str(random.randint(1000000000, 9999999999))[:10]


def build_note(templates: list[str]) -> str:
    """Pick a template and fill its placeholders. Sometimes add a fake phone number."""
    note = random.choice(templates).format(
        tiang=f"T-{random.randint(10, 99)}",
        meter=random.randint(20, 200),
        db=round(random.uniform(-32, -26), 1),
        cust=random.choice(CUSTOMERS),
    )
    if random.random() < 0.15:
        note += f" Kontak pelanggan: {fake_phone()}."
    return note


def make_rows() -> list[dict]:
    """Create N_ROWS fake ticket rows."""
    today = date.today()
    rows = []
    for i in range(1, N_ROWS + 1):
        jenis = random.choices(list(GANGGUAN), weights=GANGGUAN_WEIGHTS)[0]
        low, high, templates = GANGGUAN[jenis]
        status = random.choices(STATUS, weights=STATUS_WEIGHTS)[0]
        tgl = today - timedelta(days=random.randint(0, 60))

        # ~10% of dates use DD/MM/YYYY to test date normalization
        tgl_str = tgl.strftime("%d/%m/%Y") if random.random() < 0.10 else tgl.strftime("%Y-%m-%d")

        # Unfinished tickets have no duration yet (blank cell)
        durasi = round(random.uniform(low, high), 1) if status in ("Selesai", "Eskalasi") else None

        rows.append({
            "ticket_id": f"TKT-{i:04d}",
            "tanggal": tgl_str,
            "wilayah": random.choices(WILAYAH, weights=WILAYAH_WEIGHTS)[0],
            "jenis_gangguan": jenis,
            "catatan_teknisi": build_note(templates),
            "teknisi": random.choices(TEKNISI, weights=TEKNISI_WEIGHTS)[0],
            "status": status,
            "durasi_jam": durasi,
        })
    return rows


def main() -> None:
    random.seed(SEED)
    rows = make_rows()

    # Add a few exact duplicates (replacing the last 5 rows) to test deduplication
    for k in range(5):
        rows[-(k + 1)] = dict(rows[k])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_excel(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_PATH}")
    print(df.head())


if __name__ == "__main__":
    main()
