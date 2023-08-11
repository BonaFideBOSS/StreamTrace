$(document).ready(async function () {
  await get_user_subs()
  $("#user-subs_info").appendTo($("#table-summary"));
  $("#user-subs_paginate").appendTo($("#table-pagination"));

  await sum_of_amount_by_services()
  await monthly_breakdown()
  await get_user_watchlist()
});

const streaming_services = new Set()
var sub_table;
async function get_user_subs() {
  const url = "/user-subs";
  sub_table = $("#user-subs").DataTable({
    ajax: { url: `${url}`, dataSrc: "" },
    columns: [
      {
        data: "service",
        render: function (data, type, row) {
          const service = data[0]
          const logo = `<img src="data:image/*;base64,${service.logo}">`
          const name = service.name
          streaming_services.add(name)
          const img = `<div class="logo-container-sm">${logo}</div>`
          const container = `<div class="d-flex align-items-center gap-2">${img}<span>${name}</span></div>`
          return container;
        },
      },
      { data: "name", createdCell: function (cell) { $(cell).addClass('text-start') } },
      { data: "amount" },
      {
        data: "expiry",
        render: function (data) {
          const date = new Date(data.$date)
          const day = String(date.getDate()).padStart(2, '0');
          const month = String(date.getMonth() + 1).padStart(2, '0');
          const year = date.getFullYear();
          return `${day}/${month}/${year}`
        }
      },
      {
        data: "expiry",
        render: function (data) {
          const date = new Date(data.$date)
          var status_icon = `<i class="bi bi-circle-fill text-success"></i>`
          if (new Date() > date) {
            status_icon = `<i class="bi bi-circle-fill text-danger"></i>`
          }
          return status_icon
        },
        createdCell: function (cell, data) {
          const date = new Date(data.$date)
          var status = new Date() > date ? "Inactive" : "Active";
          $(cell).attr('data-value', status)
        }
      },
      {
        data: "_id",
        render: function (data) {
          const sub_id = data.$oid
          return `<a href="/subscriptions/manage/${sub_id}" class="btn btn-dark"><i class="bi bi-gear"></i></a>`
        }
      }
    ],
    dom: "rtip",
    order: [[4, "desc"]],
    columnDefs: [
      {
        targets: [-1],
        orderable: false,
      },
    ],

    initComplete: async function () {
      streaming_services.forEach(stream => { $('#stream-filter').append(`<option>${stream}</option>`) })
      $("select,input").attr("disabled", false);
      tableTotal();
      sub_table.on("draw.dt order.dt search.dt page.dt row.add row.remove", function () {
        tableTotal();
        // Enable inputs
        $("select,input").attr("disabled", false);
      });
    },
  });
}

$("#entries").on("change", function () {
  var selectedValue = $(this).val();
  sub_table.page.len(selectedValue).draw();
});
$("#stream-filter").on("change", function () {
  var selectedValue = $(this).val();
  sub_table.columns(0).search(selectedValue).draw();
});
$("#status-filter").on("change", function () {
  var selectedValue = $(this).val();
  sub_table.columns(4).search(selectedValue).draw();
});
$("#tablesearch").on("input", function () {
  var selectedValue = $(this).val();
  sub_table.search(selectedValue).draw();
});

function tableTotal() {
  var row = document.querySelectorAll("#user-subs tbody tr");
  var total_amount = 0;
  for (var i = 0; i < row.length; i++) {
    if (
      row[i]
        .querySelectorAll("td")[0]
        .classList.contains("dataTables_empty")
    ) {
    } else {
      total_amount += parseFloat(row[i].querySelectorAll("td")[2].textContent.replace(",", ""));
    }
  }
  $("#total-amount").html(total_amount.toLocaleString("en-US"));
}

// Statistics
async function sum_of_amount_by_services() {
  const canvas = 'sum-of-amount-by-services'
  if ($(`#${canvas}`).length != 0) {
    $.get("/sum-of-amount-by-services").done(function (data) {
      if (data) {
        data = JSON.parse(data)
        // Labels
        var labels = data.map(key => key.service)
        // Dataset
        var dataset = data.map(key => key.sum)
        // Create doughnut chart
        doughnut_chart("Sum of Expenses by Services", labels, dataset, canvas)
      }
    });
  }
}

async function monthly_breakdown() {
  const canvas = 'monthly-breakdown'
  if ($(`#${canvas}`).length != 0) {
    $.get("/monthly-breakdown").done(function (data) {
      if (data) {
        data = JSON.parse(data)
        // Labels
        var labels = data.map(key => key.month)
        labels = labels.map(i => readable_month_short(i))
        // Dataset
        var dataset = data.map(key => key.sum)
        // Create chart
        bar_chart("Monthly Breakdown", labels, dataset, [], canvas)
      }
    });
  }
}

function readable_month_short(month) {
  var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return months[month - 1];
}

// User Watchlist
async function get_user_watchlist() {
  $.get("/get-db-watchlist").done(function (data) {
    if (data) {
      data = JSON.parse(data)
      if (data.length != 0) {
        const watchlist_count = parseInt($('#user-watchlist').data('count'))
        var watchlist = ""
        data.forEach(title => {
          watchlist += `<div class="col">
          <div class="sw-card card text-bg-dark border-0">
            <img src="${title.poster}" class="card-img">
          </div>
          <div class="mt-2">
            <h6>${title.title} (${title.year})</h6>
            <span class="badge text-bg-dark fw-normal d-inline-flex gap-1 align-items-center">
              <i class="bi bi-star-fill text-warning"></i>
              <span>${title.rating}</span>
            </span>
            <span class="badge text-bg-dark fw-normal">${title.type}</span>
          </div>
        </div>`
        })

        if (watchlist_count > data.length) {
          watchlist += `
            <div class="col">
              <div class="sw-card card border border-1 h-75 border-secondary border-dashed flex-column justify-content-center align-items-center">
                <a class="stretched-link link-secondary fw-medium" href="/watchlist">See all</a>
              </div>
            </div>`
        }

        $('#user-watchlist').html(watchlist)
      }
    }
  });
}