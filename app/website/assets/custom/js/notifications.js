$("#notifications").on('shown.bs.offcanvas', async function () {
  await update_notifications()
})

async function update_notifications() {
  data = await user_subs()
  var inbox = ""
  if (data.length != 0) {
    data.forEach(item => {
      const service = item.service[0]
      const expiry = new Date(item.expiry.$date)
      var expired = ''
      var duration = ""
      var archive_btn = ""
      const today = new Date()
      if (today > expiry) {
        expired = 'text-danger'
        duration = `has <span class="fw-medium">expired</span>`
        archive_btn = `<div class="inbox-overlay"></div>
        <button onclick="archive_sub(this)" data-id="${item._id.$oid}" class="btn btn-dark">
          <i class="bi bi-trash"></i>
        </button>`
      } else {
        duration = (expiry - today) / (1000 * 60 * 60 * 24)
        duration = `will expire in <span class="fw-medium">${Math.ceil(duration)} days</span>`
      }
      inbox += `
        <div id="inbox_${item._id.$oid}" class="inbox-item row align-items-center text-secondary border-bottom pb-3 mb-3">
          ${archive_btn}
          <div class="col-2">
            <div class="logo-container-sm"><img src="data:image/*;base64,${service.logo}" /></div>
          </div>
          <div class="col-10">
            <p class="mb-0 ${expired}">
              Your <span class="fw-medium">${service.name}</span> subscription ${duration}
            </p>
          </div>
        </div>`
    });
    $('#notifications .offcanvas-body').html(inbox)
  }
}

async function user_subs() {
  var user_subs = []
  await $.get("/user-subs?archived=false").done(function (data) {
    if (data) {
      user_subs = JSON.parse(data)
    }
  });
  return user_subs
}

async function archive_sub(btn) {
  $(btn).attr("disabled", true);
  const sub_id = $(btn).data('id')
  $.post(`/archive-sub`, { "sub_id": sub_id })
    .done(function (response) {
      notify(response.response)
      if (response.success) {
        $(`#inbox_${sub_id}`).remove()
      }
    }).fail(function () {
      notify("Failed to perform action.");
    }).always(function () {
      $(btn).attr("disabled", false);
    });
}