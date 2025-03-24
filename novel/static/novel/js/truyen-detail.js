document.addEventListener("DOMContentLoaded", function () {
  const tabs = document.querySelectorAll(".tab");
  const underline = document.querySelector(".underline");
  const contentSections = document.querySelectorAll(".content-section");

  function updateActiveTab(selectedTab) {
    tabs.forEach((tab) => {
      if (tab === selectedTab) {
        tab.classList.add("active");
        tab.classList.remove("inactive");
      } else {
        tab.classList.remove("active");
        tab.classList.add("inactive");
      }
    });

    // Di chuyển underline theo tab được chọn
    const rect = selectedTab.getBoundingClientRect();
    underline.style.width = rect.width + "px";
    underline.style.left = selectedTab.offsetLeft + "px";

    // Hiển thị nội dung tương ứng với tab được chọn
    const selectedTabContent = document.getElementById(selectedTab.getAttribute("data-tab"));
    contentSections.forEach((section) => {
      section.classList.remove("active");
    });

    selectedTabContent.classList.add("active");
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", function (e) {
      e.preventDefault();
      updateActiveTab(this);
    });
  });

  // Khởi tạo vị trí mặc định của underline và nội dung
  updateActiveTab(document.querySelector(".tab.active"));

  // Rút gọn tiêu đề truyện nếu dài hơn 30 ký tự
  document.querySelectorAll(".category-list ul li a").forEach(function (item) {
    if (item.textContent.length > 30) {
      item.textContent = item.textContent.substring(0, 25) + "...";
    }
  });
});
