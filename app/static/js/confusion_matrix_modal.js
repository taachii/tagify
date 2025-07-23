document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('confusionMatrixModal');
  const img = document.getElementById('confusionMatrixImg');

  // Zamknij modal po kliknięciu poza obrazem lub w krzyżyk
  modal.addEventListener('click', (event) => {
    if (event.target === modal || event.target.classList.contains('close')) {
      hideConfusionMatrix();
    }
  });
});

function showConfusionMatrix(imageUrl) {
  const modal = document.getElementById('confusionMatrixModal');
  const img = document.getElementById('confusionMatrixImg');

  if (modal && img) {
    img.src = imageUrl;
    modal.classList.remove('hidden');
  }
}

function hideConfusionMatrix() {
  const modal = document.getElementById('confusionMatrixModal');
  const img = document.getElementById('confusionMatrixImg');

  if (modal && img) {
    modal.classList.add('hidden');
    img.src = '';
  }
}
