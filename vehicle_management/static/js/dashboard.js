// Requires HOURLY_DATA and DASHBOARD_URL globals defined in the template.

document.addEventListener("DOMContentLoaded", function () {
    const sortDateLabel = document.getElementById("sortDateLabel");
    const sortDateInput = document.getElementById("sortDateInput");

    sortDateLabel.onclick = function () {
        sortDateInput.style.display = "inline-block";
        sortDateInput.focus();
    };
    sortDateInput.onchange = function () {
        if (sortDateInput.value) {
            window.location.href = `${DASHBOARD_URL}?date=${sortDateInput.value}`;
        }
    };
    sortDateInput.onblur = function () {
        sortDateInput.style.display = "none";
    };

    const ctx = document.getElementById("vehicleChart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: HOURLY_DATA.map((d) => d.hour),
            datasets: [
                {
                    label: "Vehicles per Hour",
                    data: HOURLY_DATA.map((d) => d.count),
                    backgroundColor: "rgba(79, 70, 229, 0.6)",
                    borderColor: "rgb(79, 70, 229)",
                    borderWidth: 1,
                    borderRadius: 5,
                    maxBarThickness: 40,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1, font: { size: 12 } },
                    grid: { display: true, color: "rgba(0, 0, 0, 0.1)" },
                },
                x: { grid: { display: false }, ticks: { font: { size: 12 } } },
            },
            plugins: {
                title: {
                    display: true,
                    text: "Vehicle Traffic by Hour",
                    font: { size: 16, weight: "bold" },
                    padding: 20,
                },
                legend: { display: true, position: "top", labels: { font: { size: 12 } } },
            },
        },
    });
});
