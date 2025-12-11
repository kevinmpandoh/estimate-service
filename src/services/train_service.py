import os
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from utils.normalize import normalize_damage
from utils.mapping_type_unit import get_entry_category
from utils.paths import DATA_PATH, MODEL_PATH, ENCODER_PATH
import matplotlib.pyplot as plt
from utils.preprocessing import preprocess_training

def train_model_service():
    df = pd.read_excel(DATA_PATH)
    df.dropna(inplace=True)



    # Hapus kolom tidak digunakan
    if 'TANGGAL' in df.columns:
        df["TANGGAL"] = pd.to_datetime(df["TANGGAL"], errors="coerce", dayfirst=True)
        df = df.drop(columns=["TANGGAL"])


    # Normalisasi kerusakan (gunakan file utils)
    # df["KERUSAKAN"] = df["KERUSAKAN"].apply(normalize_damage)

    # Mapping tipe unit → Entry / Mid / High
    # df["TIPE UNIT"] = df.apply(
    #     lambda x: get_entry_category(x["MEREK"], x["TIPE UNIT"]), axis=1
    # )
    df = preprocess_training(df)

    # Tambahkan kategori biaya
    bins = [0, 250000, 500000, float("inf")]
    labels = ["Murah", "Sedang", "Mahal"]
    df["KATEGORI_BIAYA"] = pd.cut(df["BIAYA"], bins=bins, labels=labels)

    encoders = {}
    for col in ["MEREK", "TIPE UNIT", "KERUSAKAN", "KATEGORI_BIAYA"]:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    X = df[["MEREK", "TIPE UNIT", "KERUSAKAN"]]
    y = df["KATEGORI_BIAYA"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    model = DecisionTreeClassifier(criterion="entropy", random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = (y_pred == y_test).mean()
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(
        y_test, y_pred, target_names=encoders["KATEGORI_BIAYA"].classes_, output_dict=True
    )

    os.makedirs("model", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoders, ENCODER_PATH)

    # Visualisasi Tree
    plt.figure(figsize=(30, 20))
    plot_tree(
        model,
        feature_names=["MEREK", "TIPE UNIT", "KERUSAKAN"],
        class_names=encoders["KATEGORI_BIAYA"].classes_,
        filled=True,
    )
    plt.savefig("model/tree.png")
    plt.close()

    return {
        "accuracy": float(acc),
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
        "total_data": len(df),
    }