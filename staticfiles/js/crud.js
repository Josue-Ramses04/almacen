let profileData = {
  firstName: "Cameron",
  lastName: "Williamson",
  profileImage: "default-avatar.png"
};

function openEditModal() {
  document.getElementById('firstName').value = profileData.firstName;
  document.getElementById('lastName').value = profileData.lastName;
  document.getElementById('editModal').style.display = 'flex';
}

function closeEditModal() {
  document.getElementById('editModal').style.display = 'none';
}

document.getElementById('editForm').addEventListener('submit', (e) => {
  e.preventDefault();
  
  const firstName = document.getElementById('firstName').value.trim();
  const lastName = document.getElementById('lastName').value.trim();
  const imageFile = document.getElementById('profileImage').files[0];

  if (firstName && lastName) {
      // Actualizar datos
      profileData.firstName = firstName;
      profileData.lastName = lastName;

      // Actualizar imagen si se sube una nueva
      if (imageFile) {
          const reader = new FileReader();
          reader.onload = (e) => {
              profileData.profileImage = e.target.result;
              updateProfileDisplay();
          };
          reader.readAsDataURL(imageFile);
      }

      updateProfileDisplay();
      closeEditModal();
  }
});

function updateProfileDisplay() {
  document.getElementById('profileName').textContent = `${profileData.firstName} ${profileData.lastName}`;
  document.getElementById('profileImageDisplay').src = profileData.profileImage;
}

// Cargar datos al iniciar
updateProfileDisplay();