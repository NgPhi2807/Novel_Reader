
  let selectedCategories = []; // Lưu danh sách thể loại đã chọn

function showCategorySelect() {
    let categoryList = document.getElementById("category-list");

    // Chỉ hiển thị nếu chưa chọn đủ thể loại
    if (selectedCategories.length < document.querySelectorAll(".category-option").length) {
        categoryList.style.display = "block";
    }
}

function addCategory(id, name) {
    // Kiểm tra nếu thể loại đã có trong danh sách
    if (selectedCategories.some(cat => cat.id === id)) return;

    // Thêm vào danh sách
    selectedCategories.push({ id, name });

    // Cập nhật giao diện
    updateTextarea();

    // Ẩn danh sách chọn thể loại
    document.getElementById("category-list").style.display = "none";
}

function removeCategory(id) {
    // Xóa khỏi danh sách
    selectedCategories = selectedCategories.filter(cat => cat.id !== id);

    // Cập nhật giao diện
    updateTextarea();
}

function updateTextarea() {
    let container = document.getElementById("selected-categories");
    let input = document.getElementById("categories-input");

    // Xóa nội dung cũ
    container.innerHTML = "";

    if (selectedCategories.length === 0) {
        container.innerHTML = '<span class="placeholder">Chọn thể loại...</span>';
    } else {
        selectedCategories.forEach(cat => {
            let badge = document.createElement("span");
            badge.classList.add("badge");

            badge.innerHTML = `
                <span>${cat.name}</span>
                <span class="remove" onclick="removeCategory('${cat.id}')">X</span>
            `;

            container.appendChild(badge);
        });
    }

    // Cập nhật input ẩn (để gửi dữ liệu lên server)
    input.value = selectedCategories.map(cat => cat.id).join(",");
}

// Đóng danh sách khi click ra ngoài
document.addEventListener("click", function (event) {
    let dropdown = document.getElementById("category-list");
    let container = document.getElementById("selected-categories");

    if (!dropdown.contains(event.target) && !container.contains(event.target)) {
        dropdown.style.display = "none";
    }
});
