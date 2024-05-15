 document.addEventListener("DOMContentLoaded", (event) => {
    var selectedMarks = new Map();

    ymaps.ready(init);
    function init() {
        var myMap = new ymaps.Map("map", {
            center: [55.263577, 59.778038],
            zoom: 10,
            controls: []
        });
//        myMap.controls.removeAll()
        points.forEach(function (point) {
            var placeMark = new ymaps.Placemark([point.latitude, point.longitude], { hintContent: point.name });
            myMap.geoObjects.add(placeMark);
            placeMark.events
        .add('click', function (e) {
            // Ссылку на объект, вызвавший событие,
            // можно получить из поля 'target'.
            console.log(e.get('target'))
            e.get('target').options.set('preset', 'islands#redIcon');
        })
        });

    }

  });
