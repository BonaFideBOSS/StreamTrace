$('#delete-sub').on('click', async function () {
  $(this).attr('disabled', true)
  const sub_id = $(this).data('sub-id')
  const url = `/delete-sub/${sub_id}/`
  await send_request(this, url)
})

async function send_request(btn, url) {
  await $.get(url)
    .done(async function (response) {
      if (response.success) {
        history.back()
      } else {
        notify(response.response)
      }
    }).fail(function () {
      notify("Failed to perform action.");
    }).always(function () {
      $(btn).attr("disabled", false);
    });
}