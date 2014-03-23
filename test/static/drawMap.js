function drawMap(figure) {
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
	.scale(1000);

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
	d3.min(allData, function(d) { return d.avhapps; }), 
	d3.max(allData, function(d) { return d.avhapps; })
    ]);

    stateFeatures = topojson.feature(geoJson,geoJson.objects.states).features;

    //Merge the ag. data and GeoJSON
    //Loop through once for each ag. data value
    for (var i = 0; i < allData.length; i++) {
	
	//Grab state name
	var stateName = allData[i].name;
	
	//Grab data value, and convert from string to float
	var stateVal = allData[i].avhapps;
	
	//Find the corresponding state inside the GeoJSON
	for (var j = 0; j < stateFeatures.length; j++) {

	    var jsonState = stateFeatures[j].properties.name;
	    
	    if (stateName == jsonState) {
		
		//Copy the data value into the JSON
		stateFeatures[j].properties.avhapps = stateVal;
		
		//Stop looking through the JSON
		break;
	    }
	}		
    }
    
    //Bind data and create one path per GeoJSON feature
    var states = svg.selectAll("path")
	.data(stateFeatures);
    
    console.log('bound topojson to paths');
    console.log(geoJson);

    states.enter()
	.append("path")
	.attr("d", function(d,i) { return path(d.geometry); } )
	.attr("id", function(d,i) { return d.properties.name; } )
        .on("click",state_clicked);

    states.exit().remove();

    states
         .style("fill", function(d,i) {
	    // need to get the variable map right
    	    var value = allData[i].avhapps;
	    var numWords = 1000000; // d3.sum(d.properties.freq);
    	    if (numWords > 10000) {
    		return color(value);
    	    } else {
    		return "#ccc";
    	    }
    	});

    function state_clicked(d,i) { console.log(d.properties.name); console.log(i); shiftB = i; }

};









