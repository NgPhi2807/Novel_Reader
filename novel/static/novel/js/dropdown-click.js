document.addEventListener("DOMContentLoaded", function () {
  const userButton = document.querySelector(".user-button");
  const userDropdown = document.querySelector(".user-dropdown");

  // Khi click vào biểu tượng người dùng, toggle hiển thị dropdown
  userButton.addEventListener("click", function(event) {
      event.stopPropagation();  // Ngừng lan truyền sự kiện để không ẩn dropdown ngay lập tức
      userDropdown.classList.toggle("show");  // Toggle dropdown khi click vào biểu tượng
  });

  // Đảm bảo khi click ra ngoài (không phải vào biểu tượng người dùng và dropdown), dropdown sẽ ẩn
  document.addEventListener("click", function(event) {
      if (!userButton.contains(event.target) && !userDropdown.contains(event.target)) {
          userDropdown.classList.remove("show");  // Ẩn dropdown khi click ra ngoài
      }
  });
});
