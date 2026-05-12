// static/analytics/js/dashboard.js
Chart.register(window["chartjs-plugin-zoom"]);

async function initRoubleChart(apiUrl) {
  const response = await fetch(apiUrl);
  const data = await response.json();
  const ctx = document.getElementById("roubleChart").getContext("2d");

  // MATHEMATICAL FIX: Convert raw values into base-10 exponents right here
  // If a value is 0 or tiny, we guard it with log10(1e-12) -> -12
  const mapToLogScale = (series) =>
    series.points.map((p) => {
      const rawVal = parseFloat(p.value);
      const safeVal = rawVal > 0 ? rawVal : 1e-12;
      return { x: p.date, y: Math.log10(safeVal) };
    });

  const mapVolatility = (series) =>
    series.points.map((p) => ({ x: p.date, y: p.volatility }));

  const datasets = [
    {
      label: data.imperial.label,
      data: mapToLogScale(data.imperial),
      borderColor: data.imperial.color,
      backgroundColor: data.imperial.color,
      yAxisID: "yPrice",
      pointRadius: data.imperial.points.map((p) => (p.is_milestone ? 5 : 0)),
      borderWidth: 2,
    },
    {
      label: data.kerenski.label,
      data: mapToLogScale(data.kerenski),
      borderColor: data.kerenski.color,
      backgroundColor: data.kerenski.color,
      yAxisID: "yPrice",
      pointRadius: data.kerenski.points.map((p) => (p.is_milestone ? 5 : 0)),
      borderWidth: 2,
    },
    {
      label: data.sovznak.label,
      data: mapToLogScale(data.sovznak),
      borderColor: data.sovznak.color,
      backgroundColor: data.sovznak.color,
      yAxisID: "yPrice",
      pointRadius: data.sovznak.points.map((p) => (p.is_milestone ? 5 : 0)),
      borderWidth: 2,
    },
    {
      label: "Systemic Volatility",
      data: mapVolatility(data.sovznak),
      borderColor: "rgba(0, 0, 0, 0.2)",
      backgroundColor: "rgba(0, 0, 0, 0.02)",
      fill: true,
      yAxisID: "yVol",
      pointRadius: 0,
      borderWidth: 1,
    },
  ];

  new Chart(ctx, {
    type: "line",
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: "time",
          time: { unit: "month", displayFormats: { month: "MM/yyyy" } },
        },
        yPrice: {
          type: "linear", // Using linear scale on log data gives pixel-perfect distribution
          position: "left",
          min: -13, // Floor padding below 10^-12
          max: 1, // Ceiling padding above 10^0
          title: { display: true, text: "Currency Value (Log10 Power)" },
          ticks: {
            // Change raw exponents (-1, -2, -6) into clear historical labels
            callback: function (value) {
              if (value === 0) return "1.0 (Parity)";
              return "10^" + value;
            },
          },
        },
        yVol: {
          type: "linear",
          position: "right",
          min: 0,
          title: { display: true, text: "Volatility Index" },
          grid: { drawOnChartArea: false }, // Cleans up conflicting gridlines
        },
      },
      plugins: {
        zoom: {
          zoom: {
            wheel: { enabled: true },
            pinch: { enabled: true },
            mode: "x",
          },
          pan: { enabled: true, mode: "x", modifierKey: "ctrl" },
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              let label = context.dataset.label || "";
              if (label) label += ": ";
              if (context.dataset.yAxisID === "yPrice") {
                // Revert back to standard float presentation for tooltips on hover
                const realValue = Math.pow(10, context.raw.y);
                label += realValue.toExponential(4) + " Gold Parity";
              } else {
                label += context.raw.y.toFixed(4);
              }
              return label;
            },
            footer: (items) => {
              const item = items[0];
              const label = item.dataset.label.toLowerCase();
              let key = "sovznak";
              if (label.includes("imperial")) key = "imperial";
              if (label.includes("kerenski")) key = "kerenski";

              const meta = data[key]?.points[item.dataIndex];
              return meta?.event_name ? `📍 Event: ${meta.event_name}` : "";
            },
          },
        },
      },
    },
  });
}
