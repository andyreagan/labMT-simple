// make the plot
function plotShift(figure,sortedMag,sortedType,sortedWords,sumTypes,refH,compH) {
/* plot the shift

   -take a d3 selection, and draw the shift SVG on it
   -requires sorted vectors of the shift magnitude, type and word
       for each word

*/

    var margin = {top: 0, right: 0, bottom: 0, left: 0},
    figwidth = 600 - margin.left - margin.right,
    figheight = 800 - margin.top - margin.bottom,
    width = .775*figwidth,
    height = .775*figheight,
    figcenter = width/2,
    numWords = 30;

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
    .range([height, 80]); 

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
    .scale(x)
    .ticks(5)
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
  .attr("transform", "(0,0)")
  .call(yAxis);

var xAxis = create_xAxis()
    .innerTickSize(6)
    .outerTickSize(0);

axes.append("g")
  .attr("class", "x axis ")
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

// now something else
var unclipped_axes = axes;

// draw the summary things
unclipped_axes.append("line")
    .attr("x1",0)
    .attr("x2",width)
    .attr("y1",75)
    .attr("y2",75)
    .style({"stroke-width" : "2", "stroke": "black"});

var maxShiftSum = Math.max(Math.abs(sumTypes[1]),Math.abs(sumTypes[2]),sumTypes[0],sumTypes[3]);
topScale = d3.scale.linear()
  .domain([-maxShiftSum,maxShiftSum])
  .range([width*.1,width*.9]);

unclipped_axes.selectAll(".sumrectR")
   .data([sumTypes[3],sumTypes[0],sumTypes[3]-Math.abs(sumTypes[1])])
   .enter()
   .append("rect")
   .attr("fill", function(d,i) { if (i==0) {return "#FFFF4C";} else if (i==1) {return "#B3B3FF";} else {return "#FFFF4C";}})
   .attr("class", "sumrectR")
   .attr("x",function(d,i) { 
                             if (d>0) { 
                               return figcenter;
                             } 
                             else { return topScale(d)} }
                             )
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
        if (i==0) {

        d3.selectAll(".rect").transition().duration(1000).style({'opacity':'0.0','stroke-width':'1','stroke':'rgb(0,0,0)'}).attr("x",function(d,i) { if (d<0) { return -500; } else {return 500; }}); 
        d3.selectAll(".rect.three").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).style({'opacity':'0.7','stroke-width':'1','stroke':'rgb(0,0,0)'}).attr("x",figcenter); 
        d3.selectAll(".text").transition().duration(1000).style({'opacity':'0.0'}).attr("x",function(d,i) { if (d<0) { return -500; } else {return 500; }}); ; 
        d3.selectAll(".text.three").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; } ).attr("x",function(d,i) { return x(d)+2; } ).style({'opacity':'1.0'}); 

        }

        else if (i==1) {

        d3.selectAll(".rect").transition().duration(1000).style({'opacity':'0.0','stroke-width':'1','stroke':'rgb(0,0,0)'}).attr("x",function(d,i) { if (d<0) { return -500; } else {return 500; }}); 
        d3.selectAll(".rect.zero").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).style({'opacity':'0.7','stroke-width':'1','stroke':'rgb(0,0,0)'}).attr("x",figcenter); 
        d3.selectAll(".text").transition().duration(1000).style({'opacity':'0.0'}).attr("x",function(d,i) { if (d<0) { return -500; } else {return 500; }}); ; 
        d3.selectAll(".text.zero").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; } ).attr("x",function(d,i) { return x(d)+2; } ).style({'opacity':'1.0'}); 

        }
    } );


unclipped_axes.selectAll(".sumtextR")
   .data([sumTypes[3],sumTypes[0]])
   .enter()
   .append("text")
   .attr("class", "sumtextR")
   .style("text-anchor", "start")
   .attr("y",function(d,i) { return i*22+22; } )
   .text(function(d,i) { if (i == 0) {return "\u2211+\u2191";} else { return"\u2211-\u2193";} })
   .attr("x",function(d,i) { return topScale(d)+5; });

unclipped_axes.selectAll(".sumtextL")
   .data([sumTypes[1],sumTypes[2]])
   .enter()
   .append("text")
   .attr("class", "sumtextL")
   .style("text-anchor", "end")
   .attr("y",function(d,i) { return i*22+22; } )
   .text(function(d,i) { if (i == 0) {return "\u2211+\u2193";} else { return"\u2211-\u2191";} })
   .attr("x",function(d,i) { return topScale(d)-5; });

