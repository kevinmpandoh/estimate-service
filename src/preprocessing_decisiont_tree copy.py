import pandas as pd
import numpy as np
import os
import re

# ------------------------------
# KONFIGURASI
# ------------------------------
DATA_PATH = "data/dataset.xlsx"
OUTPUT_DIR = "output"
OUTPUT_EXCEL = os.path.join(OUTPUT_DIR, "tahapan_preprocessing.xlsx")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ------------------------------
# LOAD DATA AWAL
# ------------------------------
print("📥 Membaca dataset...")
df = pd.read_excel(DATA_PATH, sheet_name="Sheet1")
df_raw = df.copy()

# ------------------------------
# 1️⃣ HAPUS KOLOM TIDAK DIGUNAKAN
# ------------------------------
print("🧹 Menghapus kolom tidak digunakan...")
kolom_hapus = ['TANGGAL', 'TAHUN', 'BULAN']
for kol in kolom_hapus:
    if kol in df.columns:
        df = df.drop(columns=[kol])

df_after_drop = df.copy()

# ------------------------------
# 2️⃣ HAPUS DATA TIDAK VALID
# ------------------------------
print("🚫 Menghapus data tidak valid (simbol ?, +, ,)...")
invalid_keywords = ['?', ',', '+']
escaped_keywords = [re.escape(k) for k in invalid_keywords]
invalid_counts = 0

for col in ['MEREK', 'TIPE UNIT', 'KERUSAKAN']:
    before = len(df)
    df[col] = df[col].astype(str)
    df = df[~df[col].str.contains('|'.join(escaped_keywords), na=False)]
    invalid_counts += before - len(df)

df_after_invalid = df.copy()

# ------------------------------
# 3️⃣ TAMBAHKAN KATEGORI ENTRY LEVEL
# ------------------------------
print("📱 Menambahkan kategori entry level berdasarkan MEREK + TIPE UNIT...")

# Gabungkan kolom merek dan tipe unit
df_after_invalid["MEREK"] = df_after_invalid["MEREK"].astype(str).str.strip().str.upper()
df_after_invalid["TIPE UNIT"] = df_after_invalid["TIPE UNIT"].astype(str).str.strip().str.upper()
df_after_invalid["MEREK_TIPE"] = df_after_invalid["MEREK"] + " " + df_after_invalid["TIPE UNIT"]

