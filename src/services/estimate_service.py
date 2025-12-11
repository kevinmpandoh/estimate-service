from flask import jsonify
import joblib
import numpy as np
from utils.preprocessing import preprocess_input
from utils.paths import MODEL_PATH, ENCODER_PATH

def estimate_service(data):

    # Ambil input user
    brand = data.get("brand")
    tipe = data.get("type")
    damage = data.get("damage")

    print("Estimating for:", brand, tipe, damage)

    if not brand or not tipe or not damage:
        return {
            "success": False,
            "message": "brand, type, dan damage wajib diisi"
        }

    # 🔥 Preprocessing sama dengan training
    brand_clean, tipe_clean, damage_clean, waktu_estimasi, kategori_wkt  = preprocess_input(brand, tipe, damage)

    print("Preprocessed to:", brand_clean, tipe_clean, damage_clean)
    try:
        # Load model & encoders
        model = joblib.load(MODEL_PATH)
        encoders = joblib.load(ENCODER_PATH)
    except Exception as e:
        return {
            "success": False,
            "message": f"Model belum dilatih: {e}"
        }

    try:
        # Encode input sesuai model
        brand_encoded = encoders["MEREK"].transform([brand_clean])[0]
        tipe_encoded = encoders["TIPE UNIT"].transform([tipe_clean])[0]
        damage_encoded = encoders["KERUSAKAN"].transform([damage_clean])[0]

      

    except Exception:
        return jsonify({
            "success": False,
            "message": "Data input belum dikenal oleh model (brand/tipe/damage tidak ada dalam training)"
        }), 400

    # Bentuk array input model
    input_array = np.array([[brand_encoded, tipe_encoded, damage_encoded]])

    # Prediksi
    pred_class = model.predict(input_array)[0]
    pred_label = encoders["KATEGORI_BIAYA"].inverse_transform([pred_class])[0]

    # Range biaya berdasarkan kategori
    biaya_range = {
        "Murah": "Rp. 0 - 250.000",
        "Sedang": "Rp. 250.001 - 500.000",
        "Mahal": "> Rp. 500.000"
    }

    return {
        "success": True,
        # "estimated_cost_category": pred_label,
        "estimated_cost_category": biaya_range.get(pred_label, "Unknown"),
        "brand": brand_clean,
        "type": tipe,
        "damage": damage_clean,
        # "estimated_time": waktu_estimasi,
        "estimated_time": kategori_wkt,
        

            # "success": True,
            # "brand": brand_clean,
            # "type": tipe_clean,
            # "damage": damage_clean,
            # "estimated_cost_category": pred_label,
            # "estimated_time": "Unknown"
    }