unclipped_axes.selectAll(".sumrectL")
   .data([sumTypes[1],sumTypes[2],sumTypes[0]-Math.abs(sumTypes[2])])
   .enter()
   .append("rect")
   .attr("fill", function(d,i) { if (i==0) {return "#FFFFB3";} else if (i==1) {return "#4C4CFF";} else {return "#4C4CFF";}})
   .attr("class", "sumrectL")
   .attr("x",function(d,i) { 
                             if (i<2) { 
                               return topScale(d);
                             } 
                             else { 
                                 if (d*(sumTypes[3]-Math.abs(sumTypes[1])) > 0) {
                                     if (d>0) {
                                         return topScale((sumTypes[3]-Math.abs(sumTypes[1])));
                                      }
                                     else {
					 return topScale(d)-(figcenter-topScale((sumTypes[3]-Math.abs(sumTypes[1]))));
                                     }
                                 } 
                                 else { 
                                     if (d>0) {return figcenter} 
                                     else { return topScale(d)} }
                                 }
                             }
                             )
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
        if (i==0) {

        d3.selectAll(".rect").transition().duration(1000).style({'opacity':'0.0','stroke-width':'1','stroke':'rgb(0,0,0)'}).attr("x",function(d,i) { if (d<0) { return -500; } else {return 500; }}); 
        d3.selectAll(".rect.one").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).style({'opacity':'0.7','stroke-width':'1','stroke':'rgb(0,0,0)'}).attr("x",function(d,i) {return x(d); }); 
        d3.selectAll(".text").transition().duration(1000).style({'opacity':'0.0'}).attr("x",function(d,i) { if (d<0) { return -500; } else {return 500; }}); ; 
        d3.selectAll(".text.one").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; } ).attr("x",function(d,i) { return x(d)-2; } ).style({'opacity':'1.0'}); 

        }

        else if (i==1) {

        d3.selectAll(".rect").transition().duration(1000).style({'opacity':'0.0','stroke-width':'1','stroke':'rgb(0,0,0)'}).attr("x",function(d,i) { if (d<0) { return -500; } else {return 500; }}); 
        d3.selectAll(".rect.two").transition().duration(1000).attr("y",function(d,i) { return y(i+1); }).style({'opacity':'0.7','stroke-width':'1','stroke':'rgb(0,0,0)'}).attr("x",function(d,i) {return x(d); }); 
        d3.selectAll(".text").transition().duration(1000).style({'opacity':'0.0'}).attr("x",function(d,i) { if (d<0) { return -500; } else {return 500; }}); ; 
        d3.selectAll(".text.two").transition().duration(1000).attr("y",function(d,i) { return y(i+1)+11; } ).attr("x",function(d,i) { return x(d)-2; } ).style({'opacity':'1.0'}); 
        }
    } );
 
axes = axes.append("g")
  .attr("clip-path","url(#clip)");

canvas.append("text")
   .text("Word Rank")
   .attr("class","axes-text")
   .attr("x",(figwidth-width)/4)
   .attr("y",figheight/2+30)
   .attr("font-size", "20.0px")
   .attr("fill", "#000000")
   .attr("transform", "rotate(-90.0," + (figwidth-width)/4 + "," + (figheight/2+30) + ")");

canvas.append("text")
   .text("Per word average happiness shift")
   .attr("class","axes-text")
   .attr("x",width/2+(figwidth-width)/2)
   .attr("y",3*(figheight-height)/4+height)
   .attr("font-size", "20.0px")
   .attr("fill", "#000000")
   .attr("style", "text-anchor: middle;");

canvas.selectAll(".sumtext")
   .data([refH,compH])
   .enter()
   .append("text")
   .text(function(d,i) { if (i==0) {
                             return "Reference happiness " + (d.toFixed(3));
                         }
                         else {
			     return "Comparison happiness " + (d.toFixed(3));
			 }}
         )
   .attr("class","axes-text")
   .attr("x",width/2+(figwidth-width)/2)
   .attr("y",function(d,i) { return i*20+45 })
   .attr("font-size", "16.0px")
   .attr("fill", "#000000")
   .attr("style", "text-anchor: middle;");

intStr = ["zero","one","two","three"];

axes.selectAll(".rect")
   .data(sortedMag)
   .enter()
   .append("rect")
   .attr("fill", function(d,i) { if (sortedType[i] == 2) {return "#4C4CFF";} else if (sortedType[i] == 3) {return "#FFFF4C";} else if (sortedType[i] == 0) {return "#B3B3FF";} else { return "#FFFFB3"; }})
   .attr("class", function(d,i) { return "rect "+intStr[sortedType[i]]; })
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

axes.selectAll(".text")
   .data(sortedMag)
   .enter()
   .append("text")
   //.attr("fill", function(d,i) { if (sortedType[i] == 0 || sortedType[i] == 2) {return "blue";} else { return "yellow"; }})
   .attr("class", function(d,i) { return "text "+intStr[sortedType[i]]; })
   .style("text-anchor", function(d,i) { if (sortedMag[i] < 0) { return "end";} else { return "start";}})
   .attr("y",function(d,i) { return y(i+1)+11; } )
   .text(function(d,i) { if (sortedType[i] == 0) {tmpStr = "-\u2193";} else if (sortedType[i] == 1) {tmpStr = "\u2193+";}
   else if (sortedType[i] == 2) {tmpStr = "\u2191-";} else {tmpStr = "+\u2191";}
   if (sortedMag[i] < 0) {return tmpStr.concat(sortedWords[i]);} else { return sortedWords[i].concat(tmpStr); } })
   .attr("x",function(d,i) { if (d>0) {return x(d)+2;} else {return x(d)-2; } } );

    function zoomed() {
    //console.log(d3.event);
    //console.log(d3.event.translate[1]);
    // d3.event.translate[1] = Math.min(0,d3.event.translate[1])
    axes.selectAll(".rect").attr("transform", "translate(0," + Math.min(0,d3.event.translate[1]) + ")");
    axes.selectAll(".text").attr("transform", "translate(0," + Math.min(0,d3.event.translate[1]) + ")");
    //d3.select(".y.axis").attr("transform", "translate(0," + Math.min(0,d3.event.translate[1]) + ")");
    d3.select(".y.axis").call(yAxis);
    // make the tick lines show up on redraw							    
    d3.selectAll(".tick line").style({'stroke':'black'});
     };

console.log("happiness");

};
