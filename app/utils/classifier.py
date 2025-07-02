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

def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0
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
    results = []
    image_paths = list(session_dir.rglob("*.[jp][pn]g"))

    for img_path in image_paths:
        try:
            img_preprocessed = preprocess_image(img_path)
            preds = model.predict(img_preprocessed)[0]
            predicted_idx = int(np.argmax(preds))
            confidence = float(preds[predicted_idx])
            predicted_label = f"Klasa {predicted_idx}"

            target_path = static_session_dir / img_path.name
            shutil.copy(img_path, target_path)

            results.append({
                "filename": img_path.name,
                "predicted_class": predicted_idx,
                "predicted_label": predicted_label,
                "confidence": confidence,
                "static_path": f"classified_temp/{session_id}/{img_path.name}"
            })

        except Exception as e:
            print(f"Błąd przy przetwarzaniu {img_path.name}: {e}")

    results_json_path = static_session_dir / "results.json"
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return results, session_id
