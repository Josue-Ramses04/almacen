
document.addEventListener("DOMContentLoaded", () => {
    const toggleButton = document.getElementById("toggleMode");
    const body = document.body;

    // Verifica si el usuario ya tiene una preferencia guardada
    if (localStorage.getItem("theme") === "dark") {
        body.classList.add("dark-mode");
    }

    // Cambia el modo al hacer clic en el botón
    toggleButton.addEventListener("click", () => {
        body.classList.toggle("dark-mode");

        // Guarda la preferencia en localStorage
        if (body.classList.contains("dark-mode")) {
            localStorage.setItem("theme", "dark");
        } else {
            localStorage.setItem("theme", "light");
        }
    });
});