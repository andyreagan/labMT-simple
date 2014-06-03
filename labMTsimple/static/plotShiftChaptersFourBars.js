// make the plot
function plotShift(figure,sortedMag,sortedType,sortedWords,sortedWordsEn,sumTypes,refH,compH) {
    /* plot the shift

       -take a d3 selection, and draw the shift SVG on it
       -requires sorted vectors of the shift magnitude, type and word
       for each word

    */
    var margin = {top: 0, right: 0, bottom: 0, left: 0},
    figwidth = 500 - margin.left - margin.right,
    figheight = 600 - margin.top - margin.bottom,
    width = .775*figwidth,
    height = .775*figheight,
    figcenter = width/2,
    yHeight = 101,
    clipHeight = 100,
    barHeight = 95,
    numWords = 22,
    shiftTypeSelect = false;

    // remove an old figure if it exists
    figure.select(".canvas").remove();

    var canvas = figure.append("svg")
	.attr("width",figwidth)
	.attr("height",figheight)
	.attr("class","canvas")

    // create the x and y axis
    // scale in x by width of the top word
    // could still run into a problem if top magnitudes are similar
    // and second word is longer
    x = d3.scale.linear()
	.domain([-Math.abs(sortedMag[0]),Math.abs(sortedMag[0])])
	.range([(sortedWords[0].length+3)*9, width-(sortedWords[0].length+3)*9]);

    // linear scale function
    y =  d3.scale.linear()
	.domain([numWords,1])
	.range([height, yHeight]); 

    // zoom object for the axes
    var zoom = d3.behavior.zoom()
	.y(y) //pass linear scale function
    //.translate([10,10])
	.scaleExtent([1,1])
	.on("zoom",zoomed);

    // create the axes themselves
    var axes = canvas.append("g")
	.attr("transform", "translate(" + (0.125 * figwidth) + "," +
	      ((1 - 0.125 - 0.775) * figheight) + ")")
	.attr("width", width)
	.attr("height", height)
	.attr("class", "main")
	.call(zoom);

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
	    .ticks(4)
	    .scale(x)
	    .orient("bottom"); }

    // axis creation function
    var create_yAxis = function() {
	return d3.svg.axis()
	    .scale(y) //linear scale function
	    .orient("left"); }

    // draw the axes
    var yAxis = create_yAxis()
	.innerTickSize(6)
	.outerTickSize(0);

    axes.append("g")
	.attr("class", "y axis ")
	.attr("font-size", "14.0px")
	.attr("transform", "(0,0)")
	.call(yAxis);

    var xAxis = create_xAxis()
	.innerTickSize(6)
	.outerTickSize(0);

    axes.append("g")
	.attr("class", "x axis ")
	.attr("font-size", "14.0px")
	.attr("transform", "translate(0," + (height) + ")")
	.call(xAxis);

    d3.selectAll(".tick line").style({'stroke':'black'});

    // create the clip boundary
    var clip = axes.append("svg:clipPath")
	.attr("id","clip")
	.append("svg:rect")
	.attr("x",0)
	.attr("y",clipHeight)
	.attr("width",width)
	.attr("height",height-clipHeight);

    // now something else
    var unclipped_axes = axes;

    // draw the summary things
    unclipped_axes.append("line")
	.attr("x1",0)
	.attr("x2",width)
	.attr("y1",barHeight)
	.attr("y2",barHeight)
	.style({"stroke-width" : "2", "stroke": "black"});

    var maxShiftSum = Math.max(Math.abs(sumTypes[1]),Math.abs(sumTypes[2]),sumTypes[0],sumTypes[3]);
    topScale = d3.scale.linear()
	.domain([-maxShiftSum,maxShiftSum])
	.range([width*.1,width*.9]);

    // define the RHS summary bars so I can add if needed
    var summaryArray = [sumTypes[3],sumTypes[0],sumTypes[3]+sumTypes[1],d3.sum(sumTypes)];

    unclipped_axes.selectAll(".sumrectR")
	.data(summaryArray)
	.enter()
	.append("rect")
	.attr("fill", function(d,i) { 
	    if (i==0) { return "#FFFF4C"; } 
	    else if (i==1) { return "#B3B3FF"; } 
	    else if (i==2) {
		// if positive, the postive increasing words won, color dark yellow
		if (d>0) { return "#FFFF4C";}
		// positive decreasing words won, color light yellow
		else { return "#FFFFB3";}
	    }
	    else {
		// always dark grey
		return "#272727";
	    } })
	.attr("class", "sumrectR")
	.attr("x",function(d,i) { 
            if (d>0) { return figcenter; } 
            else { return topScale(d)} } )
        // don't move the fourth bar down as much
	.attr("y",function(d,i) { if (i<3) { return i*22+7;} else { return i*22+1;} } )
	.style({'opacity':'0.7','stroke-width':'1','stroke':'rgb(0,0,0)'})
	.attr("height",function(d,i) { return 17; } )
	.attr("width",function(d,i) { if (d>0) {return topScale(d)-figcenter;} else {return figcenter-topScale(d); } } )
	.on('mouseover', function(d){
            var rectSelection = d3.select(this).style({opacity:'1.0'});
	})
	.on('mouseout', function(d){
            var rectSelection = d3.select(this).style({opacity:'0.7'});
	})
	.on('click', function(d,i) { 
	    shiftTypeSelect = true;
	    resetButton();
	    if (i==0) {
		d3.selectAll("rect.shiftrect.zero").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("rect.shiftrect.one").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("rect.shiftrect.two").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("rect.shiftrect.three").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform","translate(0,0)");
		d3.selectAll("text.shifttext.zero").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("text.shifttext.one").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("text.shifttext.two").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("text.shifttext.three").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform","translate(0,0)");
	    }
	    else if (i==1) {
		d3.selectAll("rect.shiftrect.zero").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform","translate(0,0)");
		d3.selectAll("rect.shiftrect.one").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("rect.shiftrect.two").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("rect.shiftrect.three").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("text.shifttext.zero").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform","translate(0,0)");
		d3.selectAll("text.shifttext.one").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("text.shifttext.two").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("text.shifttext.three").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
	    }
	} );

    unclipped_axes.selectAll(".sumtextR")
	.data([sumTypes[3],sumTypes[0],d3.sum(sumTypes)])
	.enter()
	.append("text")
	.attr("class", "sumtextR")
	.style("text-anchor",function(d,i) { if (d>0) {return "start";} else {return "end";} })
	.attr("y",function(d,i) { if (i<2) {return i*22+22;} else if ((sumTypes[3]+sumTypes[1])*(sumTypes[0]+sumTypes[2])<0) {return i*22+39; } else {return i*22+30; } })
	.text(function(d,i) { if (i == 0) {return "\u2211+\u2191";} if (i==1) { return"\u2211-\u2193";} else { return "\u2211";} } )
    // push to the side of d
	.attr("x",function(d,i) { return topScale(d)+5*d/Math.abs(d); });

    var summaryArray = [sumTypes[1],sumTypes[2],sumTypes[0]+sumTypes[2]];

    unclipped_axes.selectAll(".sumrectL")
	.data(summaryArray)
	.enter()
	.append("rect")
	.attr("fill", function(d,i) { 
	    if (i==0) {
		return "#FFFFB3";
	    } 
	    else if (i==1) {
		return "#4C4CFF";
	    } 
	    else {
		// choose color based on whether increasing/decreasing wins
		if (d>0) {
		    return "#B3B3FF";
		}
		else {
		    return "#4C4CFF";
		}
	    }
	})
	.attr("class", "sumrectL")
	.attr("x",function(d,i) { 
	    if (i<2) { 
		return topScale(d);
	    } 
	    else { 
		// place the sum of negatives bar
		// if they are not opposing
		if ((sumTypes[3]+sumTypes[1])*(sumTypes[0]+sumTypes[2])>0) {
		    // if positive, place at end of other bar
		    if (d>0) {
			return topScale((sumTypes[3]+sumTypes[1]));
		    }
		    // if negative, place at left of other bar, minus length (+topScale(d))
		    else {
			return topScale(d)-(figcenter-topScale((sumTypes[3]+sumTypes[1])));
		    }
		} 
		else { 
		    if (d>0) {return figcenter} 
		    else { return topScale(d)} }
	    }
	})
	.attr("y",function(d,i) { return i*22+7; } )
	.style({'opacity':'0.7','stroke-width':'1','stroke':'rgb(0,0,0)'})
	.attr("height",function(d,i) { return 17; } )
	.attr("width",function(d,i) { if (d>0) {return topScale(d)-figcenter;} else {return figcenter-topScale(d); } } )
	.on('mouseover', function(d){
            var rectSelection = d3.select(this).style({opacity:'1.0'});
	})
	.on('mouseout', function(d){
            var rectSelection = d3.select(this).style({opacity:'0.7'});
	})
	.on('click', function(d,i) { 
	    shiftTypeSelect = true;
	    resetButton();
            if (i==0) {
		d3.selectAll("rect.shiftrect.zero").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("rect.shiftrect.one").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform","translate(0,0)");
		d3.selectAll("rect.shiftrect.two").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("rect.shiftrect.three").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("text.shifttext.zero").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("text.shifttext.one").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform","translate(0,0)");
		d3.selectAll("text.shifttext.two").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("text.shifttext.three").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
            }
            else if (i==1) {
		d3.selectAll("rect.shiftrect.zero").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("rect.shiftrect.two").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform","translate(0,0)");
		d3.selectAll("rect.shiftrect.one").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("rect.shiftrect.three").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("text.shifttext.zero").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("text.shifttext.two").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform","translate(0,0)");
		d3.selectAll("text.shifttext.one").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
		d3.selectAll("text.shifttext.three").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; }).attr("transform",function(d,i) { if (d<0) { return "translate(-500,0)"; } else { return "translate(500,0)"; } });
            }
	} );

    unclipped_axes.selectAll(".sumtextL")
	.data([sumTypes[1],sumTypes[2]])
	.enter()
	.append("text")
	.attr("class", "sumtextL")
	.style("text-anchor", "end")
	.attr("y",function(d,i) { return i*22+22; } )
	.text(function(d,i) { if (i == 0) {return "\u2211+\u2193";} else { return"\u2211-\u2191";} })
	.attr("x",function(d,i) { return topScale(d)-5; });
    
    axes = axes.append("g")
	.attr("clip-path","url(#clip)");

    canvas.append("text")
	.text("Word Rank")
	.attr("class","axes-text")
	.attr("x",(figwidth-width)/4)
	.attr("y",figheight/2+30)
	.attr("font-size", "16.0px")
	.attr("fill", "#000000")
	.attr("transform", "rotate(-90.0," + (figwidth-width)/4 + "," + (figheight/2+30) + ")");

    canvas.append("text")
	.text("Per word average happiness shift")
	.attr("class","axes-text")
	.attr("x",width/2+(figwidth-width)/2)
	.attr("y",3*(figheight-height)/4+height)
	.attr("font-size", "16.0px")
	.attr("fill", "#000000")
	.attr("style", "text-anchor: middle;");

    if (compH >= refH) {
	var happysad = "happier";
    }
    else { 
	var happysad = "less happy";
    }

    canvas.selectAll(".sumtext")
	.data(["Why ",refH,compH])
	.enter()
	.append("text")
	.text(function(d,i) { 
	    if (i==0) {
		// if there are names of the texts, put them here
		if (Math.abs(refH-compH) < 0.01) { return "How the words of reference and comparison differ";}
		else { return d+"comparison "+" is "+happysad+" than "+"reference ";}
	    }
	    else if (i==1) {
		return "Reference happiness " + (d.toFixed(2));
	    }
	    else {
		return "Comparison happiness " + (d.toFixed(2));
	    }})
	.attr("class","axes-text")
	.attr("x",width/2+(figwidth-width)/2)
	.attr("y",function(d,i) { return i*20+13 })
	.attr("font-size", "16.0px")
	.attr("fill", "#000000")
	.attr("style", "text-anchor: middle;");

    intStr = ["zero","one","two","three"];

    axes.selectAll("rect.shiftrect")
	.data(sortedMag)
	.enter()
	.append("rect")
	.attr("fill", function(d,i) { if (sortedType[i] == 2) {return "#4C4CFF";} else if (sortedType[i] == 3) {return "#FFFF4C";} else if (sortedType[i] == 0) {return "#B3B3FF";} else { return "#FFFFB3"; }})
	.attr("class", function(d,i) { return "shiftrect "+intStr[sortedType[i]]; })
	.attr("x",function(d,i) { 
            if (d>0) { 
                return figcenter;
            } 
            else { return x(d)} }
             )
	.attr("y",function(d,i) { return y(i+1); } )
	.style({'opacity':'0.7','stroke-width':'1','stroke':'rgb(0,0,0)'})
	.attr("height",function(d,i) { return 15; } )
	.attr("width",function(d,i) { if (d>0) {return x(d)-figcenter;} else {return figcenter-x(d); } } )
	.on('mouseover', function(d){
            var rectSelection = d3.select(this).style({opacity:'1.0'});
	})
	.on('mouseout', function(d){
            var rectSelection = d3.select(this).style({opacity:'0.7'});
	});

    var flipVector = Array(sortedWords.length);

    axes.selectAll("text.shifttext")
	.data(sortedMag)
	.enter()
	.append("text")
    //.attr("fill", function(d,i) { if (sortedType[i] == 0 || sortedType[i] == 2) {return "blue";} else { return "yellow"; }})
	.attr("class", function(d,i) { return "shifttext "+intStr[sortedType[i]]; })
	.style("text-anchor", function(d,i) { if (sortedMag[i] < 0) { return "end";} else { return "start";}})
	.attr("y",function(d,i) { return y(i+1)+11; } )
	.text(function(d,i) { if (sortedType[i] == 0) {tmpStr = "-\u2193";} else if (sortedType[i] == 1) {tmpStr = "\u2193+";}
			      else if (sortedType[i] == 2) {tmpStr = "\u2191-";} else {tmpStr = "+\u2191";}
			      if (sortedMag[i] < 0) {return tmpStr.concat(sortedWords[i]);} else { return sortedWords[i].concat(tmpStr); } })
	.attr("x",function(d,i) { if (d>0) {return x(d)+2;} else {return x(d)-2; } } )
	.on("click",function(d,i){
	    // goal is to toggle translation
	    // need translation vector
	    //console.log(flipVector[i]);
	    if (flipVector[i]) { 
		if (sortedType[i] == 0) {tmpStr = "-\u2193";} else if (sortedType[i] == 1) {tmpStr = "\u2193+";}
		else if (sortedType[i] == 2) {tmpStr = "\u2191-";} else {tmpStr = "+\u2191";}
		if (sortedMag[i] < 0) { tmpStr = tmpStr.concat(sortedWords[i]);} else { tmpStr = sortedWords[i].concat(tmpStr); } 
		flipVector[i] = 0;}
	    else {
		if (sortedType[i] == 0) {tmpStr = "-\u2193";} 
		else if (sortedType[i] == 1) {tmpStr = "\u2193+";}
		else if (sortedType[i] == 2) {tmpStr = "\u2191-";} 
		else {tmpStr = "+\u2191";}
		if (sortedMag[i] < 0) { tmpStr = tmpStr.concat(sortedWordsEn[i]);} 
		else { tmpStr = sortedWordsEn[i].concat(tmpStr); } 
		flipVector[i] = 1; }
	    //console.log(tmpStr);
	    newText = d3.select(this).text(tmpStr);
	    //console.log(d);
	    //console.log(i);
	});


    function resetButton() {
	d3.selectAll(".resetbutton").remove();

	var resetGroup = canvas.append("g")
	     .attr("class","resetbutton");

	resetGroup.append("rect")
	    .attr("x",385)
	    .attr("y",133)
	    .attr("rx",3)
	    .attr("ry",3)
	    .attr("width",48)
	    .attr("height",16)
	    .attr("fill","#F0F0F0") //http://www.w3schools.com/html/html_colors.asp
	    .style({'stroke-width':'0.5','stroke':'rgb(0,0,0)'});
	//.on("click",function() { console.log("clicked embed"); });

	resetGroup.append("text")
	    .text("Reset")
	    .attr("x",393)
	    .attr("y",144)
	    .attr("font-size", "11.0px")

	resetGroup.append("rect")
	    .attr("x",385)
	    .attr("y",133)
	    .attr("rx",3)
	    .attr("ry",3)
	    .attr("width",48)
	    .attr("height",16)
	    .attr("fill","white") //http://www.w3schools.com/html/html_colors.asp
	    .style({"opacity": "0.0"})
	    .on("click",function() { 
		//console.log("clicked reset");
		shiftTypeSelect = false;		
		axes.selectAll("rect.shiftrect").transition().duration(1000)
		    .attr("y", function(d,i) { return y(i+1) })
		    .attr("transform","translate(0,0)")
	            .attr("x",function(d,i) { if (d<0) { return x(d);} 
					      else { return figcenter; }});
		axes.selectAll("text.shifttext").transition().duration(1000)
		    .attr("y", function(d,i) { return y(i+1)+11; } )
	            .attr("x",function(d,i) { if (d<0) { return x(d)-2; }
					      else { return x(d)+2; } })
		    .attr("transform","translate(0,0)");
		d3.selectAll(".resetbutton").remove();
	    });
    }

    function zoomed() {
	//console.log(d3.event);
	//console.log(d3.event.translate[1]);
	// d3.event.translate[1] = Math.min(0,d3.event.translate[1])
	if (shiftTypeSelect) {
	    for (var j=0; j<4; j++) {
		axes.selectAll("rect.shiftrect."+intStr[j]).attr("y", function(d,i) { return y(i+1) });
		axes.selectAll("text.shifttext."+intStr[j]).attr("y", function(d,i) { return y(i+1)+11 }); }
	}
	else {
	    axes.selectAll("rect.shiftrect").attr("y", function(d,i) { return y(i+1) });
	    axes.selectAll("text.shifttext").attr("y", function(d,i) { return y(i+1)+11 });
	}
	//d3.select(".y.axis").attr("transform", "translate(0," + Math.min(0,d3.event.translate[1]) + ")");
	d3.select(".y.axis").call(yAxis);
	// make the tick lines show up on redraw
	d3.selectAll(".tick line").style({'stroke':'black'});
    };
    //console.log("happiness (it all worked)");

    canvas.append("text")
	.text("by Andy Reagan")
        .attr("fill","#404040")
	.attr("x",100)
	.attr("y",10)
	.attr("font-size", "11.0px");

    //resetButton();
};









