document.addEventListener("DOMContentLoaded", function () {

  const toggles = document.querySelectorAll(".toggle-password");

  toggles.forEach(function (eye) {

    eye.addEventListener("click", function () {

      const input = this.parentElement.querySelector("input");

      if (input.type === "password") {
        input.type = "text";
        this.classList.remove("fa-eye");
        this.classList.add("fa-eye-slash");
      } else {
        input.type = "password";
        this.classList.remove("fa-eye-slash");
        this.classList.add("fa-eye");
      }

    });

  });

});