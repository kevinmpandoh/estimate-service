import re
import pandas as pd
from utils.normalize import normalize_damage
from utils.mapping_type_unit import get_entry_category
from utils.waktu_mapping import waktu_mapping
from utils.waktu_kategori import kategori_waktu

INVALID_KEYWORDS = ['?', ',', '+']
ESCAPED_INVALID = [re.escape(k) for k in INVALID_KEYWORDS]

def clean_text(df):
    """Bersihkan merek, tipe unit, kerusakan"""
    for col in ['MEREK', 'TIPE UNIT', 'KERUSAKAN']:
        df[col] = df[col].astype(str).str.strip().str.lower()
        df = df[~df[col].str.contains('|'.join(ESCAPED_INVALID), na=False)]
    return df

def filter_kerusakan_minimum(df, min_count=9):
    """Hapus kategori kerusakan yang jumlahnya terlalu sedikit"""
    kerusakan_counts = df['KERUSAKAN'].value_counts()
    allowed = kerusakan_counts[kerusakan_counts >= min_count].index
    return df[df['KERUSAKAN'].isin(allowed)]

def preprocess_training(df):
    """Preprocessing full untuk training"""
    
    df = clean_text(df)

    df["KERUSAKAN"] = df["KERUSAKAN"].apply(normalize_damage)
    df["TIPE UNIT"] = df.apply(lambda x: get_entry_category(x["MEREK"], x["TIPE UNIT"]), axis=1)

    df = filter_kerusakan_minimum(df)

    return df


def preprocess_input(brand, tipe, damage):
    """Preprocessing untuk 1 data input user pada saat prediksi"""

    brand = brand.lower().strip()
    tipe = tipe.lower().strip()
    damage = damage.lower().strip()

    damage = normalize_damage(damage)
    tipe = get_entry_category(brand, tipe)
    
    waktu_estimasi = waktu_mapping.get(damage, "Tidak diketahui")
    kategori = kategori_waktu(waktu_estimasi)
    
    return brand, tipe, damage, kategori, waktu_estimasi
