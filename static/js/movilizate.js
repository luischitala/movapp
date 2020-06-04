//Elección del gráfico
const tilesProvider = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'



//Generación de mapa
let myMap = L.map('myMap').setView([20.677041,-103.347745], 10)

L.tileLayer(tilesProvider, {maxZoom: 18,}).addTo(myMap)

// //Obtención de Geolocalización
// // function obtenerloc(){
// //     if (navigator.geolocation) {
// //         navigator.geolocation.getCurrentPosition(function(position) {
// //           var pos = {
// //             lat: position.coords.latitude,
// //             lng: position.coords.longitude
// //           };
// //           console.log(pos)
// // }}


// // Try HTML5 geolocation.

// // let pos; 
// // let pos1;
// // function initMap(){
// //     navigator.geolocation.getCurrentPosition(function(position) {
// //         var pos = {
// //         lat: position.coords.latitude,
// //         lng: position.coords.longitude
// //         };
// //         console.log(pos)
    
        
// //     })  
// // }


//By using javasript json parser

function centrar(){
pos = [20.475683,-103.446807]

myMap.flyTo(pos, 15);


}

function centrarm(){
    pos = [20.677041, -103.347745]
    
    myMap.flyTo(pos, 15);
    
    
    }




// // {Lat: 20.692992, Lng:-103.3273344}
// //     lat:20.692992
// //     lng:-103.3273344




// // function basementDweller (feature, layer){
// //     layer.bindPopup(feature.properties['NOMBRE DE LA UNIDAD'])
// //     layer.setIcon(treeMarker)
    
// // };

//Ícono Hospital
let hospitalMarker = L.ExtraMarkers.icon({
    icon: 'fa-hospital',
    markerColor: 'red',
    shape: 'square',
    prefix: 'fa'
})

var respuesta = false;

if (respuesta == true){

    let geojsonlayer = L.geoJson(output, {
        onEachFeature: function(feature, layer){
            layer.bindPopup(feature.properties['name'])
            layer.setIcon(hospitalMarker)
        }
    }).addTo(myMap)
    
} else{
   centrar()

}


document.getElementById('rmodelo').onclick = function () {
    centrarm();
    }
    

// //colocar en el límite
// // myMap.fitBounds(geojsonlayer.getBounds())


// // L.geoJson(output,{

// //     onEachFeature: basementDweller

// // }).addTo(myMap);


// function movSelector(){
//     document.getElementById("select-location").addEventListener('change', function(e){
//         //Obtención de coordendas
//         console.log(e.target.value.split(","));
//         //Almacenamiento en variable
//         let coords = e.target.value.split(",");
//         //Función de colocación en el mapa
//     myMap.flyTo(coords, 14);
// })}

// movSelector();

// //Popups

// L.marker([50.5, 30.5]).addTo(myMap).bindPopup('Hi!');

// //Monito individual
// let dudeMarker = L.ExtraMarkers.icon({
//     icon: 'fa-male',
//     markerColor: 'blue',
//     shape: 'circle',
//     prefix: 'fa'
// })

// L.marker([20.475683,-103.446807]).addTo(myMap).setIcon(dudeMarker);

// centrar();

// // Routing
// // L.Routing.control({
// //     waypoints: [
// //       L.latLng(57.74, 11.94),
// //       L.latLng(57.6792, 11.949)
// //     ]
// //   }).addTo(myMap);


// const coordObt = document.getElementById("coordObt");
// coordObt.addEventListener("submit", (e) => {
//     e.preventDefault();

//     const request = new XMLHttpRequest();

//    request.open("post", "");
//    request.onload = function(){
//        console.log(request.resnponseText);
//    }
//    request.send(new FormData(coordObt));
// })

// $(document).on('submit', '#coordObt', function(e){
//     e.preventDefault();

//     $.ajax({
//         type:'POST',
//         url:'/test/',
//         data:{
//             latitude:$('#lating').val(),
//             longitude:$('#lnging').val(),
//             // csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
//         },
//         sucess: function(){
//             alert("New user creaded!");
//         }
//     });
// });


//   function obtcoord() {
//     var lating = document.getElementById("lating").value;
//     var lnging = document.getElementById("lnging").value;
//     document.getElementById("obtcoord").submit();
    
//     enrutamiento(lating,lnging);
// }




// function enrutamiento(lating, lnging){
//     // Routing advanced
//     L.Routing.control({
//     router: L.routing.mapbox('pk.eyJ1IjoiaXRhc3RldGFjbyIsImEiOiJjazlyemdhMWQwMGw4M2VsaWk1YWNoZjE5In0.pOkmZhEiIga2RtfV0rpvqA'),
//     waypoints: [
//         L.latLng(lating,lnging),
//         L.latLng(20.47565291,-103.451974)
//     ],
//     routeWhileDragging: true,
//     geocoder: L.Control.Geocoder.nominatim()
//     })
//     .on('routesfound', function(e) {
//     var routes = e.routes;
//     alert('Found ' + routes.length + ' route(s).');
//     })
// .addTo(myMap);

// }

