function initializePlot() {
    loadCsv();
}

function loadCsv() {
var csvLoadsRemaining = 4;
d3.text("tuesdayFvec.csv", function(text) {
    var tmp = text.split("\n");
    refFraw = tmp;
    if (!--csvLoadsRemaining) initializePlotPlot(refFraw,compFraw,lens,words);
});
d3.text("labMTvec.csv", function(text) {
    var tmp = text.split("\n");
    lens = tmp.map(parseFloat);
    if (!--csvLoadsRemaining) initializePlotPlot(refFraw,compFraw,lens,words);
});
d3.text("labMTwords.csv", function(text) {
    var tmp = text.split("\n");
    words = tmp;
    if (!--csvLoadsRemaining) initializePlotPlot(refFraw,compFraw,lens,words);
});
d3.text("saturdayFvec.csv", function(text) {
    var tmp = text.split("\n");
    compFraw = tmp;
    if (!--csvLoadsRemaining) initializePlotPlot(refFraw,compFraw,lens,words);
});
};

function initializePlotPlot(refFraw,compFraw,lens,words) {
    // draw the lens
    drawLens(d3.select("#lens01"),lens,refFraw,compFraw);

    // initially apply the lens, and draw the shift
    var refF = Array(refFraw.length);
    var compF = Array(compFraw.length);
    for (var i=0; i<refFraw.length; i++) {
	if (lens[i] > 4 && lens[i] < 6) {
            refF[i]= 0;
            compF[i]= 0;
        }
	else {
            refF[i]= refFraw[i];
            compF[i]= compFraw[i];
	}
    }
    shiftObj = shift(refF,compF,lens,words);
    plotShift(d3.select("#figure01"),shiftObj.sortedMag.slice(0,200),
              shiftObj.sortedType.slice(0,200),
              shiftObj.sortedWords.slice(0,200),
              shiftObj.sumTypes,
              shiftObj.refH,
              shiftObj.compH);

};

initializePlot();



