import zipfile
import os
import shutil
import uuid
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from pathlib import Path
import json

TEMP_DIR = Path("instance/tmp_classify")
STATIC_DIR = Path("app/static/classified_temp")
IMG_SIZE = (224, 224)


def get_preprocess_function(model_name):
    if model_name == "resnet50":
        from tensorflow.keras.applications.resnet50 import preprocess_input
    elif model_name == "efficientnet":
        from tensorflow.keras.applications.efficientnet import preprocess_input
    else:
        raise ValueError(f"Nieznana nazwa modelu: {model_name}")
    return preprocess_input


def preprocess_image(img_path, preprocess_fn):
    img = image.load_img(img_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)
    img_array = preprocess_fn(img_array)
    return np.expand_dims(img_array, axis=0)


def classify_zip(zip_path, model_path):
    session_id = str(uuid.uuid4())
    session_dir = TEMP_DIR / session_id
    static_session_dir = STATIC_DIR / session_id

    session_dir.mkdir(parents=True, exist_ok=True)
    static_session_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(session_dir)

    model = load_model(model_path)

    # Wczytaj class_indices z history.json
    history_path = Path(model_path).parent / "history.json"
    if history_path.exists():
        with open(history_path, "r", encoding="utf-8") as f:
            history_data = json.load(f)
        idx_to_label = {v: k for k, v in history_data.get("class_indices", {}).items()}
        model_name = history_data.get("config", {}).get("model_name", "resnet50")
    else:
        idx_to_label = {}
        model_name = "resnet50"

    preprocess_fn = get_preprocess_function(model_name)

    results = []
    image_paths = list(session_dir.rglob("*.[jp][pn]g"))

    for img_path in image_paths:
        try:
            img_preprocessed = preprocess_image(img_path, preprocess_fn)
            preds = model.predict(img_preprocessed)[0]
            predicted_idx = int(np.argmax(preds))
            confidence = float(preds[predicted_idx])
            predicted_label = idx_to_label.get(predicted_idx, f"Klasa {predicted_idx}")

            target_path = static_session_dir / img_path.name
            shutil.copy(img_path, target_path)

            results.append({
                "filename": img_path.name,
                "predicted_class": predicted_idx,
                "predicted_label": predicted_label,
                "confidence": confidence,
                "static_path": f"classified_temp/{session_id}/{img_path.name}"
            })

            # Debug: wypisz predykcje
            print(f"{img_path.name} → {preds.tolist()} → {predicted_idx} → {predicted_label}")

        except Exception as e:
            print(f"Błąd przy przetwarzaniu {img_path.name}: {e}")

    results_json_path = static_session_dir / "results.json"
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # ✅ Wyczyść tymczasowy folder po zakończeniu przetwarzania
    try:
        shutil.rmtree(session_dir)
        print(f"Usunięto tymczasowy folder: {session_dir}")
    except Exception as e:
        print(f"Błąd podczas usuwania {session_dir}: {e}")    

    return results, session_id
