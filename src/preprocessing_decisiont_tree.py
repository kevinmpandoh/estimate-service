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
    df[col] = df[col].astype(str).str.lower()
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
            "A01", "A01 CORE", "A02", "A02 CORE", "A02E", "A02S",
            "A03", "A03 2 PCS", "A03 CORE", "A03 OCRE", "A03S",
            "A04", "A04E", "A04S", "A05", "A05S", "A06", "A0S",
            "A10", "A10S", "A10S EDGE", "A11", "A12", "A13",
            "A14", "A15", "A16", "A2 CORE",
            "J1", "J1 2016", "J1 ACE",
            "J2 CORE", "J2 PRIME", "J2 PRO",
            "J3", "J3 PRO", "J4", "J4 2018", "J4 PLUS", "J400",
            "J5", "J5 2016", "J5 PRIME", "J5 PRO", "J500",
            "J6", "J6 PLUS", "J600",
            "J7", "J7 2016", "J7 PRIME", "J700",
            "J8", "J8 2018",
            "GRAND PRIME", "KECIL",
            "M02", "M10", "M10S", "M12", "M15"
        ],
        "Mid Level":[
            # Seri Galaxy A (kelas menengah)
            "A20", "A20S", "A21", "A21S",
            "A22", "A22 4G", "A22 5G",
            "A23", "A23 4G", "A23 5G",
            "A24",
            "A3 2017", "A3 CORE",
            "A30", "A30S", "A31",
            "A32", "A32 4G",
            "A33", "A33 5G",
            "A34", "A35", "A35 5G",
            "A50", "A50S", "A51",
            "A52", "A53", "A53 5G",
            "A54", "A55",
            "A6", "A6 2018", "A6 PLUS",
            "A60", "A7", "A7 2017", "A7 2018",
            "A70", "A71", "A72", "A73", "A75", "A750",
            "A8 2018", "A8 PLUS", "A8 STAR", "A80",

            # Seri Galaxy M (mid-range)
            "M20", "M30", "M30S", "M31", "M51",

            # Seri Galaxy S FE (Fan Edition)
            "S20 FE", "S24FE",

            # Seri Galaxy Note mid-tier
            "NOTE 8", "NOTE 10 LITE",

            # Seri Galaxy S lama (mid by current standard)
            "S8", "S8 PLUS", "TAB MEDIATEK", "TAB A9 LITE", "TAB 10", "TAB T95", "TAB A", "TAB T295", "TAB T285"
        ],
        "High Level": [
            # Seri Galaxy Note flagship
            "NOTE 10 PLUS", "NOTE 20 ULTRA",

            # Seri Galaxy S (kelas flagship)
            "S20", "S20 ULTRA", "S21",

            # Seri Galaxy Fold / Flip (premium foldable)
            "FLIP 4", "FLIP 5",

            # Seri Galaxy Tab premium
            "TAB S9"
        ],
    },
    "VIVO": {
        "Entry Level": [
            "03T", "5 TG", "C63",
            "Y01", "Y02", "Y02 T", "Y02T", "Y02I", "Y03",
            "Y1S", "Y12", "Y12S", "Y15", "Y15S", "Y16",
            "Y17", "Y17S", "Y18", "Y19", "Y20", "Y20S",
            "Y21", "Y21A", "Y21S", "Y22", "Y27", "Y27S",
            "Y28", "Y30", "Y30I", "Y33", "Y33S", "Y35",
            "Y35S", "Y36", "Y50", "Y51", "Y53", "Y53S",
            "Y55", "Y63", "Y66", "Y67", "Y69", "Y71",
            "Y80", "Y81", "Y83", "Y91", "Y91C", "Y93"
        ],
        "Mid Level": [
            # Seri S dan T (mid range performance)
            "S1", "S1 PRO", "T1",

            # Seri V (mid-range lifestyle series)
            "V5", "V5 5G", "V5 LITE", "V5 PLUS", "V5S",
            "V7 PLUS", "V9", "V11", "V11 PRO", "V12",
            "V15", "V15 PRO", "V17", "V17 PRO", "V17S",
            "V19", "V20", "V20 SE", "V20S", "V21",
            "V21 5G", "V21S", "V23", "V23E",
            "V27", "V27E",
            "Y100",  # model terbaru dengan spesifikasi mid-upper
            "Z1", "Z1 PRO"
        ],
        "High Level": ["X50", "X60", "X70", "X80", "X90", "X100", "X100 PRO"]
    },
    "OPPO": {
        "Entry Level": [
            "A12", "A13", "A14", "A15","A05","A03",
            "A16", "A16E", "A16K",
            "A17", "A17K", "A18",
            "A1K", "A31","A11K",
            "A33", "A33W", "A35", "A36",
            "A37", "A38",
            "A3S", "A3X",
            "A51", "A5S", "A60",
            "A71", "A83",
            "NEO 7",
            "M3", "Y17S"  # outlier entry models
        ],
        "Mid Level": [
            # Seri A mid-tier
            "A5 2020", "A52", "A53", "A54", "A54 (2 UNIT)", "A55",
            "A57", "A58", "A74", "A74 5G", "A76", "A766",
            "A77", "A77S", "A78", "A78 5G",
            "A7", "A9 2020", "A92", "A95", "A96", "A98",

            # Seri F mid-range (populer di era 2017–2020)
            "F1", "F1S", "F3", "F5", "F7", "F7 YOUTH", "F9",
            "F11", "F11 PRO",

            # Seri Reno awal sampai menengah
            "RENO 1", "RENO 2", "RENO 2F", "RENO 3",
            "RENO 4", "RENO 4F", "RENO 5", "RENO 5 4G", "RENO 5F",
            "RENO 6", "RENO 7", "RENO 7 4G", "RENO 7Z 5G",
            "RENO 8", "RENO 8 4G", "RENO 8 5G", "RENO 8 PLUS",
            "RENO 8T", "RENO 8Z 5G", "RENO 8I", "RENO 11 E",

            # Seri R mid-range
            "R17 PRO"
        ],
        "High Level": [
            "RENO 10X ZOOM",  # flagship Reno zoom series
            "X3"              # flagship Find X3 / X3 Pro
        ],
    },
    "REDMI": {
        "Entry Level": [
            # Seri angka 1 digit dan A-series
            "2 PRO", "5", "5 PLUS", "5A", "6A", "7", "8", "8 5G", "8A", "8A PRO",
            "9A", "9C", "9E", "9I", "A1", "A2", "A3",

            # Seri C-series
            "C25", "10A", "10C", "12C", "13C",

            # Seri lawas
            "S2"
        ],
        "Mid Level": [
            # Seri 9–10–12 mid-range
            "9", "9 PRO", "9T",
            "10", "10 5G", "10S",

            # Seri 12 & 13 mid-range
            "12", "12T",
            "NOTE 10", "NOTE 10 5G", "NOTE 10 PRO", "NOTE 10S",
            "NOTE 11", "NOTE 11 4G", "NOTE 11 PRO",
            "NOTE 12", "NOTE 12 5G", "NOTE 12 PRO",
            "NOTE 12 PRO 4G", "NOTE 12 PRO 5G",
            "NOTE 13", "NOTE 13 4G", "NOTE 13 PRO", "NOTE 13 PRO 5G",

            # Seri lama tapi masih mid-range
            "NOTE 3", "NOTE 4", "NOTE 4X", "NOTE 5", "NOTE 5A",
            "NOTE 6", "NOTE 6 PRO", "NOTE 7", "NOTE 8", "NOTE 8 PRO",
            "NOTE 9", "NOTE 9 PLUS", "NOTE 9 PRO", "NOTE 9A",

            # Tambahan seri A / C atas
            "10", "12T"
        ],
        "High Level": [
            "NOTE 13 PRO", "NOTE 13 PRO 5G", "NOTE 12 PRO 5G", "NOTE 12 PRO",
            "NOTE 12T", "NOTE 12T PRO", "NOTE 13 PRO PLUS"
        ]
    },
    "REALME": {
        "Entry Level": [
            # Seri C (budget series)
            "C1", "C2", "C2O", "C3",
            "C11", "C11 2021", "C12", "C13", "C15", "C17",
            "C20", "C21", "C21Y", "C211Y", "C25", "C25S", "C25Y",
            "C30", "C30S", "C31", "C33", "C35", "C50",
            "C51", "C53", "C55", "C61", "C63",

            # Seri Narzo Entry
            "NARZO", "NARZO 20", "NARZO 50A", "NARZO A30", "NARZO A50",

            # Seri lama (harga di bawah 2 juta)
            "2", "3", "3 PRO", "5", "5I", "9A", "9I", "NOTE 50", "NOTE 60"
        ],
        "Mid Level": [
            "5 PRO", "6", "6 PRO", "7", "7 PRO", "7I",
            "8", "8 (2 PCS)", "8 PRO", "8I", "8i",
            "9", "9 PRO", "9 PRO PLUS",
            "10", "11", "11 4G",
            "NOTE 10", "NOTE 11",

            # Seri Narzo menengah
            "NARZO 20 PRO", "NARZO 50",

            # Seri 2 PRO hingga 9I
            "2 PRO", "5 PRO", "9I"
        ],
        "High Level":[
            "GT MASTER",
            "XT"
        ]
    },
    "POCO": {
        "Entry Level": [
            "C65",
            "M3", "M3 PRO",
            "M4", "M4 PRO",
            "M5", "M5S"
        ],
        "Mid Level": [
            "X2 PRO",
            "X3", "X3 NFC", "X3 GT", "X3 PRO",
            "X6 PRO"
        ],
        "High Level": [
            "F1", "F1S", "F2", "F2 PRO",
            "F3", "F4", "F4 5G"
        ]
    },
    "INFINIX": {
        "Entry Level": [
            # Seri SMART
            "SMART 4", "SMART 5", "SMART 6", "SMART 6 HD",
            "SMART 6 PLIS", "SMART 6 PLUS", "SMART 6 PUS",
            "SMART 7", "SMART 8", "SMART 8 PRO", "SMART 9", "SAMRT 8",

            # Seri HOT lawas
            "HOT 9", "HOT 9 PLAY", "HOT 9 PLY",
            "HOT 10", "HOT 10 PLAY", "HOT 10 PLAY (P.T)", "HOT 10S",
            "HOT 11", "HOT 11 PLAY", "HOT 11S",
            "HOT 12", "HOT 12 PLAY", "HOT 12 PRO", "HOT 12I",

            # Seri Itel (entry brand)
            "ITEL A50", "ITELL A30", "ITELL A70", "ITELL S23"
        ],
        "Mid Level": [
            # Seri HOT generasi baru (mid-tier)
            "HOT 20I", "HOT 20S",
            "HOT 30", "HOT 30I", "HOT 30 PRO",
            "HOT 40", "HOT 40I", "HOT 40 PRO",
            "HOT 50", "HOT 50I", "HOT 50 PRO",

            # Seri NOTE (mid-range utama)
            "NOTE 7", "NOTE 8", "NOTE 10", "NOTE 11", "NOTE 12",
            "NOTE 12I", "NOTE 30", "NOTE 30I", "NOTE 30 PRO",
            "NOTE 40", "NOTE 40S", "NOTE 50", "NOTE  30", "TAB"
        ],
        "High Level": [
            "ZERO 30",
            "GT 10 PRO",
            "40 PRO"
        ]
    },
    "TECNO": {
        "Entry Level": ["SPARK 6", "SPARK 7", "SPARK 8", "SPARK 9", "SPARK"],
        "Mid Level": ["POVA", "POVA 4", "POVA 5"],
        "High Level": ["PHANTOM X", "PHANTOM X2", "19 PRO"]
    },
    "ITEL": {
        "Entry Level": [
            "50",
            "A50", "A60", "A70",
            "P40",
            "S23"
        ],
        "Mid Level": ["V55", "RS4"],
        "High Level": [
            "VISTA TAB 10"
        ]
    },
    "XIAOMI": {
        "Entry Level": [
            "A2 LITE", "A3",
            "MI A1", "MI A2", "MIA1",
            "MI PLAY",  "MI 2",
            "MI S2", "S2",
            "REDMI A1",  # kadang muncul di kategori Xiaomi di toko
            "BN 48"      # kemungkinan Redmi entry-level battery code
        ],
        "Mid Level": [
            "MI 10T", "MI 11T", "MI 11 LITE","MI 12 LITE", "MI 12T",
            "MI 8", "MI 8 LITE", "MI MAX", "MI MAX 3",
            "NOTE 4", "NOTE 5A"
        ],
        "High Level": [
            "MI 10T PRO", "MI 11T PRO", "MI 11 T PRO", "MI 12", "12T", "MI 6X"
        ]
    },
    "IPHONE": {
        "Entry Level": [
            "6G", "6S", "6S PLUS",
            "7", "7 PLUS",
            "8", "8 PLUS"
        ],
        "Mid Level": [
            "X", "XR", "XS",
            "11", "12", "13"
        ],
        "High Level": [
            "XS MAX",
            "11 PRO", "11 PROMAX",
            "12 PRO", "12 PROMAX",
            "13 PROMAX",
            "14", "14 PLUS", "14 PRO",
            "15 PRO", "15 PROMAX",
            "16"
        ],
    },
    "ASUS": {
        "Entry Level": [
    "ZF 3",
    "ZF LIVE 12"
],
        "Mid Level": [
    "MAXPLUS M1",
    "MAXPRO M1",
    "MAXPRO M2",
    "ZF MAXP M2",
    "ZF MAXPRO M1"
],
        "High Level": [
    "ZENFONE 8", "ZENFONE 9", "ZENFONE 10", "ROG PHONE"
]
    },
    "HUAWEI": {
        "Entry Level": ["Y7"],
        "Mid Level": ["HONOR"],
        "High Level": ["NOVA 5T"]
    },
    "NOKIA": {
        "Entry Level": [
            "105",        # Feature phone klasik
            "C20",        # Android Go
            "KECIL",      # Umumnya digunakan untuk HP kecil / feature phone
            "T4 1107"     # Model jadul / keypad
        ],
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
    "no chargeing": "1 - 2 Jam",
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
