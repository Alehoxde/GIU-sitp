var map = L.map('map').setView([4.65, -74.10], 12);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
attribution: 'OpenStreetMap'
}).addTo(map);


fetch("http://127.0.0.1:8000/paraderos")
.then(response => response.json())
.then(data => {

L.geoJSON(data,{
onEachFeature: function(feature, layer){

layer.bindPopup(
"Paradero: " + feature.properties.nombre +
"<br>Localidad: " + feature.properties.localidad
);

}
}).addTo(map);

});