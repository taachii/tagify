document.addEventListener("DOMContentLoaded", function () {
  const bg1 = document.getElementById("bg1");
  const bg2 = document.getElementById("bg2");

  if (!bg1 || !bg2) return;

  const images = [
    "/static/img/hero1.jpg",
    "/static/img/hero2.jpg",
    "/static/img/hero3.jpg",
    "/static/img/hero4.jpg",
    "/static/img/hero5.jpg"
  ];

  const interval = 12000;
  let showingBg1 = true;

  // Losowy startowy indeks
  const startIndex = Math.floor(Math.random() * images.length);
  const firstImage = images[startIndex];

  // Usuń pierwszy obraz z kolejki, żeby się nie powtórzył od razu
  const remainingImages = [...images];
  remainingImages.splice(startIndex, 1); // usuń 1 element pod tym indeksem

  let index = 0;

  function crossfade() {
    const current = showingBg1 ? bg1 : bg2;
    const next = showingBg1 ? bg2 : bg1;

    next.style.backgroundImage = `url('${remainingImages[index]}')`;
    next.style.opacity = 1;
    current.style.opacity = 0;

    showingBg1 = !showingBg1;
    index = (index + 1) % remainingImages.length;
  }

  // Ustaw pierwszy obraz jako losowy
  bg1.style.backgroundImage = `url('${firstImage}')`;
  bg1.style.opacity = 1;

  setInterval(crossfade, interval);
});
