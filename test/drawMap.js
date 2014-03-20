function drawMap() {
    /* 
       plot the state map!

       drawMap(figure,geoJson,stateHapps);
         -figure is a d3 selection
         -geoJson is the loaded us-states file
         -stateHapps is the loaded csv (state,val)
    */

    //Width and height
    var w = 1000;
    var h = 600;

    //Define map projection
    var projection = d3.geo.albersUsa()
	.translate([w/2, h/2])
	.scale([1000]);

    //Define path generator
    var path = d3.geo.path()
	.projection(projection);

    //Define quantize scale to sort data values into buckets of color
    var color = d3.scale.quantize()
	.range(["rgb(237,248,233)","rgb(186,228,179)","rgb(116,196,118)","rgb(49,163,84)","rgb(0,109,44)"]);
    //Colors taken from colorbrewer.js, included in the D3 download

    //Create SVG element
    var svg = figure
	.append("svg")
	.attr("width", w)
	.attr("height", h);
    
    //Set input domain for color scale
    color.domain([
	d3.min(stateHapps, function(d) { return d.value; }), 
	d3.max(stateHapps, function(d) { return d.value; })
    ]);

    x		//Merge the ag. data and GeoJSON
    //Loop through once for each ag. data value
    for (var i = 0; i < stateHapps.length; i++) {
	
	//Grab state name
	var stateNames = stateHapps[i].state;
	
	//Grab data value, and convert from string to float
	var stateVals = parseFloat(stateHapps[i].value);
	
	//Find the corresponding state inside the GeoJSON
	for (var j = 0; j < geoJson.features.length; j++) {

	    var jsonState = geoJson.features[j].properties.name;
	    
	    if (dataState == jsonState) {
		
		//Copy the data value into the JSON
		geoJson.features[j].properties.value = stateVals;
		
		//Stop looking through the JSON
		break;
		
	    }
	}		
    }
    
    //Bind data and create one path per GeoJSON feature
    var states =	svg.selectAll("path")
	.data(geoJson.features)

    states.enter()
	.append("path")
	.attr("d", path)
	.attr("id", jsonState)

    states.exit().remove()

    states
	.style("fill", function(d) {
	    //Get data value
	    var value = d.properties.value;

	    if (value) {
		//If value exists…
		return color(value);
	    } else {
		//If value is undefined…
		return "#ccc";
	    }
	});


});

});

}



}










