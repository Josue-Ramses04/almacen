document.addEventListener("DOMContentLoaded", function () {
    // Asignar eventos a botones después de que el DOM esté cargado
    document.getElementById("editForm").addEventListener("submit", handleFormSubmit);
    document.querySelector(".edit-button").addEventListener("click", openEditModal);
    document.querySelector(".close").addEventListener("click", closeEditModal);

    // Cargar datos del usuario desde Django
    fetch("/api/profile/")
        .then(response => response.json())
        .then(data => {
            document.getElementById('profileName').textContent = `${data.first_name} ${data.last_name}`;
            document.getElementById('profileImageDisplay').src = data.profile_image || "/static/images/default-avatar.png";

            // Guardar datos en el objeto para edición
            profileData = {
                firstName: data.first_name,
                lastName: data.last_name,
                profileImage: data.profile_image || "/static/images/default-avatar.png"
            };
        })
        .catch(error => console.error("Error al obtener datos del perfil:", error));
});

function openEditModal() {
    document.getElementById('firstName').value = profileData.firstName;
    document.getElementById('lastName').value = profileData.lastName;
    document.getElementById('editModal').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

function handleFormSubmit(e) {
    e.preventDefault();

    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const imageFile = document.getElementById('profileImage').files[0];

    if (firstName && lastName) {
        let formData = new FormData();
        formData.append("first_name", firstName);
        formData.append("last_name", lastName);
        if (imageFile) {
            formData.append("profile_image", imageFile);
        }

        fetch("/api/profile/update/", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                profileData.firstName = data.first_name;
                profileData.lastName = data.last_name;
                if (data.profile_image) {
                    profileData.profileImage = data.profile_image;
                }
                updateProfileDisplay();
                closeEditModal();
            } else {
                console.error("Error al actualizar perfil:", data.error);
            }
        })
        .catch(error => console.error("Error en la solicitud:", error));
    }
}

function updateProfileDisplay() {
    document.getElementById('profileName').textContent = `${profileData.firstName} ${profileData.lastName}`;
    document.getElementById('profileImageDisplay').src = profileData.profileImage;
}

function getCSRFToken() {
    let csrfToken = null;
    document.cookie.split(";").forEach(cookie => {
        let [name, value] = cookie.trim().split("=");
        if (name === "csrftoken") {
            csrfToken = value;
        }
    });
    return csrfToken;
}