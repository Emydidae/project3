// use these to test the different endpoints
// d3.json('http://127.0.0.1:5000/map_markers/2017').then(data => {console.log(data);});
// d3.json('http://127.0.0.1:5000/rain_bar/2017').then(data => {console.log(data);});
// d3.json('http://127.0.0.1:5000/fire_bar/2017').then(data => {console.log(data);});
// d3.json('http://127.0.0.1:5000/month_line').then(data => {console.log(data);});

// MAPS ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
    return d > 150 ? '#084594':
           d > 125 ? '#2171B5':
           d > 100 ? '#4292C6':
           d > 75 ? '#6BAED6':
           d > 50 ? '#9ECAE1':
           d > 25  ? '#C6DBEF':
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
<hr><p>Latitude: ${rain_data[i].Latitude}<br>
Longitude: ${rain_data[i].Longitude}<br>
Total Pcpn: ${rain_data[i].total_pcpn_inches} in.<br>
Total Expected (Avg) Pcpn: ${rain_data[i].total_expected_pcpn} in.<br>
% of Expected: ${rain_data[i].percent_avg_pcpn}%<br>
# Months Measured: ${rain_data[i].months_measured}<br>
<a href = '${rain_data[i].info_link}'>More Info</a></p>`;
        // create marker, add popup text to it
        let marker = L.circle([rain_data[i].Latitude, rain_data[i].Longitude], {
            color: 'black',
            // size = amount prcp
            radius: rain_data[i].total_pcpn_inches * 200,
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

// make markers for the fire map
function fire_markers(fire_data) {
    // empty list to hold markers
    let fire_markers = [];
    // loop through data and make markers
    for (let i = 0; i < fire_data.length; i++) {
        // format popup text
        let popup_text = `<p>Acres Burned: ${fire_data[i].Acres_Burned}<br>\
Latitude: ${fire_data[i].Latitude}<br>
Longitude: ${fire_data[i].Longitude}<br>
Month: ${fire_data[i].Month}<br>
Year: ${fire_data[i].Year}<br></p>`;
        // create marker, add the popup text to it
        let marker = L.circle([fire_data[i].Latitude, fire_data[i].Longitude], {
            color: 'black',
            // size = acres burned
            radius: Math.sqrt(fire_data[i].Acres_Burned) * 150,
            fillColor: '#d94801',
            fillOpacity: 0.75,
            opacity: 1,
            weight: 1
        }).bindPopup(popup_text);
        // add marker to list
        fire_markers.push(marker);
        };
        // make overlay map layer for the fire map
        let fire_overlay = L.layerGroup(fire_markers);
        return fire_overlay;
    };

// make the rain map chart
function make_maps(year) {
    // remove current maps & re-insert divs
    d3.select('#rain_map').remove();
    d3.select('#fire_map').remove();
    d3.select('#map_holder').append('div').attr('id','rain_map');
    d3.select('#map_holder').append('div').attr('id','fire_map');
    // make url & call for map marker data
    let url = `http://127.0.0.1:5000/map_markers/${year}`
    d3.json(url).then(data => {
        // RAIN MAP - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        // get background layers
        let base_maps = make_tiles();
        // get rain data
        let rain_data = data.rain_data;
        // get markers
        let rain_overlay = rain_markers(rain_data);
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
        let fire_overlay = fire_markers(fire_data);
        // format fire map
        let fire_map = L.map('fire_map', {
            center: [38, -120],
            zoom: 6,
            layers: [base_maps_2['Street'], fire_overlay] 
        });
        // add layer control
        L.control.layers(base_maps_2).addTo(fire_map);

        // Create the legend
        let legend = L.control({position: "bottomright"});
        // define grades for legend and add to HTML division
        legend.onAdd = function(rain_map) {
        let div = L.DomUtil.create("div", "legend"),
        grades = [0, 25, 50, 75, 100, 125, 150];
        for (let i = 0; i < grades.length; i++) {
            div.innerHTML +=
            '<i style="background:' + rain_color(grades[i] + 1) + '"></i> ' +
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '%<br>' : '%+');
            }
            return div;
        };
        // Add legend to rain map
        legend.addTo(rain_map);

        // Use sync plugin to synchronize maps
        rain_map.sync(fire_map);
        fire_map.sync(rain_map);
    });
};

// BARS ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
            type: 'bar',
            marker: {
              color: '#2171B5'
            }
        }];
        // give name
        let layout = {
            title: `Monthly Avg Precipitation in CA - ${year}`
        };
        // make chart
        Plotly.newPlot('rain_bar', trace1, layout);
    });
};

// make the fire bar chart
function make_fire_bars(year) {
    // make url & call for data
    let url = `http://127.0.0.1:5000/fire_bar/${year}`
    d3.json(url).then(data => {
        // make trace for y axis 1
        let trace1 = {
            x: data.map(item => {return item.month}),
            y: data.map(item => {return item.avg_acres_burned}),
            text: data.map(item => {return 'Average Acres Burned'}),
            type: 'bar',
            marker: {
              color: '#d94801'
            }
        };
        // make trace for y axis 2          
        let trace2 = {
            x: data.map(item => {return item.month}),
            y: data.map(item => {return item.num_of_fires}),
            text: data.map(item => {return 'Fires'}),
            type: 'bar',
            marker: {
              color: '#d94801'
            }
        };
        // set titles
        let layout = {
            title: `Monthly Avg Acres Burned in CA - ${year}`
        };
        let layout2 = {
            title: `Monthly # of Fires in CA - ${year}`
        };
        // make plots
        Plotly.newPlot('fire_bar1', [trace1], layout);
        Plotly.newPlot('fire_bar2', [trace2], layout2);
    });
};

