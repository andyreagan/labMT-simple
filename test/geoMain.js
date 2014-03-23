function initializePlot() {
    loadCsv();
}

allStateNames = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut"
,"Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana"
,"Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska"
,"Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio"
,"Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee"
,"Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming","District of Columbia"]

function loadCsv() {
var csvLoadsRemaining = 4;
d3.text("labMTvecGeo.csv", function(text) {
    var tmp = text.split("\n");
    lens = tmp.map(parseFloat);
    if (!--csvLoadsRemaining) initializePlotPlot(lens,words);
});
d3.text("labMTwordsGeo.csv", function(text) {
    var tmp = text.split("\n");
    words = tmp;
    if (!--csvLoadsRemaining) initializePlotPlot(lens,words);
});
d3.json("static/us-states.topojson", function(data) {
    geoJson = data;
    console.log(geoJson);
    if (!--csvLoadsRemaining) initializePlotPlot(lens,words);
});
d3.text("data/wordCounts2013.csv", function(text) {
    tmp = text.split("\n");
    allData = Array(51);
    for (var i=0; i<allData.length; i++) {
	allData[i] = {name: allStateNames[i],
		      rawFreq: tmp[i].split(","),
		      freq: tmp[i].split(",")};
    }
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
    if (!--csvLoadsRemaining) initializePlotPlot(lens,words);
});
};

function initializePlotPlot(lens,words) {
    // draw the lens
    drawLensGeo(d3.select("#lens01"),lens);

    // initially apply the lens, and draw the shift
    for (var j=0; j<allData.length; j++) {
	for (var i=0; i<allData[j].rawFreq.length; i++) {
	    if (lens[i] > 4 && lens[i] < 6) {
		allData[j].freq[i] = 0;
            }
	    else {
		allData[j].freq[i] = allData[j].rawFreq[i];
	    }
	}
    }

    computeHapps();

    shiftObj = shift(allData[0].freq,allData[1].freq,lens,words);
    plotShift(d3.select("#shift01"),shiftObj.sortedMag.slice(0,200),
              shiftObj.sortedType.slice(0,200),
              shiftObj.sortedWords.slice(0,200),
              shiftObj.sumTypes,
              shiftObj.refH,
              shiftObj.compH);

    drawMap(d3.select('#map01'))

};

initializePlot();



