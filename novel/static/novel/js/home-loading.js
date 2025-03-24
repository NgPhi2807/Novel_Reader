document.addEventListener("DOMContentLoaded", function () {
  const trendingSection = document.getElementById("trending-section");
  const products = document.querySelectorAll(".product__item");

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
        } else {
          // Khi cuộn ra khỏi phần này, ẩn sản phẩm để có thể chạy lại hiệu ứng khi cuộn vào
    
        }
      });
    },
    { threshold: 0.2 } // Kích hoạt khi 20% section xuất hiện trên màn hình
  );

  observer.observe(trendingSection);
});
