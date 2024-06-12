document.addEventListener("DOMContentLoaded", (event) => {
  var selectedMarks = new Map();

  ymaps.ready(init);
  function init() {
    var myMap = new ymaps.Map("map", {
      center: [55.263577, 59.778038],
      zoom: 10,
      controls: [],
    });
    console.log(points);
    points.forEach(function (point) {
      var placeMark = new ymaps.Placemark([point.latitude, point.longitude], {
        hintContent: point.name,
      });

      // Добавляем флаг для отслеживания текущего состояния иконки
      placeMark.state.set("isRed", false);

      myMap.geoObjects.add(placeMark);

      placeMark.events.add("click", function (e) {
        var target = e.get("target");
        var isRed = target.state.get("isRed");
        console.log(isRed, point);
        if (isRed) {
          target.options.set("preset", "islands#blueIcon");
          selectedMarks.delete(point.name);
        } else {
          target.options.set("preset", "islands#redIcon");
          selectedMarks.set(point.name, point);
        }

        // Переключаем флаг
        target.state.set("isRed", !isRed);
      });
    });

    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
    document
      .getElementById("create-route-btn")
      .addEventListener("click", function (e) {
        e.preventDefault();

        // Делаем элементы неактивными и показываем спиннер
        $("button, input, select").prop("disabled", true);
        $("#spinner-overlay").css("display", "flex");

        const level = document.getElementById("level_of_hardness").value;
        const duration = document.getElementById("duration").value;
        const number_participants = document.getElementById(
          "number_participants"
        ).value;
        const season = document.getElementById("season").value;
        const accommodation = document.getElementById("accommodation").value;

        var selectedPoints = Array.from(selectedMarks.values()).map(function (
          point
        ) {
          return {
            name: point.name,
            latitude: point.latitude,
            longitude: point.longitude,
            description: point.description,
            order: point.order,
            closest_accomodation: point.closest_accomodation,
          };
        });
        const bodyData = {
          points: selectedPoints,
          level,
          duration,
          number_participants,
          season,
          accommodation,
        };
        console.log(bodyData);
        fetch("/routeq/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify(bodyData),
        })
          .then((response) => response.json())
          .then((data) => {
            console.log("Response data:", data);

            if (data.route_id) {
              window.location.href = `\http://127.0.0.1:8000/route/${data.route_id}/`;
            } else {
              console.error("route_id is missing in the response");
            }
          })
          .catch((error) => {
            console.error("Error:", error);
            $("button, input, select").prop("disabled", false);
            $("#spinner-overlay").css("display", "none");
          });
      });
  }
});
