function selectChapterTop(figure,numSections) {
/* takes a d3 selection and draws the lens distribution
   on slide of the stop-window
     -reload data csv's
     -cut out stops words (0 the frequencies)
     -call shift on these frequency vectors */


    margin = {top: 0, right: 0, bottom: 0, left: 0},
    figwidth = 600 - margin.left - margin.right,
    figheight = 38 - margin.top - margin.bottom,
    width = .775*figwidth,
    height = figheight;

    // remove an old figure if it exists
    figure.select(".canvas").remove();

    var canvas = figure.append("svg")
	.attr("width",figwidth)
	.attr("height",figheight)
	.attr("class","canvas");


    // create the x and y axis
    x = d3.scale.linear()
	//.domain([d3.min(lens),d3.max(lens)])
	.domain([0,100])
	.range([0,width]);
    
    // linear scale function
    y =  d3.scale.linear()
	.domain([0,1])
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

    // create the clip boundary
    var clip = axes.append("svg:clipPath")
	.attr("id","clip")
	.append("svg:rect")
	.attr("x",0)
	.attr("y",38)
	.attr("width",width)
	.attr("height",height-30);

    var unclipped_axes = axes;

    canvas.append("text")
	.text("Comparison")
	.attr("class","complabel")
	.attr("x",.82*figwidth)
	.attr("y",figheight-figheight/3)
	.attr("font-size", "12.0px")
	.attr("fill", "#000000")
	.attr("style", "text-anchor: middle;");
 
    brushX = d3.scale.linear()
        .domain([0,allDataRaw.length])
        .range([figwidth*.125,width+figwidth*.125]);
    
    var brush = d3.svg.brush()
        .x(brushX)
        .extent([Math.round(allDataRaw.length*.80),allDataRaw.length])
        .on("brush",brushing)
        .on("brushend",brushended);

    var gBrush = canvas.append("g")
        .attr("class","brush")
        .call(brush)
        .call(brush.event);

    gBrush.selectAll("rect")
        .attr("height",height-4)
        .attr("y",4)
	.style({'stroke-width':'2','stroke':'rgb(100,100,100)','opacity': 0.35})
	.attr("fill", "rgb(90,90,90)");

    function brushing() {
	if (!d3.event.sourceEvent) return;
	var extent0 = brush.extent(),
	    extent1 = extent0.map(Math.round); // should round it to bins
	
	d3.selectAll("text.complabel").attr("x",brushX(d3.sum(extent1)/extent1.length));
    };

    function brushended() {
	if (!d3.event.sourceEvent) return;
	var extent0 = brush.extent(),
	    extent1 = extent0.map(Math.round); // should round it to bins
	
	//d3.selectAll("text.complabel").attr("x",brushX(d3.sum(extent1)/extent1.length));

	compFextent = extent1;

	// initialize new values
	var refF = Array(allDataRaw[0].length);
	var compF = Array(allDataRaw[0].length);
	for (var i=0; i<allDataRaw[0].length; i++) {
            refF[i]= 0;
            compF[i]= 0;
	}
	// loop over each slice of data
	for (var i=0; i<allDataRaw[0].length; i++) {
		for (var k=refFextent[0]; k<refFextent[1]; k++) {
                    refF[i] += allData[k][i];
		}
		for (var k=compFextent[0]; k<compFextent[1]; k++) {
                    compF[i] += allData[k][i];
		}
	}
	
	console.log("redrawing shift");
	var shiftObj = shift(refF,compF,lens,words);
	plotShift(d3.select("#figure01"),shiftObj.sortedMag.slice(0,200),
		  shiftObj.sortedType.slice(0,200),
		  shiftObj.sortedWords.slice(0,200),
		  shiftObj.sortedWordsEn.slice(0,200),
		  shiftObj.sumTypes,
		  shiftObj.refH,
		  shiftObj.compH);

	d3.select(this).transition()
	    .call(brush.extent(extent1))
	    .call(brush.event);

    }
}





