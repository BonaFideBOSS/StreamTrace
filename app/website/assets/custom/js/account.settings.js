$('form#update-personal').on('submit', async function (e) {
  e.preventDefault()
  const url = `/update-personal`
  await send_request(this, url)
})

$('form#update-email').on('submit', async function (e) {
  e.preventDefault()
  const url = `/update-email`
  await send_request(this, url)
})

$('form#update-password').on('submit', async function (e) {
  e.preventDefault()
  const url = `/update-password`
  await send_request(this, url)
})

async function send_request(form, url) {
  const form_btn = $(form).find('button[type="submit"]')
  const data = $(form).serialize()
  if (form.checkValidity()) {
    $.post(url, data)
      .done(function (response) {
        notify(response)
        $(form).removeClass('was-validated')
      }).fail(function () {
        notify("Failed to perform action.");
      }).always(function () {
        $(form_btn).html("Update");
        $(form_btn).attr("disabled", false);
      });
  }
}