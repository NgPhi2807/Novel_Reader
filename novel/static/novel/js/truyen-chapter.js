// Đặt kích thước chữ mặc định (đơn vị: px) và font mặc định
let currentFontSize = 22;
let defaultFont = "Palatino Linotype"; // Font mặc định

// Hàm cập nhật kích thước chữ và font chữ mặc định
function updateFontSize() {
    const content = document.querySelector('.novel-content');
    if (content) {
        content.style.fontSize = `${currentFontSize}px`;
        content.style.fontFamily = defaultFont; // Đặt font mặc định

        // Cập nhật tất cả phần tử con bên trong (p, span, div, li, ...)
        content.querySelectorAll('*').forEach(el => {
            el.style.fontSize = `${currentFontSize}px`;
            el.style.fontFamily = defaultFont;
        });
    }
}

// Hàm tăng kích thước chữ
function increaseFontSize() {
    currentFontSize += 2;
    updateFontSize();
}

// Hàm giảm kích thước chữ
function decreaseFontSize() {
    if (currentFontSize > 12) { // Giới hạn kích thước tối thiểu là 12px
        currentFontSize -= 2;
        updateFontSize();
    }
}

// Hàm thay đổi font chữ
function changeFont(fontName) {
    const content = document.querySelector('.novel-content');
    if (content) {
        content.style.fontFamily = fontName;

        // Cập nhật font cho tất cả phần tử con bên trong
        content.querySelectorAll('*').forEach(el => {
            el.style.fontFamily = fontName;
        });
    }
}

// Gán sự kiện sau khi trang tải xong
document.addEventListener('DOMContentLoaded', function () {
    updateFontSize();

    document.getElementById('increaseFont').addEventListener('click', increaseFontSize);
    document.getElementById('decreaseFont').addEventListener('click', decreaseFontSize);
    document.getElementById('changeFont').addEventListener('change', function () {
        changeFont(this.value);
    });
});