// LINE ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

function make_line() {
    // make url and call for data
    // can uncomment the console log at the top to print this data to console for you to reference
    let url = 'http://127.0.0.1:5000/month_line'
    d3.json(url).then(data => {
        // make trace for each of the 3 arrays for the line graph
        // use the map function to get month data for x and the specific data point for y
        // since some will have gaps in the data, make sure to set connectgaps to false (see https://plotly.com/javascript/line-charts/#connect-gaps-between-data)
        let prcp = data.avg_rain
        let trace1 = {
            x: prcp.map(item => {return item.month}),
            y: prcp.map(item => {return item.avg_rainfall}),
            text: prcp.map(item => {return `Inches`}),
            name: 'Avg. Precipitation',
            mode: 'lines',
            marker: {
                color: '#2171B5'
            }
        };
        let fire_acres = data.avg_fire
        let trace2 = {
            x: fire_acres.map(item => {return item.month}),
            y: fire_acres.map(item => {return item.avg_acres_burned}),
            text: fire_acres.map(item => {return 'Average Acres Burned'}),
            name: 'Avg. Acres Burned',
            mode: 'lines',
            yaxis: 'y2',
            marker: {
                color: '#d91a01'
            }
        };
        let fire_counts = data.fire_counts
        let trace3 = {
            x: fire_counts.map(item => {return item.month}),
            y: fire_counts.map(item => {return item.num_of_fires}),
            text: fire_counts.map(item => {return 'Fires'}),
            name: '# of Fires',
            mode: 'lines',
            yaxis: 'y3',
            marker: {
                color: '#d98301'
            }
        };
        let traces = [trace1, trace2, trace3];

        // make a single layout variable with info for each y axis (https://plotly.com/javascript/multiple-axes/)
        // you don't need all the info from that for each axis, but you should make sure to give a title and say which side the axis should appear on (rain info on left, fire stuff on the right)
        let layout = {
            title: 'Monthly Precipitation and Wildfire Trends (2013-2019)',
            xaxis: {
                tickvals: ['Jan 2013', 'May 2013', 'Sep 2013',
                           'Jan 2014', 'May 2014', 'Sep 2014',
                           'Jan 2015', 'May 2015', 'Sep 2015',
                           'Jan 2016', 'May 2016', 'Sep 2016',
                           'Jan 2017', 'May 2017', 'Sep 2017',
                           'Jan 2018', 'May 2018', 'Sep 2018',
                           'Jan 2019', 'May 2019', 'Sep 2019'],
                ticktext: ["Jan '13", "May '13", "Sep '13",
                           "Jan '14", "May '14", "Sep '14",
                           "Jan '15", "May '15", "Sep '15",
                           "Jan '16", "May '16", "Sep '16",
                           "Jan '17", "May '17", "Sep '17",
                           "Jan '18", "May '18", "Sep '18",
                           "Jan '19", "May '19", "Sep '19"],
                tickangle: 300,
                domain: [0.0, 0.95]
            },
            yaxis: {
                title: 'Avg. Precipitation',
                titlefont: {color: '#2171B5'},
                tickfont: {color: '#2171B5'},
            },
            yaxis2: {
                title: 'Avg. Acres Burned',
                titlefont: {color: '#d91a01'},
                tickfont: {color: '#d91a01'},
                anchor: 'x',
                overlaying: 'y',
                side: 'right'
            },
            yaxis3: {
                title: '# of Fires',
                titlefont: {color: '#d98301'},
                tickfont: {color: '#d98301'},
                anchor: 'free',
                overlaying: 'y',
                side: 'right',
                position: 1
            }
        };
       
        // make graph
        Plotly.newPlot('line', traces, layout)
    });
};

// DROPDOWN FUNCTIONALITY ----------------------------------------------------------------------------------------------------------------------------------------------------

// update the visuals when a different year is selected
function update_vis() {
    let year = Number(d3.select('select').property('value'));
    d3.select('#rain_title').text(`${year} Rainy Season Data (November - June)`);
    d3.select('#fire_title').text(`${year} Fire Season Data (June - November)`);
    make_maps(year);
    make_rain_bar(year);
    make_fire_bars(year);
};

// get select menu
let select_menu = d3.select('#sel_year');

// read in samples.json to the dropdown
d3.json('http://127.0.0.1:5000/years').then(data => {
    for (let i = 0; i < data.length; i++) {
        select_menu.append('option').attr('value', data[i]).text(data[i]);
    };
    // call function to initialize the visuals
    update_vis();
});

// initialize line
make_line();

// Call update_vis() when a change takes place
d3.select("#sel_year").on("change", update_vis);

