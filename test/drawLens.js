function drawLens(figure,lens) {
    margin = {top: 0, right: 0, bottom: 0, left: 0},
    figwidth = 600 - margin.left - margin.right,
    figheight = 150 - margin.top - margin.bottom,
    width = .775*figwidth,
    height = .775*figheight;

    // remove an old figure if it exists
    figure.select(".canvas").remove();

    var canvas = figure.append("svg")
	.attr("width",figwidth)
	.attr("height",figheight)
	.attr("class","canvas");

    // create the x and y axis
    x = d3.scale.linear()
	.domain([d3.min(lens),d3.max(lens)])
	.range([0,width]);
    
    // use d3.layout http://bl.ocks.org/mbostock/3048450
    data = d3.layout.histogram()
        .bins(x.ticks(75))
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
	    .ticks(5)
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
	.attr("class", "y axis ")
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

    var bar = axes.selectAll(".rect")
        .data(data)
        .enter()
        .append("g")
        .attr("class","distrect")
        .attr("fill","yellow")
        .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

    bar.append("rect")
	.attr("x", 1)
	.attr("width", x(data[0].dx+d3.min(lens))-2 )
	.attr("height", function(d) { return height - y(d.y); });

    console.log(x(d3.min(lens)));


}