entry_map = {
    "SAMSUNG": {
        "Entry Level": [
            "A0", "A01", "A02", "A03", "A04", "A05", "A06", "J1", "J2", "J3", "J4", "J5", "M01", "M02", "M10", "M12", "M13"
        ],
        "Mid Level": [
            "A10", "A11", "A12", "A13", "A14", "A15", "A20", "A21", "A22", "A23", "A24", "M20", "M21", "M30", "M31", "A30", "A31", "A32", "A33", "A34", "A35", "A50", "A51", "A52", "A53", "A54"
        ],
        "High Level": [
            "S8", "S9", "S10", "S20", "S21", "S22", "S23", "S24", "NOTE 8", "NOTE 10", "NOTE 20", "FLIP", "FOLD"
        ]
    },
    "VIVO": {
        "Entry Level": ["Y01", "Y02", "Y03", "Y12", "Y15", "Y16", "Y17", "Y20", "Y21", "Y22"],
        "Mid Level": ["Y27", "Y30", "Y33", "Y35", "Y36", "Y50", "Y53", "Y55"],
        "High Level": ["V11", "V15", "V17", "V19", "V20", "V21", "V23", "V25", "V27"]
    },
    "OPPO": {
        "Entry Level": ["A01", "A03", "A05", "A11K", "A12", "A15", "A16", "A17", "A18"],
        "Mid Level": ["A31", "A33", "A37", "A5", "A52", "A53", "A54", "A57", "A58", "A76", "A77", "A78"],
        "High Level": ["F5", "F7", "F9", "R17", "RENO 3", "RENO 5", "RENO 6", "RENO 7", "RENO 8", "RENO 10", "RENO 11", "FIND X"]
    },
    "REDMI": {
        "Entry Level": ["5A", "6A", "7A", "8A", "9A", "A1", "A2", "A3"],
        "Mid Level": ["9C", "9T", "10", "10A", "10C", "12C", "13C", "NOTE 10", "NOTE 11", "NOTE 12", "NOTE 13"],
        "High Level": ["NOTE 12 PRO", "NOTE 13 PRO", "NOTE 13 PRO+", "NOTE 9 PRO", "NOTE 8 PRO", "NOTE 7 PRO"]
    },
    "REALME": {
        "Entry Level": ["C1", "C2", "C3", "C11", "C12", "C15", "C17", "C20", "C21", "C25", "C30", "C33", "C35", "C50"],
        "Mid Level": ["5", "5I", "6", "6I", "7", "7I", "8", "8I", "9", "9I", "9 PRO", "NARZO 20", "NARZO 50"],
        "High Level": ["GT", "GT MASTER", "10", "11", "11 PRO", "11 PLUS", "9 PRO+", "XT"]
    },
    "POCO": {
        "Entry Level": ["C3", "C40", "C50", "C55", "C65"],
        "Mid Level": ["M2", "M3", "M4", "M4 PRO", "M5", "M5S"],
        "High Level": ["F1", "F2", "F2 PRO", "F3", "F4", "F4 GT", "X3", "X3 PRO", "X4", "X5", "X6", "X6 PRO"]
    },
    "INFINIX": {
        "Entry Level": ["SMART", "SMART 4", "SMART 5", "SMART 6", "SMART 7", "SMART 8", "SMART 9"],
        "Mid Level": ["HOT 9", "HOT 10", "HOT 11", "HOT 12", "HOT 20", "HOT 30", "HOT 40", "NOTE 10", "NOTE 11", "NOTE 12"],
        "High Level": ["NOTE 30", "NOTE 40", "NOTE 50", "ZERO 30", "GT 10 PRO"]
    },
    "TECNO": {
        "Entry Level": ["SPARK 6", "SPARK 7", "SPARK 8", "SPARK 9"],
        "Mid Level": ["POVA", "POVA 4", "POVA 5"],
        "High Level": ["PHANTOM X", "PHANTOM X2", "19 PRO"]
    },
    "ITEL": {
        "Entry Level": ["A50", "A60", "A70"],
        "Mid Level": ["P40", "RS4"],
        "High Level": ["V55", "S23"]
    },
    "XIAOMI": {
        "Entry Level": ["A1", "A2", "A3"],
        "Mid Level": ["MI 8", "MI 9", "MI 10T", "MI 11T", "MI 12"],
        "High Level": ["MI 11 PRO", "MI 12T PRO", "MI 12T", "MI 13"]
    },
    "IPHONE": {
        "Entry Level": ["6", "6S", "7", "8", "SE"],
        "Mid Level": ["X", "XR", "XS", "11", "12"],
        "High Level": ["13", "14", "15", "PRO", "PROMAX"]
    },
    "ASUS": {
        "Entry Level": ["MAXPLUS M1", "MAXPRO M1"],
        "Mid Level": ["MAXPRO M2", "ZF MAXPRO M1", "ZF MAXP M2"],
        "High Level": ["ZF 3", "ZF LIVE 12"]
    },
    "HUAWEI": {
        "Entry Level": ["Y7"],
        "Mid Level": ["HONOR"],
        "High Level": ["NOVA 5T"]
    },
    "NOKIA": {
        "Entry Level": ["105", "C20", "T4"],
        "Mid Level": ["5"],
        "High Level": ["EXPERIA"]
    },
    "LAPTOP": {
        "Entry Level": ["AXIOO", "MY BOOK"],
        "Mid Level": ["LENOVO", "HP"],
        "High Level": ["ASUS", "ACER"]
    },
    "TAB": {
        "Entry Level": ["ADVAN", "ITEL"],
        "Mid Level": ["REALME"],
        "High Level": ["SAMSUNG"]
    }
}

def get_entry_category(merek, tipe):
    merek = str(merek).upper()
    tipe = str(tipe).upper()
    if merek in entry_map:
        for level, tipe_list in entry_map[merek].items():
            for t in tipe_list:
                if t in tipe:
                    return level
    return "Unknown"

df_after_invalid["ENTRY_LEVEL"] = df_after_invalid.apply(
    lambda x: get_entry_category(x["MEREK"], x["TIPE UNIT"]), axis=1
)

df_after_entry = df_after_invalid.copy()

