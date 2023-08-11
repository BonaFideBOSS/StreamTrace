$("#sidebar-toggle").on("click", function () {
  $(".sidebar").toggleClass("collapsed");
});

function previewFile(fileInput, previewId) {
  const preview = document.getElementById(previewId);

  for (const file of fileInput.files) {
    const reader = new FileReader();
    reader.onload = function (e) {
      if (file.type.startsWith('image/')) {
        const img = `<img src="${e.target.result}">`
        preview.innerHTML = img
      }
    };
    reader.readAsDataURL(file);
  }
}