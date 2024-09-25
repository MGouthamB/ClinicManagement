const hamBurger = document.querySelector(".toggle-btn");

hamBurger.addEventListener("click", function () {
  document.querySelector("#sidebar").classList.toggle("expand");
  document.querySelector("#main").classList.toggle("expand");
  var logoElement = document.getElementById("logo");

    if (logoElement.innerText === "sentiment_very_satisfied") {
        logoElement.innerText = "menu_open";
    } else {
        logoElement.innerText = "sentiment_very_satisfied";
    }

});