// Requires HISTORY_URL global defined in the template.

document.addEventListener("DOMContentLoaded", function () {
    const label = document.getElementById("historySortDateLabel");
    const input = document.getElementById("historySortDateInput");
    if (label && input) {
        label.onclick = function () {
            input.style.display = "inline-block";
            input.focus();
        };
        input.onblur = function () {
            input.style.display = "none";
        };
    }
});

function changePage(page) {
    const params = new URLSearchParams(window.location.search);
    params.set("page", page);
    window.location.href = `${HISTORY_URL}?${params.toString()}`;
}
