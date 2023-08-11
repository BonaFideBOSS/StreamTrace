$('.add-to-watchlist').on('click', async function () {
  await add_to_watchlist(this)
})

$('.del-from-watchlist').on('click', async function () {
  await del_from_watchlist(this)
})

async function add_to_watchlist(btn) {
  $('.add-to-watchlist').attr('disabled', true)
  const watchlist_id = $(btn).data('id')
  const url = `/add-to-watchlist?watchlist_id=${watchlist_id}`
  await send_request(url)
}

async function del_from_watchlist(btn) {
  $('.del-from-watchlist').attr('disabled', true)
  const watchlist_id = $(btn).data('id')
  const url = `/del-from-watchlist?watchlist_id=${watchlist_id}`
  await send_request(url, watchlist_id)
}

async function send_request(url, watchlist_id = null) {
  $.get(url)
    .done(function (response) {
      if (typeof response == "object") {
        notify(response.response)
      } else {
        notify(response)
      }
      if (watchlist_id && response.success) {
        $(`#${watchlist_id}`).remove()
      }
    }).fail(function () {
      notify("Failed to perform action.");
    }).always(function () {
      $('.watchlist-btn').attr('disabled', false)
    });
}