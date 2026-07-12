(function () {
  "use strict";

  const menuButton = document.querySelector(".menu-toggle");
  const navigation = document.querySelector(".site-nav");

  function closeMenu() {
    if (!menuButton || !navigation) return;
    menuButton.setAttribute("aria-expanded", "false");
    navigation.classList.remove("is-open");
    document.body.classList.remove("menu-open");
  }

  if (menuButton && navigation) {
    menuButton.addEventListener("click", function () {
      const willOpen = menuButton.getAttribute("aria-expanded") !== "true";
      menuButton.setAttribute("aria-expanded", String(willOpen));
      navigation.classList.toggle("is-open", willOpen);
      document.body.classList.toggle("menu-open", willOpen);
    });

    navigation.addEventListener("click", function (event) {
      if (event.target.closest("a")) closeMenu();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && navigation.classList.contains("is-open")) {
        closeMenu();
        menuButton.focus();
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 900) closeMenu();
    });
  }

  const gallery = document.querySelector("[data-gallery]");
  const dialog = document.querySelector("[data-gallery-dialog]");
  if (!gallery || !dialog || typeof dialog.showModal !== "function") return;

  const triggers = Array.from(gallery.querySelectorAll("[data-gallery-index]"));
  const dialogImage = dialog.querySelector("[data-gallery-image]");
  const dialogCaption = dialog.querySelector("[data-gallery-caption]");
  let currentIndex = 0;
  let lastTrigger = null;

  function showImage(index) {
    currentIndex = (index + triggers.length) % triggers.length;
    const sourceImage = triggers[currentIndex].querySelector("img");
    dialogImage.src = sourceImage.currentSrc || sourceImage.src;
    dialogImage.alt = sourceImage.alt;
    dialogCaption.textContent = sourceImage.alt;
  }

  triggers.forEach(function (trigger, index) {
    trigger.addEventListener("click", function () {
      lastTrigger = trigger;
      showImage(index);
      dialog.showModal();
    });
  });

  dialog.querySelector("[data-gallery-close]").addEventListener("click", function () {
    dialog.close();
  });

  dialog.querySelector("[data-gallery-prev]").addEventListener("click", function () {
    showImage(currentIndex - 1);
  });

  dialog.querySelector("[data-gallery-next]").addEventListener("click", function () {
    showImage(currentIndex + 1);
  });

  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) dialog.close();
  });

  dialog.addEventListener("keydown", function (event) {
    if (event.key === "ArrowLeft") showImage(currentIndex - 1);
    if (event.key === "ArrowRight") showImage(currentIndex + 1);
  });

  dialog.addEventListener("close", function () {
    dialogImage.removeAttribute("src");
    if (lastTrigger) lastTrigger.focus();
  });
})();
