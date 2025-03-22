


// Script para alternar la visibilidad de la contraseña
const togglePassword = document.getElementById("togglePassword");
const passwordField = document.getElementById("password");

togglePassword.addEventListener("click", function () {
    // Cambiar el tipo del campo de contraseña entre 'text' y 'password'
    if (passwordField.type === "text") {
        passwordField.type = "password";
        togglePassword.classList.remove("fa-eye-slash");
        togglePassword.classList.add("fa-eye");
    } else {
        passwordField.type = "text";
        togglePassword.classList.remove("fa-eye");
        togglePassword.classList.add("fa-eye-slash");
    }
});