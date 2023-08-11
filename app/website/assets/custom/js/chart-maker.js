Chart.defaults.plugins.tooltip.displayColors = false;
Chart.defaults.plugins.tooltip.padding = '10';

// Function to Create a DOUGHNUT Chart
function doughnut_chart(title, labels, dataset, canvas) {
  const data = {
    labels: labels,
    datasets: [{ data: dataset }]
  };

  const config = {
    type: 'doughnut',
    data: data,
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' },
        title: {
          display: true,
          text: title,
          font: { size: 20 }
        }
      }
    }
  };

  new Chart(
    document.getElementById(canvas),
    config
  );
}

// Function to Create a LINE Chart
function line_chart(title, labels, datasets, dataset_labels, canvas) {

  var legend = { display: false, position: 'bottom' }
  var data = {
    labels: labels,
    datasets: [{ data: datasets }]
  };


  if (dataset_labels.length > 1) {
    data.datasets = datasets.map((dataset, index) => ({ label: dataset_labels[index], data: dataset }))
    legend.display = true
  }

  const config = {
    type: 'line',
    data: data,
    options: {
      responsive: true,
      interaction: {
        intersect: false,
        mode: 'index',
      },
      plugins: {
        legend: legend,
        title: {
          display: true,
          text: title,
          font: { size: 20 }
        }
      }
    }
  };

  new Chart(
    document.getElementById(canvas),
    config
  );
}

// Function to Create a BAR Chart
function bar_chart(title, labels, datasets, dataset_labels, canvas) {

  var legend = { display: false, position: 'bottom' }
  var data = {
    labels: labels,
    datasets: [{ data: datasets }]
  };


  if (dataset_labels.length > 1) {
    data.datasets = datasets.map((dataset, index) => ({ label: dataset_labels[index], data: dataset }))
    legend.display = true
  }

  const config = {
    type: 'bar',
    data: data,
    options: {
      responsive: true,
      interaction: {
        intersect: false,
        mode: 'index',
      },
      plugins: {
        legend: legend,
        title: {
          display: true,
          text: title,
          font: { size: 20 }
        }
      }
    }
  };

  new Chart(
    document.getElementById(canvas),
    config
  );
}