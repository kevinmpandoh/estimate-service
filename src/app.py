from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import re
from sklearn.model_selection import train_test_split
from werkzeug.utils import secure_filename
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from datetime import datetime
import numpy as np
from sklearn.tree import DecisionTreeClassifier, plot_tree
import matplotlib.pyplot as plt

app = Flask(__name__)
CORS(app)
MODEL_PATH = "model/model.pkl"
ENCODER_PATH = "model/encoders.pkl"
DATA_PATH = "data/dataset.xlsx"

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


    try: 
        data = request.get_json()
        input_data = {
            'MEREK': data['brand'].strip().lower(),
            'TIPE UNIT': data['type'].strip().lower(),
            'KERUSAKAN': data['damage'].strip().lower()
        }
        waktu_mapping = {
            "ganti lcd": "30 Menit - 1 Jam",
            "software": "1 - 2 Jam",
            "mati total": "2 - 4 Jam",
            "masuk air": "1 - 2 Jam",
            "connector charge": "30 Menit - 1 Jam",
            "error": "3 Hari",
            "buka pola": "2 - 4 jam",
            "ic gambar": "2 - 5 Hari",
            "fuse baterai": "1 - 2 Jam",
            "no chargeing": "1 - 2 Jam",
            "flexible on/off": "1 - 2 Jam",
            "ganti baterai": "30 Menit - 1 Jam",
            "install ulang": "30 Menit - 1 Jam",
            "ganti ic power": "2 - 5 Jam",
            "ganti kamera": "1 - 2 Jam",
            "ganti tombol": "1 - 2 Jam",
            "ganti speaker": "30 Menit - 1 Jam"
        }
        estimasi_waktu = waktu_mapping.get(input_data['KERUSAKAN'], "Tidak Diketahui")

        # Encode input
        encoded = []
        for key in ['MEREK', 'TIPE UNIT', 'KERUSAKAN']:
            le = encoders[key]
            if input_data[key] in le.classes_:
                encoded.append(le.transform([input_data[key]])[0])
            else:
                return jsonify({"success": False, "message": f"{key} '{input_data[key]}' tidak dikenal."})
            
        waktu_le = encoders.get('ESTIMASI_WAKTU')
        if waktu_le:
            if estimasi_waktu in waktu_le.classes_:
                encoded.append(waktu_le.transform([estimasi_waktu])[0])
            else:
                # Jika waktu tidak dikenal, gunakan nilai rata-rata atau default
                encoded.append(int(np.median(range(len(waktu_le.classes_)))))
        else:
            encoded.append(0)

        # Tambahkan fitur waktu (pakai hari ini)
        today = datetime.today()
        encoded.append(today.year)
        encoded.append(today.month)
        print(today)

        # Prediksi
        prediction = model.predict([encoded])
        kategori_le = encoders['KATEGORI_PENDAPATAN']
        kategori_biaya = kategori_le.inverse_transform(prediction.astype(int))[0]

        if prediction is None:
            return jsonify({
                "success": False,
                "message": "Estimasi tidak ditemukan."
            }), 404       
        
        return jsonify({
            "success": True,
            "brand": input_data['MEREK'],
            "type": input_data['TIPE UNIT'],
            "damage": input_data['KERUSAKAN'],
            "estimated_cost_category": kategori_biaya,
            "estimated_time": estimasi_waktu
        })

        # prediction_value = int(round(float(prediction)))

        # return jsonify({
        #     "success": True,
        #     "estimated_cost": prediction_value,
        #     "brand": input_data['MEREK'],
        #     "type": input_data['TIPE UNIT'],
        #     "damage": input_data['KERUSAKAN']
        # })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/train", methods=["POST"])
