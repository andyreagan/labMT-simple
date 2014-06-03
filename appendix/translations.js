
google.load("visualization", "1", {packages:["corechart"]});
google.setOnLoadCallback(drawChart);
function drawChart() {

    var data = new google.visualization.DataTable();
    data.addColumn('number','Average Valence');
    data.addColumn('number','Average Valence');
    data.addColumn({
	type: 'string',
	role: 'tooltip'
    });

    data.addColumn('number','y = x');
    data.addRows([
	[ 1, null, null ,1 ],[ 9, null, null ,9 ],]);

    d3.text("data/translation-files/TransValChart_English_German.txt", function(translation) {

	tmp = translation.split("\n");
	tmp = tmp.split(1,tmp.length-1);
	tmp = tmp.map(function(d) { return d.split(","); });
	data.addRows(tmp);

	var options = {
	    title: 'English vs German Average Word Happiness', 
	    titleTextStyle: { textPosition: 'in', fontType: 'helvetica', fontSize: 28,  bold: true}, 
	    hAxis: {title: 'English Average Word Happiness', minValue: 1, maxValue: 9, 
		    titleTextStyle: { textPosition: 'in', fontType: 'helvetica', fontSize: 25,  bold: true}    }, 
	    vAxis: {title: 'German Average Word Happiness', minValue: 1, maxValue: 9, 
		    titleTextStyle: { textPosition: 'in', fontType: 'helvetica', fontSize: 25,  bold: true}    }, 
	    pointSize: 1,
	    legend: 'none',
	    trendlines: { 1: { color: 'red',
			       opacity: 0.2,
			     } },
	};

	var chart = new google.visualization.ScatterChart(document.getElementById('chart_div'));
	chart.draw(data, options);
    });
};















    


