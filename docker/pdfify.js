var fs = require('fs');
var convertFactory = require('electron-html-to');

var htmlfile = process.argv[2];
var pdffile = process.argv[3];
console.log("converting " + htmlfile + " to " + pdffile);
console.log(process.cwd());

var conversion = convertFactory({
    converterPath: convertFactory.converters.PDF
});

fs.readFile(htmlfile, function (err, data) {
    console.log("read the file");
    if (err) {
        throw err;
    }
    // console.log(data);
    conversion({ html: data }, function(err, result) {
        console.log("converted the data");
        if (err) {
            return console.error(err);
        }
        // console.log(result.numberOfPages);
        result.stream.pipe(fs.createWriteStream(pdffile));
        conversion.kill(); // necessary if you use the electron-server strategy, see bellow for details 
    });
});

