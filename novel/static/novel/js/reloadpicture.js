document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('img').addEventListener('change', function (event) {
      const file = event.target.files[0]; // Lấy file được chọn
      if (file) {
        const imageUrl = URL.createObjectURL(file); // Tạo URL cho ảnh
        const previewImage = document.getElementById('previewImage');

        previewImage.style.backgroundImage = `url('${imageUrl}')`; // Cập nhật ảnh
        previewImage.removeAttribute("data-setbg"); // Xóa thuộc tính cũ để tránh lỗi

        console.log("Ảnh đã cập nhật:", imageUrl); // Debug để kiểm tra
      }
    });
  });