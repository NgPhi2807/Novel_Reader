
  document.addEventListener("DOMContentLoaded", function () {
    let userBtn = document.querySelector(".user-button");
    let dropdown = document.querySelector(".user-dropdown");

    userBtn.addEventListener("click", function (event) {
      event.preventDefault();
      dropdown.classList.toggle("show");
    });

    // Ẩn dropdown khi click ra ngoài
    document.addEventListener("click", function (event) {
      if (!userBtn.contains(event.target) && !dropdown.contains(event.target)) {
        dropdown.classList.remove("show");
      }
    });
  });

