$('form#update-personal').on('submit', async function (e) {
  e.preventDefault()
  await update_personal(this)
})

$('form#update-email').on('submit', async function (e) {
  e.preventDefault()
  await update_email(this)
})

$('form#update-password').on('submit', async function (e) {
  e.preventDefault()
  await update_password(this)
})

async function update_personal(form) {
  const data = new FormData(form)
  const params = new URLSearchParams(data).toString();
  const url = `/update-personal?${params}`
  await send_request(form, url)
}

async function update_email(form) {
  const data = new FormData(form)
  const email = data.get('email')
  const url = `/update-email?email=${email}`
  await send_request(form, url)
}

async function update_password(form) {
  const data = new FormData(form)
  const old_password = data.get('old_password')
  const new_password = data.get('new_password')
  const url = `/update-password?old=${old_password}&new=${new_password}`
  await send_request(form, url)
}

async function send_request(form, url) {
  const form_btn = $(form).find('button[type="submit"]')
  if (form.checkValidity()) {
    $.get(url)
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