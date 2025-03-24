document.addEventListener("DOMContentLoaded", function () {

    const chapterItems = document.querySelectorAll(".chapter-item");
    const editBox = document.getElementById("editChapterBox");
    const editChapterSection = document.getElementById("editChapterSection");
    const addChapterBox = document.getElementById("addChapterSection");
    const chapterTitle = document.getElementById("chapterTitle");
    const myTextArea = document.getElementById("editor");
    const addChapterBtn = document.getElementById("addChapter");
    const cancelEdit = document.getElementById("cancelEdit");
    const cancelAdd = document.getElementById("cancelAdd");

    let activePopup = null;

    // Ẩn các form ban đầu
    editChapterSection.style.display = "none";
    addChapterBox.style.display = "none";

    // Xử lý danh sách chương
    chapterItems.forEach(item => {
        const popup = item.querySelector(".popup-menu");
        const editBtn = popup?.querySelector(".edit-btn");
        const deleteBtn = popup?.querySelector(".delete-btn");

        if (popup) popup.style.display = "none";

        item.addEventListener("click", function (e) {
            e.stopPropagation();
            if (activePopup && activePopup !== popup) activePopup.style.display = "none";
            if (popup) {
                popup.style.display = popup.style.display === "block" ? "none" : "block";
                activePopup = popup.style.display === "block" ? popup : null;
            }
        });

        if (editBtn) {
            editBtn.addEventListener("click", function (e) {
                e.stopPropagation();
                chapterTitle.value = item.getAttribute("data-title") || "";
                myTextArea.value = item.getAttribute("data-content") || "";

                editChapterSection.style.display = "block";
                addChapterBox.style.display = "none";

                popup.style.display = "none";
                activePopup = null;
            });
        }

        if (deleteBtn) {
            deleteBtn.addEventListener("click", function (e) {
                e.stopPropagation();
                if (confirm("Bạn có chắc muốn xóa chương này không?")) {
                    item.remove();
                }
            });
        }
    });


    document.addEventListener("click", function () {
        if (activePopup) {
            activePopup.style.display = "none";
            activePopup = null;
        }
    });


    // Hiện/ẩn form "Thêm Chương Mới"
    addChapterBtn.addEventListener("click", function () {
        addChapterBox.style.display = addChapterBox.style.display === "none" ? "block" : "none";
        editChapterSection.style.display = "none";
    });

    cancelAdd.addEventListener("click", function () {
        addChapterBox.style.display = "none";
    });

    // Hiện/ẩn form chỉnh sửa
    cancelEdit.addEventListener("click", function () {
        editChapterSection.style.display = "none";
    });

    document.querySelectorAll(".edit-btn").forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.stopPropagation();
            editChapterSection.style.display = "block";
            addChapterBox.style.display = "none";
        });
    });
});

