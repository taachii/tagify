document.addEventListener("DOMContentLoaded", function () {
  const images = [
    "/static/img/hero1.jpg",
    "/static/img/hero2.jpg",
    "/static/img/hero3.jpg",
    "/static/img/hero4.jpg",
    "/static/img/hero5.jpg"
  ];

  let index = 0;
  const changeInterval = 10000; // 15 sekund

  function changeBackground() {
    const body = document.querySelector("body.hero-bg");
    if (body) {
      body.style.backgroundImage = `url('${images[index]}')`;
      index = (index + 1) % images.length;
    }
  }

  // Start rotacji
  changeBackground();
  setInterval(changeBackground, changeInterval);
});
