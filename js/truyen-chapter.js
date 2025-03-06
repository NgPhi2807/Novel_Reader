
      let currentChapter = 1;
      let currentFontSize = 20; // Mặc định 20px
      let currentFont = "Palatino Linotype"; // Font mặc định

      const chapters = {
        1: {
          title: "Chương 1: 800 năm sau",
          content: [
            '"Trì Dao, ta đối với ngươi như tình cảm chân thành, ngươi vì sao muốn giết ta?"',
            'Trương Nhược Trần hét lớn một tiếng, nghĩ trước bổ nhào về phía trước, ép tới mà vàng chế tạo giường "Kẽo kẹt" một tiếng, đột nhiên ngồi dậy.',
            "Phát hiện chỉ là một giấc mộng, Trương Nhược Trần mới thở ra một hơi thật dài, dùng ống tay áo đem mồ hôi trên trán lau khô.",
            "Không!",
            "Đây không phải là một giấc mộng!",
            "Hắn cùng Trì Dao công chúa phát sinh hết thảy, lại thế nào có thể là một giấc mộng?",
            'Trương Nhược Trần vốn là Côn Lôn Giới chín đại Đế Quân một trong "Minh Đế" con trai độc nhất, năm gần 16 tuổi, lợi dụng nghịch thiên thể chất, tu luyện tới Thiên Cực Cảnh đại viên mãn.',
          ],
        },
        2: {
          title: "Chương 2: Hồi sinh từ tro tàn",
          content: [
            "Trong một ngôi miếu đổ nát, ánh sáng le lói từ ngọn nến mờ.",
            "Cả thiên hạ đã lãng quên hắn, nhưng hắn không bao giờ quên nỗi nhục ngày đó...",
          ],
        },
        3: {
          title: "Chương 3: Hành trình mới",
          content: [
            "Hắn bước đi trong gió lạnh, cảm nhận được sức mạnh mới đang dâng trào trong huyết quản.",
            "Cuộc báo thù chỉ mới bắt đầu...",
          ],
        },
      };

      function prevChapter() {
        if (currentChapter > 1) {
          currentChapter--;
          updateChapter();
        }
      }

      function nextChapter() {
        if (currentChapter < Object.keys(chapters).length) {
          currentChapter++;
          updateChapter();
        }
      }

      function updateChapter() {
        document.getElementById("chapter-title").innerText =
          chapters[currentChapter].title;

        let chapterContent = document.getElementById("chapter-content");

        // Xóa nội dung cũ
        chapterContent.innerHTML = "";

        // Thêm nội dung mới và giữ nguyên font & cỡ chữ
        chapters[currentChapter].content.forEach((paragraph) => {
          let p = document.createElement("p");
          p.style.fontSize = currentFontSize + "px";
          p.style.fontFamily = currentFont;
          p.innerText = paragraph;
          chapterContent.appendChild(p);
        });
      }

      function increaseFontSize() {
        currentFontSize += 2;
        document.querySelectorAll("#chapter-content p").forEach((p) => {
          p.style.fontSize = currentFontSize + "px";
        });
      }

      function decreaseFontSize() {
        currentFontSize -= 2;
        document.querySelectorAll("#chapter-content p").forEach((p) => {
          p.style.fontSize = currentFontSize + "px";
        });
      }

      function changeFont(fontName) {
        currentFont = fontName;
        document.querySelectorAll("#chapter-content p").forEach((p) => {
          p.style.fontFamily = currentFont;
        });
      }

      updateChapter();
