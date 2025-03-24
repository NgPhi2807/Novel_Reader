document.addEventListener("DOMContentLoaded", function () {
  // Xử lý nút chỉnh sửa
  document.querySelectorAll(".edit-btn").forEach((button) => {
      button.addEventListener("click", function () {
          let chapId = this.getAttribute("data-id");
          openPopup(chapId);
      });
  });

  // Gửi dữ liệu khi submit form chỉnh sửa
  document.getElementById("editChapterForm").addEventListener("submit", function (event) {
      event.preventDefault();
      saveChapter();
  });

  // Gửi dữ liệu khi submit form thêm chương
  document.getElementById("addChapterForm").addEventListener("submit", function (event) {
      event.preventDefault();
      addChapter();
  });

  // Xử lý nút "Thêm chương"
  document.getElementById("addChapter").addEventListener("click", function () {
      document.getElementById("addChapterSection").style.display = "block";
      document.getElementById("editChapterSection").style.display = "none";
  });
  document.querySelectorAll(".delete-btn").forEach(button => {
    button.addEventListener("click", function () {
        const chapId = this.parentElement.querySelector(".edit-btn").getAttribute("data-id");
        deleteChapter(chapId);
    });
});
  // Xử lý nút Hủy
  document.getElementById("cancelAdd").addEventListener("click", function () {
      document.getElementById("addChapterForm").reset();
      if (window.tinymce) tinymce.get("editor").setContent("");
  });

  document.getElementById("cancelEdit").addEventListener("click", function () {
      document.getElementById("editChapterForm").reset();
      if (window.tinymce) tinymce.get("editor").setContent("");
      document.getElementById("editChapterSection").style.display = "none";
  });
});

function openPopup(chapId) {
  let novelId = window.location.pathname.match(/\d+/)[0];

  fetch(`/novel/${novelId}/list_chapter/get_chapter/${chapId}/`, {
      method: "GET",
      headers: { "X-Requested-With": "XMLHttpRequest" },
  })
      .then((response) => {
          if (!response.ok) throw new Error(`Lỗi HTTP: ${response.status}`);
          return response.json();
      })
      .then((data) => {
          document.getElementById("chapterTitle").value = data.name;
          document.getElementById("chapterId").value = chapId;

          if (window.tinymce && tinymce.get("editor")) {
              tinymce.get("editor").setContent(data.content);
          } else if (window.CKEDITOR && CKEDITOR.instances["editor"]) {
              CKEDITOR.instances["editor"].setData(data.content);
          } else {
              document.getElementById("editor").value = data.content;
          }

          let saveButton = document.querySelector("#editChapterForm button[type='submit']");
          if (saveButton) {
              let updateUrl = `/novel/${novelId}/list_chapter/update/${chapId}/`;
              saveButton.setAttribute("data-url", updateUrl);
          }

          document.getElementById("editChapterSection").style.display = "block";
          document.getElementById("addChapterSection").style.display = "none";
      })
      .catch((error) => console.error("Lỗi khi lấy dữ liệu chương:", error));
}

function showAlert(message) {
    const alertBox = document.getElementById("alertBox");
    const alertMessage = document.getElementById("alertMessage");

    alertMessage.textContent = message;
    alertBox.classList.add("show");

    setTimeout(() => {
        alertBox.classList.remove("show");
    }, 2000); // Ẩn sau 2 giây
}

