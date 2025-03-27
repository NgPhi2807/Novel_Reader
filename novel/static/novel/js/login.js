
  document.addEventListener("DOMContentLoaded", function () {
      const openLoginModal = document.getElementById("open-login-modal");
      const closeLoginModal = document.getElementById("close-login-modal");
      const loginModal = document.getElementById("login-modal");
  
      if (openLoginModal && closeLoginModal && loginModal) {
          openLoginModal.addEventListener("click", function (event) {
              event.preventDefault();
              loginModal.classList.remove("hidden");
          });
  
          closeLoginModal.addEventListener("click", function () {
              loginModal.classList.add("hidden");
          });
  
          loginModal.addEventListener("click", function (event) {
              if (event.target === loginModal) {
                  loginModal.classList.add("hidden");
              }
          });
      }
  });
  