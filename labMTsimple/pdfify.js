var fs = require('fs');
var convertFactory = require('electron-html-to');

var htmlfile = process.argv[2];
var pdffile = process.argv[3];
console.log("converting " + htmlfile + " to " + pdffile);
console.log(process.cwd());

var conversion = convertFactory({
    converterPath: convertFactory.converters.PDF,
    // timeout: 20000,
    numberOfWorkers: 2,
    allowLocalFilesAccess: true,
    // strategy: 'electron-ipc | electron-server | dedicated-process'
    strategy: 'dedicated-process',
});

conversion({ html: '<h1>Hello World</h1>' }, function(err, result) {
    if (err) {
        return console.error(err);
    }

    console.log(result.numberOfPages);
    result.stream.pipe(fs.createWriteStream('anywhere.pdf'));
    conversion.kill(); // necessary if you use the electron-server strategy, see bellow for details
});

// fs.readFile(htmlfile, function (err, data) {
//     console.log("read the file");
//     if (err) {
//         throw err;
//     }
//     // console.log(data);
//     conversion({ html: data }, function(err, result) {
//         if (err) {
//             return console.error(err);
//         }
//         console.log("converted the data");
//         // console.log(result.numberOfPages);
//         result.stream.pipe(fs.createWriteStream(pdffile));
//         conversion.kill(); // necessary if you use the electron-server strategy, see bellow for details 
//     });
// });

