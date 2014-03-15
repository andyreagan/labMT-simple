function shift(refF,compF,lens,words) {

    // non-normalized frequency
    //console.log(refF[10])

    // normalize frequencies
    var Nref = 0.0;
    var Ncomp = 0.0;
    for (var i=0; i<refF.length; i++) {
        Nref += parseFloat(refF[i]);
        Ncomp += parseFloat(compF[i]);
    }

    for (var i=0; i<refF.length; i++) {
        refF[i] = parseFloat(refF[i])/Nref;
        compF[i] = parseFloat(compF[i])/Ncomp;
    }
    
    // normalized frequency
    //console.log(refF[10])

    // compute reference happiness
    refH = 0.0;
    for (var i=0; i<refF.length; i++) {
        refH += refF[i]*parseFloat(lens[i]);
    }

    // compute comparison happiness
    compH = 0.0;
    for (var i=0; i<compF.length; i++) {
        compH += compF[i]*parseFloat(lens[i]);
    }

    //console.log(refH);

    // do the shifting
    shiftMag = Array(refF.length);
    shiftType = Array(refF.length);
    var freqDiff = 0.0;
    for (var i=0; i<refF.length; i++) {
	freqDiff = compF[i]-refF[i];
        shiftMag[i] = (parseFloat(lens[i])-refH)*freqDiff;
	if (freqDiff > 0) { shiftType[i] = 2; }
	else { shiftType[i] = 0}
	if (parseFloat(lens[i]) > refH) { shiftType[i] += 1;}
    }

    // do the sorting
    indices = Array(refF.length);
    for (var i = 0; i < refF.length; i++) { indices[i] = i; }
    indices.sort(function(a,b) { return Math.abs(shiftMag[a]) < Math.abs(shiftMag[b]) ? 1 : Math.abs(shiftMag[a]) > Math.abs(shiftMag[b]) ? -1 : 0; });

    sortedMag = Array(refF.length);
    sortedType = Array(refF.length);
    sortedWords = Array(refF.length);

    for (var i = 0; i < refF.length; i++) { 
	sortedMag[i] = shiftMag[indices[i]]; 
	sortedType[i] = shiftType[indices[i]]; 
	sortedWords[i] = words[indices[i]]; 
    }

    // compute the sum of contributions of different types
    sumTypes = [0.0,0.0,0.0,0.0];
    for (var i = 0; i < refF.length; i++)
    { 
        sumTypes[shiftType[i]] += shiftMag[i];
    }

    // return as an object
    return {
      sortedMag: sortedMag,
      sortedType: sortedType,
      sortedWords: sortedWords,
      sumTypes: sumTypes
    };
};
