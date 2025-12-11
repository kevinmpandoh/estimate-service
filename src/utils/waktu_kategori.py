def kategori_waktu(val: str):
    v = str(val).lower()

    if "menit" in v or "<" in v:
        return "Cepat"
    elif "jam" in v:
        return "Sedang"
    elif "hari" in v:
        return "Lama"
    else:
        return "Tidak Diketahui"
