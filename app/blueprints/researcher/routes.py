from flask import Blueprint, render_template, request, url_for
from flask_login import login_required, current_user
from app.decorators import role_required
from app.utils.classifier import get_available_models
from app.models import UserRole
import json
import os

from . import researcher

@researcher.route('/models', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.RESEARCHER)
def model_comparison():
    models = get_available_models()
    selected_model = None
    model_info = None

    if request.method == "POST":
        selected_model = request.form.get("model")
        if selected_model and os.path.exists(selected_model):
            try:
                history_path = os.path.join(os.path.dirname(selected_model), "history.json")
                with open(history_path, "r", encoding="utf-8") as f:
                    history = json.load(f)

                config = history.get("config", {})
                val_acc = history.get("history", {}).get("val_accuracy", [])
                epoch_times = history.get("epoch_times_sec", [])
                training_time_sec = sum(epoch_times) if epoch_times else 0
                avg_epoch_time_sec = round(training_time_sec / len(epoch_times), 2) if epoch_times else 0

                model_dirname = os.path.basename(os.path.dirname(selected_model))
                plot_base = f"img/{model_dirname}"
                accuracy_plot = url_for("static", filename=f"{plot_base}/accuracy.svg")
                loss_plot = url_for("static", filename=f"{plot_base}/loss.svg")

                model_info = {
                    "name": model_dirname,
                    "config": {
                        "model_name": config.get("model_name"),
                        "mode": config.get("mode"),
                        "use_aug": config.get("use_aug"),
                        "epochs": config.get("epochs"),
                        "batch_size": config.get("batch_size"),
                        "early_stopping": history.get("early_stopping", False),
                        "actual_epochs": history.get("actual_epochs", None),
                        "class_count": len(history.get("class_indices", {}))
                    },
                    "val_accuracy": val_acc[-1] if val_acc else None,
                    "training_time_min": round(training_time_sec / 60, 2),
                    "avg_epoch_time_sec": avg_epoch_time_sec,
                    "plots": {
                        "accuracy": accuracy_plot,
                        "loss": loss_plot
                    }
                }

            except Exception as e:
                print(f"Błąd przy ładowaniu history.json: {e}")
                model_info = None

    return render_template(
        "researcher/models.html",
        models=models,
        selected_model=selected_model,
        model_info=model_info
    )