function saveChapter() {
    let saveButton = document.querySelector("#editChapterForm button[type='submit']");
    if (!saveButton) {
        console.error("Không tìm thấy nút submit");
        return;
    }

    let updateUrl = saveButton.getAttribute("data-url");
    let title = document.getElementById("chapterTitle").value;
    let content = "";

    if (window.tinymce && tinymce.get("editor")) {
        content = tinymce.get("editor").getContent();
    } else if (window.CKEDITOR && CKEDITOR.instances["editor"]) {
        content = CKEDITOR.instances["editor"].getData();
    } else {
        content = document.getElementById("editor").value;
    }

    let csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    fetch(updateUrl, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: title, content: content }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.status === "success") {
                showAlert("Cập nhật thành công!");
                // Reload sau khi thông báo xuất hiện
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                showAlert("Lỗi: " + (data.message || "Cập nhật thất bại"));
            }
        })
        .catch((error) => {
            console.error("Lỗi khi lưu chương:", error);
            showAlert("Lỗi khi lưu chương!");
        });
}
function addChapter() {
    let form = document.getElementById("addChapterForm");
    if (!form) {
        console.error("Không tìm thấy form #addChapterForm");
        return;
    }

    let saveButton = form.querySelector("button[type='submit']");
    if (!saveButton) {
        console.error("Không tìm thấy nút submit");
        return;
    }

    let updateUrl = saveButton.getAttribute("data-url");

    // Kiểm tra các phần tử trước khi lấy value
    let nameInput = document.getElementById("name");
    let numberInput = document.getElementById("number");
    let addEditor = document.getElementById("addEditor");

    if (!nameInput || !numberInput || !addEditor) {
        console.error("Không tìm thấy một hoặc nhiều phần tử: name, number, hoặc addEditor");
        console.log("name:", nameInput);
        console.log("number:", numberInput);
        console.log("addEditor:", addEditor);
        return;
    }

    let name = nameInput.value;
    let number = numberInput.value;
    let content = "";

    // Lấy nội dung từ editor
    if (window.tinymce && tinymce.get("addEditor")) {
        content = tinymce.get("addEditor").getContent();
    } else if (window.CKEDITOR && CKEDITOR.instances["addEditor"]) {
        content = CKEDITOR.instances["addEditor"].getData();
    } else {
        content = addEditor.value;  // Chỉ gọi .value nếu addEditor tồn tại
    }

    let csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
    if (!csrfToken) {
        console.error("Không tìm thấy CSRF token");
        return;
    }
    csrfToken = csrfToken.value;

    if (!name || !number || !content) {
        alert("Vui lòng điền đầy đủ các trường bắt buộc!");
        return;
    }

    fetch(updateUrl, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            name: name,
            number: number,
            content: content
        }),
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error("Lỗi khi gửi request: " + response.status);
        }
        return response.json();
    })
    .then((data) => {
        if (data.status === "success") {
            showAlert("Thêm chương thành công !");
            
            form.reset();
            if (window.tinymce && tinymce.get("addEditor")) {
                tinymce.get("addEditor").setContent("");
            }
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            alert("Lỗi: " + (data.message || "Thêm chương thất bại"));
        }
    })
    .catch((error) => {
        console.error("Lỗi khi thêm chương:", error);
        alert("Đã xảy ra lỗi khi thêm chương!");
    });
}
function deleteChapter(chapId) {
  const novelId = window.location.pathname.match(/\d+/)[0];  
  const deleteUrl = `/novel/${novelId}/list_chapter/delete/${chapId}/`;
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

  fetch(deleteUrl, {
      method: "POST",
      headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json",
      },
  })
  .then(response => {
      if (!response.ok) {
          throw new Error("Lỗi khi xóa chương: " + response.status);
      }
      return response.json();
  })
  .then(data => {
      if (data.status === "success") {
        showAlert("Xóa chương thành công!");
        setTimeout(() => {
            location.reload();
        }, 1000);
      } else {
          alert("Lỗi: " + (data.message || "Xóa chương thất bại"));
      }
  })
  .catch(error => {
      console.error("Lỗi khi xóa chương:", error);
      alert("Đã xảy ra lỗi khi xóa chương!");
  });
}
function deleteChapter(chapId) {
    const novelId = window.location.pathname.match(/\d+/)[0];  
    const deleteUrl = `/novel/${novelId}/list_chapter/delete/${chapId}/`;
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    fetch(deleteUrl, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Lỗi khi xóa chương: " + response.status);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === "success") {
            showAlert("Xóa chương thành công!", "success");

            setTimeout(() => {
                location.remove();
            }, 2000);  
        } else {
            showAlert("Lỗi: " + (data.message || "Xóa chương thất bại"), "error");
        }
    })
    .catch(error => {
        console.error("Lỗi khi xóa chương:", error);
        showAlert("Đã xảy ra lỗi khi xóa chương!", "error");
    });
}

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".chapter-item").forEach(item => {
      let text = item.childNodes[0].textContent.trim();
      if (text.length > 35) {
          item.childNodes[0].textContent = text.substring(0, 35) + "...";
      }
  });
});