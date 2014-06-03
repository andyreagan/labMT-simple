function computeHapps() {
    var timeseries = Array(allDataRaw.length-(minWindows-1));
    // rolling
    var N = d3.sum(allData[0]);
    var freq = Array(allDataRaw[0].length);
    for (var i=0; i<allData[0].length; i++) {
        freq[i] = allData[0][i];
    }
    // add next 3 [1,2,3]
    for (var j=1; j<minWindows-1; j++) {
	N+=d3.sum(allData[j]);
	for (var i=0; i<allData[j].length; i++) {
            freq[i] += allData[j][i];
	}
    }
    //console.log(N);
    //console.log(allData[0]);
    // start the fourth
    var j = 4;
    var happs = 0.0;
    N+=d3.sum(allData[j])
    for (var i=0; i<allData[j].length; i++) {
	freq[i] += allData[j][i];
	happs += freq[i]*lens[i];
    }
    timeseries[0] = happs/N;
    //console.log(N);
    console.log(freq);
    console.log(d3.sum(freq));
    // rola forward
    for (var j=minWindows; j<allData.length; j++) {
	var happs = 0.0
	N+=d3.sum(allData[j])
	//console.log(N);
	//console.log(allData[0]);
	N-=d3.sum(allData[j-minWindows])
	for (var i=0; i<allData[j].length; i++) {
	    freq[i] += allData[j][i];
	    freq[i] -= allData[j-minWindows][i];
	    //console.log(freq[i]);
	    happs += freq[i]*lens[i];
	}
	//console.log(happs);
	//console.log(happs/N);
	timeseries[j-(minWindows-1)] = happs/N;
    }
    console.log("inside computeHappsChapters");
    console.log(timeseries);
    return timeseries;
}









