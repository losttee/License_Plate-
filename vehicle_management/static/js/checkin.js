// Requires CSRF_TOKEN and URLS ({recognize, saveHistory, checkVehicle}) globals.

let detectedVehicles = [];
let currentVehicleIndex = 0;
let currentProcessingType = null; // 'in' or 'out'

function hideUploadBtns() {
    document.getElementById("controls-in").classList.add("hidden");
    document.getElementById("controls-out").classList.add("hidden");
}
function showUploadBtns() {
    document.getElementById("controls-in").classList.remove("hidden");
    document.getElementById("controls-out").classList.remove("hidden");
}
function showProgressSection() {
    document.getElementById("progressSection").style.display = "block";
    document.getElementById("vehicleNavigation").style.display = "none";
}
function showResultsSection() {
    document.getElementById("progressSection").style.display = "none";
    if (detectedVehicles.length > 0) {
        document.getElementById("vehicleNavigation").style.display = "flex";
        displayCurrentVehicle();
    }
}
function updateProgress(current, total) {
    document.getElementById("progressFill").style.width = (current / total) * 100 + "%";
    document.getElementById("vehicleCounter").textContent = `Đã phát hiện ${current}/${total} xe`;
}

function displayCurrentVehicle() {
    if (detectedVehicles.length === 0) return;
    const vehicle = detectedVehicles[currentVehicleIndex];

    document.getElementById("vehicleIndex").textContent =
        `Xe ${currentVehicleIndex + 1} / ${detectedVehicles.length}`;
    document.getElementById("prevVehicle").disabled = currentVehicleIndex === 0;
    document.getElementById("nextVehicle").disabled =
        currentVehicleIndex === detectedVehicles.length - 1;

    const cameraBox =
        currentProcessingType === "in"
            ? document.getElementById("camera-in")
            : document.getElementById("camera-out");
    if (vehicle.img_b64) {
        cameraBox.innerHTML = `<img src="data:image/jpeg;base64,${vehicle.img_b64}" width="100%" style="border-radius:12px;">`;
    }

    resetVehicleInfo();
    document.getElementById("license-plate").textContent = vehicle.plate;
    document.getElementById("vehicle-model").textContent = vehicle.user_info.model || "";

    const avatarEl = document.getElementById("vehicle-avatar");
    if (vehicle.user_info.avatar_url) {
        avatarEl.src = vehicle.user_info.avatar_url;
        avatarEl.style.display = "block";
    } else {
        avatarEl.src = "";
        avatarEl.style.display = "none";
    }

    if (currentProcessingType === "in") {
        if (vehicle.status === "registered") {
            fillUserInfo(vehicle.user_info);
            document.getElementById("btn-registered").style.display = "inline-block";
            document.getElementById("btn-unregistered").style.display = "none";
            autoSaveOnce(vehicle);
        } else {
            document.getElementById("btn-registered").style.display = "none";
            document.getElementById("btn-unregistered").style.display = "inline-block";
        }
    } else if (currentProcessingType === "out") {
        fillUserInfo(vehicle.user_info);
        const btnRegistered = document.getElementById("btn-registered");
        const btnUnregistered = document.getElementById("btn-unregistered");
        if (vehicle.status === "inlot") {
            btnRegistered.textContent = "In Lot";
            btnRegistered.className = "status registered";
            btnRegistered.style.display = "inline-block";
            btnUnregistered.style.display = "none";
            autoSaveOnce(vehicle);
        } else {
            btnUnregistered.textContent = "Not In Lot";
            btnUnregistered.className = "status unregistered";
            btnUnregistered.style.display = "inline-block";
            btnRegistered.style.display = "none";
        }
    }
}

function fillUserInfo(info) {
    document.getElementById("user-name").textContent = info.user_name || "";
    document.getElementById("user-unit").textContent = info.unit || "";
    document.getElementById("issued-date").textContent = info.issued_date || "";
    document.getElementById("expired-date").textContent = info.expired_date || "";
    document.getElementById("entry-time").textContent = info.entry_time || "";
}

function autoSaveOnce(vehicle) {
    if (!vehicle.processed) {
        saveVehicleToHistory(vehicle).then(() => {
            vehicle.processed = true;
        });
    }
}

function resetVehicleInfo() {
    ["vehicle-model", "license-plate", "user-name", "user-unit", "issued-date",
        "expired-date", "entry-time", "exit-time"].forEach(
        (id) => (document.getElementById(id).textContent = "")
    );
    document.getElementById("btn-registered").style.display = "none";
    document.getElementById("btn-unregistered").style.display = "none";
    document.getElementById("manualInputBox").classList.add("hidden");
}

