function drawBookTimeseries(figure,data) {
/* takes a d3 selection and draws the lens distribution
   on slide of the stop-window
     -reload data csv's
     -cut out stops words (0 the frequencies)
     -call shift on these frequency vectors */


    margin = {top: 0, right: 0, bottom: 0, left: 0},
    figwidth = 600 - margin.left - margin.right,
    figheight = 100 - margin.top - margin.bottom,
    width = .775*figwidth,
    height = figheight;

    console.log(data);

    // remove an old figure if it exists
    figure.select(".canvas").remove();

    var canvas = figure.append("svg")
	.attr("width",figwidth)
	.attr("height",figheight)
	.attr("class","canvas");


    // create the x and y axis
    x = d3.scale.linear()
	//.domain([d3.min(lens),d3.max(lens)])
	.domain([0,data.length])
	.range([0,width]);
    
    // use d3.layout http://bl.ocks.org/mbostock/3048450
    // data = d3.layout.histogram()
    //     .bins(x.ticks(65))
    //     (lens);

    // linear scale function
    y =  d3.scale.linear()
	.domain([d3.min(data),d3.max(data)])
	.range([height-8, 4]); 

    // create the axes themselves
    var axes = canvas.append("g")
	.attr("transform", "translate(" + (0.125 * figwidth) + "," +
	      ((1 - 0.125 - 0.775 - .09) * figheight) + ")") // 99 percent
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

    // // create the clip boundary
    // var clip = axes.append("svg:clipPath")
    // 	.attr("id","clip")
    // 	.append("svg:rect")
    // 	.attr("x",0)
    // 	.attr("y",0)
    // 	.attr("width",width)
    // 	.attr("height",height);

    // var unclipped_axes = axes;

    // axes = axes.append("g")
    // 	.attr("clip-path","url(#clip)");
 
    var line = d3.svg.line()
	.x(function(d,i) { return x(i); })
	.y(function(d) { return y(d); })
	.interpolate("linear");

    axes.append("path")
	.datum(data)
	.attr("class", "line")
	.attr("d", line)
	.attr("stroke","black")
	.attr("stroke-width",3)
	.attr("fill","none");

    var area = d3.svg.area()
	.x(function(d,i) { return x(i); })
	.y0(height)
	.y1(function(d) { return y(d); });

    axes.append("path")
        .datum(data)
        .attr("class", "area")
        .attr("d", area)
        .attr("fill","#D3D3D3");

}





