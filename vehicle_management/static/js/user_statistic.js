// Requires CSRF_TOKEN and URLS ({add}) globals defined in the template.

function postForm(url, formData) {
    return fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": CSRF_TOKEN },
        body: formData,
    }).then((r) => r.json());
}

document.addEventListener("DOMContentLoaded", function () {
    const addBtn = document.getElementById("addUserBtn");
    if (!addBtn) return; // guard role: no manager controls rendered

    const modal = document.getElementById("addUserModal");
    addBtn.onclick = () => (modal.style.display = "flex");
    document.getElementById("closeUserModalBtn").onclick = () =>
        (modal.style.display = "none");

    document.getElementById("addUserForm").onsubmit = async function (e) {
        e.preventDefault();
        const result = await postForm(URLS.add, new FormData(this));
        if (result.message) {
            location.reload();
        } else {
            alert("Thêm xe thất bại: " + (result.error || JSON.stringify(result.errors || {})));
        }
    };

    document.querySelectorAll(".edit-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            const tr = btn.closest("tr");
            if (btn.textContent !== "Edit") return;

            const id = tr.getAttribute("data-id");
            const originalValues = [];
            for (let i = 1; i < 8; i++) {
                const td = tr.children[i];
                const value = td.textContent;
                originalValues.push(value);
                td.innerHTML = `<input class="editing-input" value="${value}" ${
                    i === 6 || i === 7 ? 'type="date"' : 'type="text"'
                }>`;
                if (i === 6 || i === 7) {
                    const parts = value.split("/");
                    if (parts.length === 3) {
                        td.querySelector("input").value = `${parts[2]}-${parts[1]}-${parts[0]}`;
                    }
                }
            }

            const avatarTd = tr.children[0];
            const originalAvatarHTML = avatarTd.innerHTML;
            avatarTd.innerHTML = `<input type="file" class="edit-avatar-input" accept="image/*">`;

            btn.textContent = "Save";
            btn.className = "save-btn";
            const cancelBtn = document.createElement("button");
            cancelBtn.textContent = "Cancel";
            cancelBtn.className = "cancel-btn";
            btn.after(cancelBtn);

            btn.onclick = async function () {
                const formData = new FormData();
                formData.append("user_name", tr.children[1].querySelector("input").value);
                formData.append("unit", tr.children[2].querySelector("input").value);
                formData.append("model", tr.children[3].querySelector("input").value);
                formData.append("license_plate", tr.children[4].querySelector("input").value);
                formData.append("phone_number", tr.children[5].querySelector("input").value);
                formData.append("issued_date", tr.children[6].querySelector("input").value);
                formData.append("expired_date", tr.children[7].querySelector("input").value);
                const avatarInput = tr.children[0].querySelector('input[type="file"]');
                if (avatarInput && avatarInput.files.length > 0) {
                    formData.append("avatar", avatarInput.files[0]);
                }
                const result = await postForm(`/update_vehicle/${id}/`, formData);
                if (result.success) {
                    location.reload();
                } else {
                    alert("Cập nhật thất bại: " + (result.error || JSON.stringify(result.errors || {})));
                }
            };

            cancelBtn.onclick = function () {
                avatarTd.innerHTML = originalAvatarHTML;
                for (let i = 1; i < 8; i++) {
                    tr.children[i].textContent = originalValues[i - 1];
                }
                btn.textContent = "Edit";
                btn.className = "edit-btn";
                cancelBtn.remove();
                btn.onclick = null;
            };
        });
    });

    document.querySelectorAll(".delete-btn").forEach(function (btn) {
        btn.addEventListener("click", async function () {
            if (!confirm("Are you sure you want to delete this vehicle?")) return;
            const tr = btn.closest("tr");
            const id = tr.getAttribute("data-id");
            const result = await postForm(`/delete_vehicle/${id}/`, new FormData());
            if (result.success) {
                tr.remove();
            } else {
                alert("Xóa thất bại: " + (result.error || "Lỗi không xác định"));
            }
        });
    });
});
