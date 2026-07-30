(function () {
  "use strict";

  const menuButton = document.querySelector(".menu-toggle");
  const navigation = document.querySelector(".site-nav");
  const backgroundRegions = [
    document.querySelector(".site-main"),
    document.querySelector(".site-footer")
  ].filter(Boolean);

  function setBackgroundInert(isInert) {
    backgroundRegions.forEach(function (region) {
      region.inert = isInert;
    });
  }

  function closeMenu(restoreFocus) {
    if (!menuButton || !navigation) return;
    menuButton.setAttribute("aria-expanded", "false");
    navigation.classList.remove("is-open");
    document.body.classList.remove("menu-open");
    setBackgroundInert(false);
    if (restoreFocus) menuButton.focus();
  }

  if (menuButton && navigation) {
    menuButton.addEventListener("click", function () {
      const willOpen = menuButton.getAttribute("aria-expanded") !== "true";
      if (!willOpen) {
        closeMenu(false);
        return;
      }

      menuButton.setAttribute("aria-expanded", "true");
      navigation.classList.add("is-open");
      document.body.classList.add("menu-open");
      setBackgroundInert(true);

      const firstLink = navigation.querySelector("a");
      if (firstLink) firstLink.focus();
    });

    navigation.addEventListener("click", function (event) {
      if (event.target.closest("a")) closeMenu(false);
    });

    document.addEventListener("keydown", function (event) {
      if (!navigation.classList.contains("is-open")) return;

      if (event.key === "Escape") {
        closeMenu(true);
        return;
      }

      if (event.key === "Tab") {
        const focusable = [menuButton].concat(Array.from(navigation.querySelectorAll("a")));
        const first = focusable[0];
        const last = focusable[focusable.length - 1];

        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 900) closeMenu(false);
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
