var compF = Array(compFraw.length);
for (var i=0; i<compFraw.length; i++) {
    compF[i]= compFraw[i];
}

hedotools.shifter._compF(compF);
hedotools.shifter._lens(lens);
hedotools.shifter._words(words);
hedotools.shifter.selfShifter();
hedotools.shifter.setfigure(d3.select('#figure01')).plot();
