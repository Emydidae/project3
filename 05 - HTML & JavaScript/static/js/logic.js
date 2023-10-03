d3.json('http://127.0.0.1:5000/map_markers/2017').then(data => {console.log(data);});

// background layer of maps
function make_tiles() {
    // get tile layers
    let street = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'});
    let sat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'});
    let topo = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
        maxZoom: 17,
        attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
    });
    // make a map background object
    let base_maps = {
        'Street': street,
        'Satellite': sat,
        'Topographical': topo
    };
    return base_maps;
};

// make the markers for the rain map
function rain_markers(rain_data) {
    let rain_markers = [];
    for (let i = 0; i < rain_data.length; i++) {
        let popup_text = `<h3>${rain_data[i].Station_ID} - ${rain_data[i].Station_Name}</h3>\
<hr><p>Latitude - ${rain_data[i].Latitude}<br>
Longitude - ${rain_data[i].Longitude}<br>
Total Pcpn (in) - ${rain_data[i].total_pcpn_inches}<br>
Total Expected Pcpn - ${rain_data[i].total_expected_pcpn}<br>
% of Expected - ${rain_data[i].percent_avg_pcpn}<br>
# Months Measured - ${rain_data[i].months_measured}<br>
<a href = '${rain_data[i].info_link}'>More Info</a></p>`;
        let marker = L.circle([rain_data[i].Latitude, rain_data[i].Longitude], {
            color: 'black',
            // size = amount prcp
            radius: rain_data[i].total_pcpn_inches * 100,
            // color = % avg
            fillColor: 'blue',
            fillOpacity: .5,
            opacity: 1,
            weight: 1
        }).bindPopup(popup_text);
        rain_markers.push(marker);
    };
    // make overlay map layer for the rain map
    let rain_overlay = L.layerGroup(rain_markers);
    return rain_overlay;
};

// make the rain map chart
function make_maps(year) {
    // make url & call for map marker data
    let url = `http://127.0.0.1:5000/map_markers/${year}`
    d3.json(url).then(data => {
        // get background layers
        let base_maps = make_tiles();
        // make markers
        // get rain data & markers
        let rain_data = data.rain_data;
        let rain_overlay = rain_markers(rain_data)
        let rain_map = L.map('rain_map', {
            center: [38, -120],
            zoom: 6,
            layers: [base_maps['Street'], rain_overlay]
        });
        // Create a layer control, add to the rain map.
        L.control.layers(base_maps).addTo(rain_map);
    });
};


// make the rain bar chart
function make_rain_bar(year) {

};

// make the fire bar chart
function make_fire_bar(year) {

};

function make_line() {

};

// update the visuals when a different year is selected
function init_page(year) {
    make_maps(year);
    make_rain_bar(year);
    make_fire_bar(year);
};

// call function to make the visuals
//init_page(2017); // delete this when dropdown is implemented !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
//make_line();
make_maps(2017);