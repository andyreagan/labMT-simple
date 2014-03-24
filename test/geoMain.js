function initializePlot() {
    loadCsv();
}

allStateNames = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut"
,"Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana"
,"Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska"
,"Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio"
,"Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee"
,"Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming","DC","the entire U.S."]

ignoreWords = ["severe","flood","warning","earthquake","nigga","niggas","niggaz"];

function loadCsv() {
var csvLoadsRemaining = 4;
d3.text("data/wordScores.csv", function(text) {
    var tmp = text.split(",");
    lens = tmp.map(parseFloat);
    if (!--csvLoadsRemaining) initializePlotPlot(lens,words);
});
d3.text("data/words.csv", function(text) {
    var tmp = text.split(",");
    words = tmp;
    if (!--csvLoadsRemaining) initializePlotPlot(lens,words);
});
d3.json("static/us-states.topojson", function(data) {
    geoJson = data;
    stateFeatures = topojson.feature(geoJson,geoJson.objects.states).features;
    if (!--csvLoadsRemaining) initializePlotPlot(lens,words);
});
d3.text("data/wordCounts2013.csv", function(text) {
    tmp = text.split("\n");
    allData = Array(52);
    for (var i=0; i<51; i++) {
	allData[i] = {name: allStateNames[i],
		      rawFreq: tmp[i].split(",").map(parseFloat),
		      freq: tmp[i].split(",")};
    }
    // initialize the all data
    allData[51] = {name: allStateNames[51],
		   rawFreq: Array(allData[0].freq.length),
		   freq: Array(allData[0].freq.length),};
    for (var j=0; j<allData[0].freq.length; j++) {
	allData[51].rawFreq[j] = 0.0;
    }
    for (var i=0; i<51; i++) {
	for (var j=0; j<allData[0].freq.length; j++) {
	    allData[51].rawFreq[j] += parseFloat(allData[i].rawFreq[j]);
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
    // refill the avhapps value in the main data

    // reset
    for (var j=0; j<allData.length; j++) {
	for (var i=0; i<allData[j].rawFreq.length; i++) {
	    var include = true;
	    // check if in removed word list
	    for (var k=0; k<ignoreWords.length; k++) {
		if (ignoreWords[k] == words[i]) {
		    include = false;
		    //console.log("ignored "+ignoreWords[k]);
		}
	    }
	    // check if underneath lens cover
	    if (lens[i] >= 4 && lens[i] <= 6) {
		include = false;
	    }
	    // include it, or set to 0
	    if (include) {
		allData[j].freq[i] = allData[j].rawFreq[i];
	    }
	    else { allData[j].freq[i] = 0; }
	    
	}
    }

    computeHapps();

    // draw the map
    drawMap(d3.select('#map01'))

    shiftRef = 51;
    shiftComp = 51;
    
    // compute the shift initially
    // shiftObj = shift(allData[shiftRef].freq,allData[shiftComp].freq,lens,words);
    // plotShift(d3.select("#shift01"),shiftObj.sortedMag.slice(0,200),
    //           shiftObj.sortedType.slice(0,200),
    //           shiftObj.sortedWords.slice(0,200),
    //           shiftObj.sumTypes,
    //           shiftObj.refH,
    //           shiftObj.compH);
};

initializePlot();



