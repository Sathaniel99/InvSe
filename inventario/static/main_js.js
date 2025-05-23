const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle-tooltip="tooltip"]');
const tooltipList = [...tooltipTriggerList].map(
  (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
);

const btn_theme = document.getElementById("btn-theme");
const html_container = document.documentElement;

document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme") || "light";
  html_container.setAttribute("data-bs-theme", savedTheme);
  if (savedTheme === "dark") {
    btn_theme.children[0].classList.add("bi-moon");
    btn_theme.children[0].classList.remove("bi-sun");
  } else {
    btn_theme.children[0].classList.add("bi-sun");
    btn_theme.children[0].classList.remove("bi-moon");
  }
});


btn_theme.addEventListener("click", () => {
  btn_theme.children[0].classList.toggle("bi-sun");
  btn_theme.children[0].classList.toggle("bi-moon");

  const currentTheme = html_container.getAttribute("data-bs-theme");
  const newTheme = currentTheme === "light" ? "dark" : "light";
  html_container.setAttribute("data-bs-theme", newTheme);

  localStorage.setItem("theme", newTheme);
});

// Animar numeros
function animateNumber(targetElement, start, end, duration){
  let startTime = null;

  function step(timestamp){
    if (!startTime) startTime = timestamp;
    const progress = Math.min((timestamp - startTime) / duration, 1);
    const currentValue = Math.floor(start + progress * (end - start))
    targetElement.textContent = currentValue;
    if(progress < 1){
      requestAnimationFrame(step);
    }
  }
  requestAnimationFrame(step);
}

const counters = document.querySelectorAll('.counter-frame');

counters.forEach(counter => {
  const targetNumber = parseInt(counter.textContent, 10);
  if(!isNaN(targetNumber)){
    animateNumber(counter, 0, targetNumber, 1500);
  }
  else{
    alert("El contenido el div no es un numero valido:" , counter.textContent)
  }
})


///////////////////////////////////////////////////////////////////////////////////////////////////
const aside_hide = document.getElementById("aside-hide");
const main_aside = document.getElementById("main-aside");

main_aside.style.width = localStorage.getItem('aside_hidenmode') == 'hide'? '5rem' : '15rem';

aside_hide.addEventListener('click', () => {
    token = localStorage.getItem('aside_hidenmode');
    if (token == 'hide') {
        localStorage.setItem('aside_hidenmode', 'unhide');
        main_aside.style.width = '15rem';
    }
    else {
        localStorage.setItem('aside_hidenmode', 'hide');
        main_aside.style.width = '5rem';
    }
});

// IMPLEMENTAR LOS TOAST ALERT