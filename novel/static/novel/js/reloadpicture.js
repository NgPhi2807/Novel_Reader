document.addEventListener("DOMContentLoaded", function () {
  const imgInput = document.getElementById("img");
  const previewImage = document.getElementById("previewImage");

  if (imgInput && previewImage) {
      imgInput.addEventListener("change", function (event) {
          const file = event.target.files[0]; // Lấy file được chọn
          if (file) {
              const imageUrl = URL.createObjectURL(file); // Tạo URL tạm cho ảnh

              previewImage.style.backgroundImage = `url('${imageUrl}')`; // Cập nhật ảnh
              previewImage.removeAttribute("data-setbg"); // Xóa thuộc tính cũ để tránh lỗi
              
              // Dọn dẹp URL sau khi hình ảnh đã tải
              previewImage.onload = function () {
                  URL.revokeObjectURL(imageUrl);
              };
          }
      });
  }
});
