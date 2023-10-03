// use these to test the different endpoints
// d3.json('http://127.0.0.1:5000/map_markers/2017').then(data => {console.log(data);});
// d3.json('http://127.0.0.1:5000/rain_bar/2017').then(data => {console.log(data);});
// d3.json('http://127.0.0.1:5000/fire_bar/2017').then(data => {console.log(data);});
// d3.json('http://127.0.0.1:5000/month_line').then(data => {console.log(data);});

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

function rain_color(d) {
    return d > 200 ? '#084594':
           d > 180 ? '#2171B5':
           d > 150 ? '#4292C6':
           d > 125 ? '#6BAED6':
           d > 100 ? '#9ECAE1':
           d > 75  ? '#C6DBEF':
           d > 0   ? '#EFF3FF':
                     '#000000';
}

// make the markers for the rain map
function rain_markers(rain_data) {
    // empty list to hold markers
    let rain_markers = [];
    // loop through data and make markers
    for (let i = 0; i < rain_data.length; i++) {
        // format popup text
        let popup_text = `<h3>${rain_data[i].Station_ID} - ${rain_data[i].Station_Name}</h3>\
<hr><p>Latitude - ${rain_data[i].Latitude}<br>
Longitude - ${rain_data[i].Longitude}<br>
Total Pcpn (in) - ${rain_data[i].total_pcpn_inches}<br>
Total Expected Pcpn - ${rain_data[i].total_expected_pcpn}<br>
% of Expected - ${rain_data[i].percent_avg_pcpn}<br>
# Months Measured - ${rain_data[i].months_measured}<br>
<a href = '${rain_data[i].info_link}'>More Info</a></p>`;
        // create marker, add popup text to it
        let marker = L.circle([rain_data[i].Latitude, rain_data[i].Longitude], {
            color: 'black',
            // size = amount prcp
            radius: rain_data[i].total_pcpn_inches * 100,
            // color = % avg
            fillColor: rain_color(rain_data[i].percent_avg_pcpn),
            fillOpacity: .75,
            opacity: 1,
            weight: 1
        }).bindPopup(popup_text);
        // add marker to list
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
        // RAIN MAP - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        // get background layers
        let base_maps = make_tiles();
        // get rain data
        let rain_data = data.rain_data;
        // get markers
        let rain_overlay = rain_markers(rain_data)
        // format map
        let rain_map = L.map('rain_map', {
            center: [38, -120],
            zoom: 6,
            layers: [base_maps['Street'], rain_overlay]
        });
        // Create a layer control, add to the rain map.
        L.control.layers(base_maps).addTo(rain_map);

        // FIRE MAP - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        // get background layers for fire map
        let base_maps_2 = make_tiles();
        // get fire data
        let fire_data = data.fire_data;
        // get markers
        let fire_overlay = rain_markers(rain_data) // USING RAIN DATA RIGHT NOW FOR TESTING, NEED TO CODE A FUNCTION TO GET THE FIRE MARKERS - MARKER SIZE SHOULD INCREASE RELATIVE TO ACRES BURNED
        // format fire map
        let fire_map = L.map('fire_map', {
            center: [38, -120],
            zoom: 6,
            layers: [base_maps_2['Street'], fire_overlay]         // change this when we get the fire marker overlay made
        });
        // add layer control
        L.control.layers(base_maps_2).addTo(fire_map);

        // Use sync plugin to synchronize maps
        rain_map.sync(fire_map);
        fire_map.sync(rain_map);
    });
};

// make the rain bar chart
function make_rain_bar(year) {
    // make url & call for data
    let url = `http://127.0.0.1:5000/rain_bar/${year}`
    d3.json(url).then(data => {
        // make trace
        let trace1 = [{
            x: data.map(item => {return item.month}),
            y: data.map(item => {return item.avg_rainfall}),
            text: data.map(item => {return `Inches`}),
            type: 'bar'
        }];
        // give name
        let layout = {
            title: `Monthly Average Precipitation in California - ${year}`
        };
        // make chart
        Plotly.newPlot('rain_bar', trace1, layout);
    });
};

// make the fire bar chart
function make_fire_bar(year) {
    // make url & call for data

        // make trace with x being the month and 2 different y axes - avg acres burned and number of fires
                // https://plotly.com/javascript/bar-charts/
                // https://plotly.com/javascript/multiple-axes/ - some resources on how to do multiple bars

        // give name

        // make chart with ID 'fire_bar'

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
make_rain_bar(2017);
make_fire_bar(2017);