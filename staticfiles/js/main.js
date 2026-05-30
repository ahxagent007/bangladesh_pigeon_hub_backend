function toggleMobileNav() {
  document.getElementById('mobileNav').classList.toggle('open');
}

// Auto-dismiss flash messages after 4s
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => el.remove(), 4000);
});

// Image preview on file input
function previewImage(input, previewId) {
  const preview = document.getElementById(previewId);
  if (!preview) return;
  const file = input.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = e => {
      preview.src = e.target.result;
      preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }
}