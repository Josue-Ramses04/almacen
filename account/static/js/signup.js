function validateEmail(input) {
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailPattern.test(input.value)) {
        input.setCustomValidity("Introduce un correo electrónico válido.");
    } else {
        input.setCustomValidity("");
    }
}
