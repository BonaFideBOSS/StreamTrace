// Disabling form submissions if there are invalid fields
(() => {
  'use strict'

  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  const forms = document.querySelectorAll('.needs-validation')

  // Loop over them and prevent submission
  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
      }

      form.classList.add('was-validated')
    }, false)
  })
})()

// Clear previous requests
if (window.history.replaceState) {
  window.history.replaceState(null, null, window.location.href);
}

// Tooltips
function enable_tooltips() {
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
  const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
}
enable_tooltips()

// Notification Toast
function notify(message, delay = 5) {
  delay = delay * 1000
  toast_container = document.getElementById("notification-toast");
  const wrapper = document.createElement("div");
  wrapper.classList.add("toast", "text-bg-purple", "shadow-lg", "border-0");
  wrapper.setAttribute("data-bs-delay", delay);
  wrapper.innerHTML =
    `<div class="toast-header border-0">
      <img src="/assets/img/favico.ico" width="20" class="me-2">
      <strong class="me-auto">StreamTrace</strong>
      <small>Just Now</small>
      <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
    </div>
    <div class="toast-body fs-6">${message}</div>`;
  toast_container.append(wrapper);
  const toast = new bootstrap.Toast(wrapper);
  toast.show();
}

// Setting current year
function set_current_date() {
  const current_date = new Date();
  $(".current-year").html(current_date.getUTCFullYear());
}
set_current_date();

// Theme Changer
$(".theme").on("click", function () {
  $.get("/theme-changer").done(function (theme) {
    if (theme == "light") {
      $(".theme").html('<i class="bi bi-sun-fill text-warning"></i>');
    } else {
      $(".theme").html('<i class="bi bi-moon-fill text-white"></i>');
    }
    $("html").attr("data-bs-theme", theme);
  });
});

// Scroll to Top Button
let calcScrollValue = () => {
  let scrollProgress = document.getElementById("scroll-to-top");
  let pos = document.documentElement.scrollTop;
  let calcHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
  let scrollValue = Math.round((pos * 100) / calcHeight);
  if (pos > 100) {
    $(scrollProgress).fadeIn()
    scrollProgress.style.display = "grid";
  } else {
    $(scrollProgress).fadeOut('fast')
  }
  scrollProgress.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  scrollProgress.style.background = `conic-gradient(var(--bs-purple) ${scrollValue}%, #d7d7d7 ${scrollValue}%)`;
};

window.onscroll = calcScrollValue;
window.onload = calcScrollValue;

// Disable submit button on form submission
$('form').on('submit', function () {
  const loader = `<span class="spinner-grow spinner-grow-sm"></span><span role="status">Loading...</span>`
  const btn = $(this).find('button[type="submit"]')
  if (this.checkValidity()) {
    $(btn).attr('disabled', true)
    $(btn).addClass('d-flex align-items-center gap-2')
    $(btn).html(loader)
  }
})