# ------------------------------
# 5️⃣ TAMBAHKAN KATEGORI PENDAPATAN
# ------------------------------
print("💰 Menambahkan kategori pendapatan...")
bins = [0, 200000, 500000, float('inf')]
labels = ['Rendah', 'Sedang', 'Tinggi']
df['KATEGORI_PENDAPATAN'] = pd.cut(df['BIAYA'], bins=bins, labels=labels)
df_after_income = df.copy()

# ------------------------------
# 6️⃣ TAMBAHKAN ESTIMASI & KATEGORI WAKTU
# ------------------------------
print("⏱️ Menambahkan estimasi waktu dan kategori waktu...")
waktu_mapping = {
    "ganti lcd": "30 Menit - 1 Jam",
    "pasang lcd": "15 - 30 Menit",
    "ganti baterai": "30 - 1 Jam",
    "buka pola / pin / password": "2 - 4 jam",
    "software": "1 - 2 Jam",
    "ganti tombol": "10 Menit",
    "flexible on/off": "1 - 2 Jam",
    "ganti papan charge": "30 - 1 Jam",
    "mati total": "3 Jam",
    "error/hang": "3 Hari",
    "flexible mic/board": "1 - 2 Jam",
    "ganti connector charge": "30 Menit - 1 Jam",
    "ic charge": "1 - 2 Jam",
    "jalur charge": "1 - 2 Jam",
    "speaker": "1 - 2 Jam",
    "no charging": "1 - 2 Jam",
    "pasang papan charge": "30 Menit - 1 Jam",
    "ic gambar": "2 - 5 Hari",
    "masuk air": "1 - 2 Jam",
    "ganti back cover": "15 - 30 Menit",
    "ganti flexible fingerprint": "30 Menit - 1 Jam",
    "socket mesin": "30 menit - 1 Jam",
    "mic/audio": "1 - 2 Jam",
}
df["ESTIMASI_WAKTU"] = df["KERUSAKAN"].map(waktu_mapping).fillna("Tidak Diketahui")

def kategori_waktu(val):
    v = str(val).lower()
    if "menit" in v or "<" in v:
        return "Cepat (< 1 Jam)"
    elif "1 jam" in v or "2 jam" in v or "3 jam" in v or "4 jam" in v:
        return "Sedang (1 - 4 Jam)"
    elif "hari" in v:
        return "Lama (> 4 Jam)"
    else:
        return "Tidak Diketahui"

df["KATEGORI_WAKTU"] = df["ESTIMASI_WAKTU"].apply(kategori_waktu)
df_after_time = df.copy()

# ------------------------------
# 7️⃣ SIMPAN SEMUA TAHAP KE FILE EXCEL
# ------------------------------
print("💾 Menyimpan seluruh tahapan ke file Excel...")

with pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl') as writer:
    df_raw.to_excel(writer, index=False, sheet_name="1_Data_Awal")
    df_after_drop.to_excel(writer, index=False, sheet_name="2_Hapus_Kolom")
    df_after_invalid.to_excel(writer, index=False, sheet_name=f"3_Hapus_Data_Invalid({invalid_counts})")
    df_after_entry.to_excel(writer, index=False, sheet_name="4_Kategori_Entry_Level")
    df_after_income.to_excel(writer, index=False, sheet_name="5_Kategori_Pendapatan")
    df_after_time.to_excel(writer, index=False, sheet_name="6_Kategori_Waktu")

# ------------------------------
# 8️⃣ SIMPAN RINGKASAN
# ------------------------------
summary = pd.DataFrame({
    "Tahap": [
        "Data Awal",
        "Setelah Hapus Kolom",
        "Setelah Hapus Data Invalid",
        "Setelah Tambah Entry Level",
        "Setelah Kategori Pendapatan",
        "Setelah Kategori Waktu"
    ],
    "Total Data": [
        len(df_raw),
        len(df_after_drop),
        len(df_after_invalid),
        len(df_after_entry),
        len(df_after_income),
        len(df_after_time)
    ],
    "Data Dihapus": [
        0,
        len(df_raw) - len(df_after_drop),
        invalid_counts,
        0,
        0,
        0
    ]
})

with pd.ExcelWriter(OUTPUT_EXCEL, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
    summary.to_excel(writer, index=False, sheet_name="8_Ringkasan")

print(f"\n✅ Preprocessing selesai termasuk kategori Entry Level.")
print(f"📁 File disimpan di: {OUTPUT_EXCEL}")
