function drawLensGeo(figure,lens) {
/* takes a d3 selection and draws the lens distribution
   on slide of the stop-window
     -reload data csv's
     -cut out stops words (0 the frequencies)
     -call shift on these frequency vectors */


    margin = {top: 0, right: 0, bottom: 0, left: 0},
    figwidth = 600 - margin.left - margin.right,
    figheight = 150 - margin.top - margin.bottom,
    width = .775*figwidth,
    height = .775*figheight-10;

    // remove an old figure if it exists
    figure.select(".canvas").remove();

    var canvas = figure.append("svg")
	.attr("width",figwidth)
	.attr("height",figheight)
	.attr("class","canvas");


    // create the x and y axis
    x = d3.scale.linear()
	//.domain([d3.min(lens),d3.max(lens)])
	.domain([1.00,9.00])
	.range([0,width]);
    
    // use d3.layout http://bl.ocks.org/mbostock/3048450
    data = d3.layout.histogram()
        .bins(x.ticks(65))
        (lens);

    // linear scale function
    y =  d3.scale.linear()
	.domain([0,d3.max(data,function(d) { return d.y; } )])
	.range([height, 0]); 

    // create the axes themselves
    var axes = canvas.append("g")
	.attr("transform", "translate(" + (0.125 * figwidth) + "," +
	      ((1 - 0.125 - 0.775) * figheight) + ")")
	.attr("width", width)
	.attr("height", height)
	.attr("class", "main");

    // create the axes background
    axes.append("svg:rect")
	.attr("width", width)
	.attr("height", height)
	.attr("class", "bg")
	.style({'stroke-width':'2','stroke':'rgb(0,0,0)'})
	.attr("fill", "#FCFCFC");

    // axes creation functions
    var create_xAxis = function() {
	return d3.svg.axis()
	    .scale(x)
	    .ticks(9)
	    .orient("bottom"); }

    // axis creation function
    var create_yAxis = function() {
	return d3.svg.axis()
	    .ticks(3)
	    .scale(y) //linear scale function
	    .orient("left"); }

    // draw the axes
    var yAxis = create_yAxis()
	.innerTickSize(6)
	.outerTickSize(0);

    axes.append("g")
	.attr("class", "top")
	.attr("transform", "(0,0)")
	.attr("font-size", "12.0px")
	.call(yAxis);

    var xAxis = create_xAxis()
	.innerTickSize(6)
	.outerTickSize(0);

    axes.append("g")
	.attr("class", "x axis ")
	.attr("font-size", "12.0px")
	.attr("transform", "translate(0," + (height) + ")")
	.call(xAxis);

    d3.selectAll(".tick line").style({'stroke':'black'});

    // create the clip boundary
    var clip = axes.append("svg:clipPath")
	.attr("id","clip")
	.append("svg:rect")
	.attr("x",0)
	.attr("y",80)
	.attr("width",width)
	.attr("height",height-80);

    var unclipped_axes = axes;
 
    //axes = axes.append("g")
	//.attr("clip-path","url(#clip)");

    canvas.append("text")
	.text("Num Words")
	.attr("class","axes-text")
	.attr("x",(figwidth-width)/4)
	.attr("y",figheight/2+30)
	.attr("font-size", "12.0px")
	.attr("fill", "#000000")
	.attr("transform", "rotate(-90.0," + (figwidth-width)/4 + "," + (figheight/2+30) + ")");

    canvas.append("text")
	.text("Word score")
	.attr("class","axes-text")
	.attr("x",width/2+(figwidth-width)/2)
	.attr("y",figheight)
	.attr("font-size", "12.0px")
	.attr("fill", "#000000")
	.attr("style", "text-anchor: middle;");

    var lensMean = d3.mean(lens);

    var bar = axes.selectAll(".rect")
        .data(data)
        .enter()
        .append("g")
        .attr("class","distrect")
        .attr("fill",function(d,i) { if (d.x > lensMean) {return "grey";} else { return "grey";}})
        .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

    bar.append("rect")
	.attr("x", 1)
	.attr("width", x(data[0].dx+1)-2 )
	.attr("height", function(d) { return height - y(d.y); });

    //console.log(x(d3.min(lens)));

    brushX = d3.scale.linear()
        .domain([d3.min(lens),d3.max(lens)])
        .range([figwidth*.125,width+figwidth*.125]);
    
    var brush = d3.svg.brush()
        .x(brushX)
        .extent([4,6])
        .on("brushend",brushended);

    var gBrush = canvas.append("g")
        .attr("class","brush")
        .call(brush)
        .call(brush.event);

    gBrush.selectAll("rect")
        .attr("height",height)
        .attr("y",15)
	.style({'stroke-width':'2','stroke':'rgb(100,100,100)','opacity': 0.95})
	.attr("fill", "#FCFCFC");

    function brushended() {
	if (!d3.event.sourceEvent) return;
	var extent0 = brush.extent(),
	    extent1 = extent0; // should round it to bins
	
	// window.stopVals = extent1;
	// console.log(extent1);

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
		if (lens[i] >= extent1[0] && lens[i] <= extent1[1]) {
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
	drawMap(d3.select('#map01'));
	sortStates(d3.select('#table01'));

	if (shiftRef !== shiftComp) {
	    shiftObj = shift(allData[shiftRef].freq,allData[shiftComp].freq,lens,words);
	    plotShift(d3.select('#shift01'),shiftObj.sortedMag.slice(0,200),
		      shiftObj.sortedType.slice(0,200),
		      shiftObj.sortedWords.slice(0,200),
		      shiftObj.sumTypes,
		      shiftObj.refH,
		      shiftObj.compH);
	}

	d3.select(this).transition()
	    .call(brush.extent(extent1))
	    .call(brush.event);

    }
}





