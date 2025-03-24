// Code chuyển slide ảnh trên trang chủ
// Sử dụng thư viện Swiper.js
// https://swiperjs.com/
    document.addEventListener("DOMContentLoaded", function () {
    var swiper = new Swiper(".mySwiper", {
        slidesPerView: 3, // Hiển thị đúng 3 slide
        spaceBetween: 0,
        centeredSlides: true,
        loop: true, // Vòng lặp vô hạn
        initialSlide: 0, // Bắt đầu từ slide đầu tiên
        effect: "coverflow",
        coverflowEffect: {
            rotate: 0,
            stretch: 0,
            depth: 150,
            modifier: 2,
            slideShadows: false,
        },
        autoplay: {
            delay: 2500, // 2.5 giây tự động chuyển slide
            disableOnInteraction: false,
            reverseDirection: false, // Chuyển slide từ trái qua phải
        },
        pagination: {
            el: ".swiper-pagination",
            clickable: true, // Cho phép click để chọn slide
        },
        on: {
            slideChangeTransitionStart: function () {
                updateVisibleSlides(swiper);
            },
        },
    });

    function updateVisibleSlides(swiper) {
        // Ẩn tất cả các slide trước khi cập nhật lại
        document.querySelectorAll(".swiper-slide").forEach((slide) => {
            slide.style.opacity = "0";
            slide.style.transition = "opacity 0.5s ease";
        });

        // Hiển thị chỉ 3 slide chính giữa
        let activeSlides = [
            swiper.slides[swiper.activeIndex - 1],
            swiper.slides[swiper.activeIndex],
            swiper.slides[swiper.activeIndex + 1]
        ];

        activeSlides.forEach((slide) => {
            if (slide) {
                slide.style.opacity = "1";
            }
        });
    }

    // Cập nhật slide hiển thị ban đầu
    updateVisibleSlides(swiper);

    // Gán sự kiện cho các nút điều hướng riêng
    document.querySelector(".custom-prev").addEventListener("click", function () {
        swiper.slidePrev();
    });

    document.querySelector(".custom-next").addEventListener("click", function () {
        swiper.slideNext();
    });
});
