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

// older shifters

// shiftObj = shift(refF,compF,lens,words);
// plotShift(d3.select("#figure01"),shiftObj.sortedMag.slice(0,200),
//           shiftObj.sortedType.slice(0,200),
//           shiftObj.sortedWords.slice(0,200),
//           shiftObj.sumTypes,
//           shiftObj.refH,
//           shiftObj.compH);

// now with hedotools

hedotools.shifter.shift(refF,compF,lens,words);
hedotools.shifter.setfigure(d3.select('#figure01')).plot();
