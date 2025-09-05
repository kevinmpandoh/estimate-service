from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import re
from sklearn.model_selection import train_test_split
from werkzeug.utils import secure_filename
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime
import numpy as np

app = Flask(__name__)
CORS(app)
MODEL_PATH = "model/model.pkl"
ENCODER_PATH = "model/encoders.pkl"
DATA_PATH = "data/gabungan_data_hasil_clean.xlsx"

# Load model & encoder jika ada
model = None
encoders = None
if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
    model = joblib.load(MODEL_PATH)
    encoders = joblib.load(ENCODER_PATH)

@app.route("/estimate", methods=["POST"])
def predict():
    global model, encoders

    if model is None or encoders is None:
        return jsonify({"success": False, "message": "Model belum tersedia. Silakan latih terlebih dahulu."})

    data = request.get_json()

    try: 
        input_data = {
            'MEREK': data['brand'].strip().lower(),
            'TIPE UNIT': data['type'].strip().lower(),
            'KERUSAKAN': data['damage'].strip().lower()
        }

        # Encode input
        encoded = []
        for key in ['MEREK', 'TIPE UNIT', 'KERUSAKAN']:
            le = encoders[key]
            if input_data[key] in le.classes_:
                encoded.append(le.transform([input_data[key]])[0])
            else:
                return jsonify({"success": False, "message": f"{key} '{input_data[key]}' tidak dikenal."})

        # Tambahkan fitur waktu (pakai hari ini)
        today = datetime.today()
        encoded.append(today.year)
        encoded.append(today.month)
        print(today)

        # Prediksi
        prediction = model.predict([encoded])[0]

        return jsonify({
            "success": True,
            "estimated_cost": int(prediction)
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/train", methods=["POST"])
def train_model():
    global model, encoders

    try:
        # Load data dari Excel
        df = pd.read_excel(DATA_PATH, sheet_name="Sheet1")
        df.dropna(inplace=True)

        # Bersihkan data yang tidak valid
        invalid_keywords = ['?', ',', '+']
        escaped_keywords = [re.escape(k) for k in invalid_keywords]

        for col in ['MEREK', 'TIPE UNIT', 'KERUSAKAN']:
            df = df[~df[col].astype(str).str.contains('|'.join(escaped_keywords), na=False)]

        # Normalisasi teks (strip + lowercase)
        for col in ['MEREK', 'TIPE UNIT', 'KERUSAKAN']:
            df[col] = df[col].astype(str).str.strip().str.lower()

        # Pastikan kolom tanggal jadi datetime
        df["TANGGAL"] = pd.to_datetime(df["TANGGAL"], errors="coerce", dayfirst=True)
        df = df.dropna(subset=["TANGGAL"])

        # Ekstrak fitur tanggal
        df["TAHUN"] = df["TANGGAL"].dt.year
        df["BULAN"] = df["TANGGAL"].dt.month

        # Encode kolom kategori
        encoders = {}
        for col in ['MEREK', 'TIPE UNIT', 'KERUSAKAN']:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            encoders[col] = le

        # Fitur (X) dan Target (y)
        X = df[['MEREK', 'TIPE UNIT', 'KERUSAKAN', 'TAHUN', 'BULAN']]
        y = df['PENDAPATAN']

        # Split train/test (80/20)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Latih model
        model = DecisionTreeRegressor(criterion='squared_error', max_depth=5, random_state=42)
        model.fit(X_train, y_train)

        # Evaluasi di train set
        y_train_pred = model.predict(X_train)
        train_mse = mean_squared_error(y_train, y_train_pred)
        train_rmse = np.sqrt(train_mse)
        train_r2 = r2_score(y_train, y_train_pred)

        # Evaluasi di test set
        y_test_pred = model.predict(X_test)
        test_mse = mean_squared_error(y_test, y_test_pred)
        test_rmse = np.sqrt(test_mse)
        test_r2 = r2_score(y_test, y_test_pred)

        # Simpan model dan encoder
        os.makedirs("model", exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        joblib.dump(encoders, ENCODER_PATH)

        return jsonify({
            "success": True,
            "message": "Model berhasil dilatih ulang.",
            "train_mse": train_mse,
            "train_rmse": train_rmse,
            "train_r2_score": train_r2,
            "test_mse": test_mse,
            "test_rmse": test_rmse,
            "test_r2_score": test_r2
        })
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    
@app.route("/upload", methods=["POST"])
def upload_data():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "Tidak ada file yang dikirim."})

        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "message": "Nama file kosong."})

        if not file.filename.endswith('.xlsx'):
            return jsonify({"success": False, "message": "File harus berformat .xlsx."})

        # Simpan file ke folder data
        os.makedirs("data", exist_ok=True)
        filename = secure_filename("gabungan_data_hasil.xlsx")
        file_path = os.path.join("data", filename)
        file.save(file_path)

        return jsonify({"success": True, "message": "File berhasil diupload dan disimpan."})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
