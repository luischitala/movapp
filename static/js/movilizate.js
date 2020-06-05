        // Creación de mapa
        const tilesProvider = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        let myMap = L.map('myMap').setView([20.677041,-103.347745], 10)
        L.tileLayer(tilesProvider, {maxZoom: 18,}).addTo(myMap)
        // Personalización íconos
        let hospitalMarker = L.ExtraMarkers.icon({
            icon: 'fa-hospital',
            markerColor: 'red',
            shape: 'square',
            prefix: 'fa'
        })

         //Monito individual
        let dudeMarker = L.ExtraMarkers.icon({
            icon: 'fa-male',
            markerColor: 'blue',
            shape: 'circle',
            prefix: 'fa'
        })
                


        function center(latitude,longitude){
            pos = [latitude,longitude]
            
            myMap.flyTo(pos, 12);
            L.marker(pos).addTo(myMap).setIcon(dudeMarker);         
            }

        function hospitalmarker(mlatitude,mlongitude){

            pos = [mlatitude,mlongitude]

            L.marker(pos).addTo(myMap).setIcon(hospitalMarker);  
        }

        //    let geojsonlayer = L.geoJson(hospitales, {
        //     onEachFeature: function(feature, layer){
        //     layer.bindPopup(feature.properties['NOMBRE_DE_LA_UNIDAD'])
        //     layer.setIcon(hospitalMarker)
        //         }
        //      }).addTo(myMap)
        //     myMap.fitBounds(geojsonlayer.getBounds())
        //     L.geoJson(hospitales,{
        //      onEachFeature: basementDweller

        //     }).addTo(myMap);
        