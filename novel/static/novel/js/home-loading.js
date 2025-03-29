document.addEventListener("DOMContentLoaded", function () {
  const trendingSection = document.getElementById("trending-section");
  const products = document.querySelectorAll(".product__item");

  if (!trendingSection || products.length === 0) {
      return; // Dừng script nếu không tìm thấy phần tử
  }

  const observer = new IntersectionObserver(
      (entries) => {
          entries.forEach((entry) => {
              if (entry.isIntersecting) {
                  // Hiển thị từng sản phẩm một với hiệu ứng mượt
                  products.forEach((product, index) => {
                      setTimeout(() => {
                          product.classList.add("show");
                      }, index * 150);
                  });
              }
          });
      },
      { threshold: 0.2 } // Kích hoạt khi 20% section xuất hiện trên màn hình
  );

  observer.observe(trendingSection);
});
