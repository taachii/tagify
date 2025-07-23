import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore
from sklearn.metrics import confusion_matrix # type: ignore
import numpy as np # type: ignore
import os

def save_confusion_matrix(label_pairs, output_path):
    """
    Generuje i zapisuje macierz pomyłek na podstawie par (true_label, predicted_label).

    :param label_pairs: lista krotek (true_label, predicted_label)
    :param output_path: ścieżka do pliku PNG z wykresem
    """
    if not label_pairs:
        print("Brak danych do wygenerowania confusion matrix.")
        return

    # Rozpakowanie par do dwóch list
    true_labels, pred_labels = zip(*label_pairs)

    # Lista wszystkich unikalnych etykiet
    labels = sorted(list(set(true_labels + pred_labels)))

    # Wyliczenie macierzy
    cm = confusion_matrix(true_labels, pred_labels, labels=labels)

    # Normalizacja względem wierszy (każda klasa osobno)
    with np.errstate(all='ignore'):
        cm_norm = cm.astype('float') / cm.sum(axis=1, keepdims=True)
        cm_norm = np.nan_to_num(cm_norm)

    # Tworzenie wykresu
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm_norm, annot=True, fmt=".2f", cmap="Blues",
                xticklabels=labels, yticklabels=labels,
                linewidths=0.5, linecolor='gray')
    plt.xlabel('Predykcja')
    plt.ylabel('Poprawna etykieta')
    plt.title('Macierz pomyłek (confusion matrix)')
    plt.tight_layout()

    # Zapis do pliku
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    print(f"Confusion matrix zapisana do: {output_path}")