async function handleVideo(file, type) {
    currentProcessingType = type;
    hideUploadBtns();
    showProgressSection();
    document.getElementById("processingStatus").textContent = "Đang xử lý video...";

    const formData = new FormData();
    formData.append("video", file);
    try {
        const res = await fetch(`${URLS.recognize}?type=${type}`, {
            method: "POST",
            headers: { "X-CSRFToken": CSRF_TOKEN },
            body: formData,
        });
        const data = await res.json();
        if (data.success) {
            detectedVehicles = data.vehicles;
            currentVehicleIndex = 0;
            document.getElementById("processingStatus").textContent =
                `Hoàn thành! Phát hiện ${data.total_vehicles} xe`;
            updateProgress(data.total_vehicles, data.total_vehicles);
            setTimeout(showResultsSection, 1000);
        } else {
            document.getElementById("processingStatus").textContent =
                data.message || "Không phát hiện được xe nào";
            setTimeout(() => {
                showUploadBtns();
                document.getElementById("manualInputBox").classList.remove("hidden");
            }, 2000);
        }
    } catch (error) {
        console.error("Lỗi xử lý:", error);
        document.getElementById("processingStatus").textContent = "Có lỗi xảy ra khi xử lý video";
        setTimeout(showUploadBtns, 2000);
    }
}

async function saveVehicleToHistory(vehicle) {
    const formData = new FormData();
    formData.append("license_plate", vehicle.plate);
    formData.append("action", currentProcessingType);
    formData.append("status", vehicle.status);
    try {
        const res = await fetch(URLS.saveHistory, {
            method: "POST",
            headers: { "X-CSRFToken": CSRF_TOKEN },
            body: formData,
        });
        return (await res.json()).success;
    } catch (error) {
        console.error("Lỗi lưu lịch sử:", error);
        return false;
    }
}

function bindUploadButtons() {
    document.getElementById("confirmIn").onclick = function () {
        const file = document.getElementById("videoIn").files[0];
        if (file) handleVideo(file, "in");
    };
    document.getElementById("confirmOut").onclick = function () {
        const file = document.getElementById("videoOut").files[0];
        if (file) handleVideo(file, "out");
    };
}

function resetToInitialState() {
    detectedVehicles = [];
    currentVehicleIndex = 0;
    currentProcessingType = null;
    document.getElementById("progressSection").style.display = "none";
    document.getElementById("vehicleNavigation").style.display = "none";
    document.getElementById("camera-in").innerHTML = `
        <div class="camera-controls" id="controls-in">
            <input type="file" id="videoIn" accept="video/*" class="upload-btn">
            <button id="confirmIn" class="confirm-btn">Confirm In</button>
        </div>`;
    document.getElementById("camera-out").innerHTML = `
        <div class="camera-controls" id="controls-out">
            <input type="file" id="videoOut" accept="video/*" class="upload-btn">
            <button id="confirmOut" class="confirm-btn">Confirm Out</button>
        </div>`;
    resetVehicleInfo();
    showUploadBtns();
    bindUploadButtons();
}

document.addEventListener("DOMContentLoaded", function () {
    bindUploadButtons();

    document.getElementById("prevVehicle").onclick = function () {
        if (currentVehicleIndex > 0) {
            currentVehicleIndex--;
            displayCurrentVehicle();
        }
    };
    document.getElementById("nextVehicle").onclick = function () {
        if (currentVehicleIndex < detectedVehicles.length - 1) {
            currentVehicleIndex++;
            displayCurrentVehicle();
        }
    };

    document.getElementById("btn-unregistered").onclick = async function () {
        const vehicle = detectedVehicles[currentVehicleIndex];
        if (vehicle.processed) return;
        if (await saveVehicleToHistory(vehicle)) {
            vehicle.processed = true;
            alert("Đã lưu xe chưa đăng ký vào lịch sử!");
            if (currentVehicleIndex < detectedVehicles.length - 1) {
                currentVehicleIndex++;
                displayCurrentVehicle();
            } else {
                resetToInitialState();
            }
        } else {
            alert("Có lỗi khi lưu thông tin xe");
        }
    };

    document.getElementById("license-plate").onclick = function () {
        document.getElementById("manualInputBox").classList.remove("hidden");
        document.getElementById("manualPlate").value =
            detectedVehicles.length > 0 ? detectedVehicles[currentVehicleIndex].plate : "";
    };

    document.getElementById("manualConfirm").onclick = async function () {
        const newPlate = document.getElementById("manualPlate").value.trim();
        if (!newPlate) {
            alert("Vui lòng nhập biển số!");
            return;
        }
        try {
            let url = `${URLS.checkVehicle}?plate=${encodeURIComponent(newPlate)}`;
            if (currentProcessingType === "out") url += "&type=out";
            const data = await (await fetch(url)).json();
            const status = data.status || (data.registered ? "inlot" : "not_in_lot");
            const info = data.vehicle ? data.vehicle : { license_plate: newPlate, model: "" };

            if (detectedVehicles.length === 0) {
                detectedVehicles = [
                    { plate: newPlate, status, user_info: info, img_b64: "", processed: false },
                ];
                currentVehicleIndex = 0;
                showResultsSection();
            } else {
                const v = detectedVehicles[currentVehicleIndex];
                v.plate = newPlate;
                v.status = status;
                v.user_info = info;
            }

            document.getElementById("manualInputBox").classList.add("hidden");
            displayCurrentVehicle();

            const v = detectedVehicles[currentVehicleIndex];
            if (v.status === "inlot" && !v.processed) {
                await saveVehicleToHistory(v);
                v.processed = true;
            }
        } catch (error) {
            alert("Lỗi kiểm tra biển số!");
        }
    };
});
