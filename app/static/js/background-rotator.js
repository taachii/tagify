document.addEventListener("DOMContentLoaded", function () {
  const bg1 = document.getElementById("bg1");
  const bg2 = document.getElementById("bg2");

  if (!bg1 || !bg2) return; // nie rób nic, jeśli elementów nie ma

  const images = [
    "/static/img/hero1.jpg",
    "/static/img/hero2.jpg",
    "/static/img/hero3.jpg",
    "/static/img/hero4.jpg",
    "/static/img/hero5.jpg"
  ];

  let index = 0;
  const interval = 12000;
  let showingBg1 = true;

  function crossfade() {
    const current = showingBg1 ? bg1 : bg2;
    const next = showingBg1 ? bg2 : bg1;

    next.style.backgroundImage = `url('${images[index]}')`;
    next.style.opacity = 1;
    current.style.opacity = 0;

    showingBg1 = !showingBg1;
    index = (index + 1) % images.length;
  }

  // Inicjalizacja
  bg1.style.backgroundImage = `url('${images[0]}')`;
  bg1.style.opacity = 1;
  index = 1;

  setInterval(crossfade, interval);
});