def train_model():
    global model, encoders

    try:
        # Load data dari Excel
        df = pd.read_excel(DATA_PATH, sheet_name="Sheet1")
        df.dropna(inplace=True)

         # Hapus kolom tidak digunakan
        if 'TANGGAL' in df.columns:
            df["TANGGAL"] = pd.to_datetime(df["TANGGAL"], errors="coerce", dayfirst=True)
            df["TAHUN"] = df["TANGGAL"].dt.year
            df["BULAN"] = df["TANGGAL"].dt.month
            df = df.drop(columns=["TANGGAL"])


        # Bersihkan data yang tidak valid
        invalid_keywords = ['?', ',', '+']
        escaped_keywords = [re.escape(k) for k in invalid_keywords]
        
        for col in ['MEREK', 'TIPE UNIT', 'KERUSAKAN']:
            df[col] = df[col].astype(str).str.strip().str.lower()
            df = df[~df[col].str.contains('|'.join(escaped_keywords), na=False)]

         # --- TRANSFORMATION: Perbaikan typo dan penyatuan nama ---
        # Normalisasi kerusakan
        damage_map = {
            "jalur lcd": "ganti lcd",
            "error/hank": "error / hang",
            "error/hank/restart": "error / hang",
            "tombol/error": "ganti tombol",
            "tombol": "ganti tombol",
            "gantitombol": "ganti tombol",
            "tombol luar": "ganti tombol",
            "ganti tombol luar": "ganti tombol",
            "tombol power": "ganti tombol",
            "lem lcd tombol": "ganti tombol",
            "repair tombol": "ganti tombol",
            "pasang tombol": "ganti tombol",
            "tombol volume": "ganti tombol",
            "error sim card": "error / hang",
            "papan charge": "pasang papan charge",
            "c. papan charge": "pasang papan charge",
            "repair papan charge": "ganti papan charge",
            "pasang kamera depan": "pasang kamera",
            "repair back camera": "pasang kamera",
            "repair camera": "pasang kamera",
            "camera": "pasang kamera",
            "ganti camera": "ganti kamera",
            "lem back cover": "pasang back cover",
            "back cover": "ganti back cover",
            "ganti cover": "ganti back cover",
            "connector": "ganti connector charge",
            "connector charge": "ganti connector charge",
            "conector charge": "ganti connector charge",
            "ganti flexiblle finger": "ganti flexible fingerprint",
            "flexible finger": "ganti flexible fingerprint",
            "finger": "ganti flexible fingerprint",
            "ganti finger": "ganti flexible fingerprint",
            "ganti flexible finger": "ganti flexible fingerprint",
            "jalur gambar": "ic gambar",
            "ganti baterai ori cabutan": "ganti baterai",
            "ganti casing": "ganti casing",
            "ganti casing set": "ganti casing",
            "pasang casing": "ganti casing",
            "pasang casing fullset": "ganti casing",
            "pasang casing set": "ganti casing",
            "ganti flexible on/off/volume": "flexible on/off",
            "ganti flexible board (soket)": "flexible mic / board",
            "ganti flexible": "flexible mic / board"
        }

        df["KERUSAKAN"] = df["KERUSAKAN"].replace(damage_map)

          # Tambahkan kolom estimasi waktu berdasarkan wawancara teknisi
        waktu_mapping = {
            "ganti lcd": "1 - 3 Jam",
            "ganti baterai": "30 Menit - 1 Jam",
            "install ulang": "30 Menit - 1 Jam",
            "ganti ic power": "2 - 5 Jam",
            "ganti kamera": "1 - 2 Jam",
            "ganti tombol": "1 - 2 Jam",
            "ganti speaker": "30 Menit - 1 Jam"
        }

        df["ESTIMASI_WAKTU"] = df["KERUSAKAN"].map(waktu_mapping).fillna("Tidak Diketahui")

        # Pastikan kolom tanggal jadi datetime
        # df["TANGGAL"] = pd.to_datetime(df["TANGGAL"], errors="coerce", dayfirst=True)
        # df = df.dropna(subset=["TANGGAL"])

        # Ekstrak fitur tanggal
        # df["TAHUN"] = df["TANGGAL"].dt.year
        # df["BULAN"] = df["TANGGAL"].dt.month

        bins = [0, 200000, 500000, float('inf')]
        labels = ['Rendah', 'Sedang', 'Tinggi']
        df['KATEGORI_PENDAPATAN'] = pd.cut(df['PENDAPATAN'], bins=bins, labels=labels)

        # Encode kolom kategori
        encoders = {}
        for col in ['MEREK', 'TIPE UNIT', 'KERUSAKAN', 'ESTIMASI_WAKTU', 'KATEGORI_PENDAPATAN']:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            encoders[col] = le

        # Fitur (X) dan Target (y)
        X = df[['MEREK', 'TIPE UNIT', 'KERUSAKAN', 'ESTIMASI_WAKTU', 'TAHUN', 'BULAN']]
        y = df['KATEGORI_PENDAPATAN']

        # Split train/test (80/20)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = DecisionTreeClassifier(criterion='entropy', random_state=42)
        model.fit(X_train, y_train)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        acc = np.mean(y_pred == y_test)   
        cm = confusion_matrix(y_test, y_pred)
        report = classification_report(
            y_test, y_pred, target_names=encoders['KATEGORI_PENDAPATAN'].classes_, output_dict=True
        )     

        # Simpan model dan encoder
        os.makedirs("model", exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        joblib.dump(encoders, ENCODER_PATH)


        # --- Visualisasi Pohon Keputusan ---
        plt.figure(figsize=(30, 20))
        feature_names = ['MEREK', 'TIPE UNIT', 'KERUSAKAN', 'ESTIMASI_WAKTU', 'TAHUN', 'BULAN']
        class_names = encoders['KATEGORI_PENDAPATAN'].classes_

        plot_tree(
            model,
            feature_names=feature_names,
            class_names=class_names,
            filled=True,
            rounded=True,
            fontsize=10
        )

        tree_path = "model/tree_visualization.png"
        plt.savefig(tree_path, bbox_inches="tight")
        plt.close()

                # --- Format confusion matrix untuk JSON ---
        cm_labels = encoders['KATEGORI_PENDAPATAN'].classes_.tolist()
        cm_list = cm.tolist()

        return jsonify({
            "success": True,
            "message": "Model berhasil dilatih dengan preprocessing dan estimasi waktu.",
            "accuracy": float(acc),
            "total_data": len(df),
            "confusion_matrix": {
                "labels": cm_labels,
                "matrix": cm_list
            },
            "classification_report": report,
        
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
