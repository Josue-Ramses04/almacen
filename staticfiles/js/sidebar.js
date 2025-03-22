const cloud = document.getElementById("cloud");
const barraLateral = document.querySelector(".barra-lateral");
const spans = document.querySelectorAll("span");
const palanca = document.querySelector(".switch");
const circulo = document.querySelector(".circulo");
const menu = document.querySelector(".menu");
const main = document.querySelector("main");
const toggleButton = document.getElementById("toggleMode");
const body = document.body;

// Al cargar la página, restaurar estados desde localStorage
document.addEventListener("DOMContentLoaded", () => {
    // Restaurar modo oscuro
    const darkMode = localStorage.getItem("darkMode");
    if (darkMode === "true") {
        body.classList.add("dark-mode");
        circulo.classList.add("prendido");
    } else {
        body.classList.remove("dark-mode");
        circulo.classList.remove("prendido");
    }

    // Restaurar estado de la barra lateral
    const barraEstado = localStorage.getItem("barraLateral");
    if (barraEstado === "mini") {
        barraLateral.classList.add("mini-barra-lateral");
        main.classList.add("min-main");
        spans.forEach((span) => span.classList.add("oculto"));
    } else {
        barraLateral.classList.remove("mini-barra-lateral");
        main.classList.remove("min-main");
        spans.forEach((span) => span.classList.remove("oculto"));
    }
});

// Función para alternar la barra lateral y guardar el estado
function toggleBarra() {
    barraLateral.classList.toggle("mini-barra-lateral");
    main.classList.toggle("min-main");
    spans.forEach((span) => span.classList.toggle("oculto"));

    // Guardar el estado en localStorage
    if (barraLateral.classList.contains("mini-barra-lateral")) {
        localStorage.setItem("barraLateral", "mini");
    } else {
        localStorage.setItem("barraLateral", "normal");
    }
}

menu.addEventListener("click", toggleBarra);
cloud.addEventListener("click", toggleBarra);

// Función para alternar el modo oscuro y guardar el estado
function toggleDarkMode() {
    body.classList.toggle("dark-mode");
    circulo.classList.toggle("prendido");

    // Guardar el estado del modo oscuro en localStorage
    if (body.classList.contains("dark-mode")) {
        localStorage.setItem("darkMode", "true");
    } else {
        localStorage.setItem("darkMode", "false");
    }
}

palanca.addEventListener("click", toggleDarkMode);
toggleButton.addEventListener("click", toggleDarkMode);


// Función para cambiar entre modo claro y oscuro
