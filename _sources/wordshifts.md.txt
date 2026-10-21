Making Wordshifts
================

I just merged updates to the d3 wordshift plotting into labMTsimple, and combined with phantom crowbar (see previous post), it's easier than ever to use the labMT data set to compare texts.

To make an html page with the shift, you'll just need to have labMT-simple installed.
To automate the process into generating svg files, you'll need the phantom crowbar, which depends on phantomjs.
To go all the way to pdf, you'll also need inkscape for making vectorized pdfs, or rsvg for making better formatted, but rasterized, versions.

Let's get set up to make shifts automatically.
Since they're aren't many dependencies all the way down, start by getting phantomjs installed, then the phantom-crowbar.

Installing phantom-crowbar
--------------------------

For the phantomjs, I prefer to use homebrew:

```bash
brew update
brew upgrade
brew install phantomjs
```

Then to get the crowbar, clone the git repository.

```bash
cd ~
git clone https://github.com/andyreagan/phantom-crowbar
```

To use it system-wide, I use the bash alias:

```bash
alias phantom-crowbar="/usr/local/bin/phantomjs ~/phantom-crowbar/phantom-crowbar.js"
```

Without too much detail, I recommend adding this to your `~/.bash_profile` so that it's loaded every time you start a terminal session.

Installing inkscape
----------------------

You only need inkscape if you want to go from svg to pdf (and there are other ways too), but this one is easy with, again, homebrew.

```bash
brew install inkscape
```

Installing rsvg
----------------------

You only need inkscape if you want to go from svg to pdf (and there are other ways too), but this one is easy with, again, homebrew.

```bash
brew install librsvg
```

Installing labMTsimple
----------------------

There are two ways to get it: using pip of cloning the git repo.
If you're not sure, use pip.
I think pip makes it easier to keep it up to date, etc.

```bash
pip install labMTsimple
```

Making your first shift
-----------------------

If you cloned the git repository, install the thing and then you can check out the example in `examples/example.py`.
If you went with pip, see that file on [github](https://github.com/andyreagan/labMT-simple/blob/master/examples/example.py).

Go ahead and run that script!
```
python example-002.py
```

You can open the html file to see the shift in any browser, with your choice of local webserver.
Python's SimpleHTTPServer works fine, and I've found that the node based http-server is a bit more stable.

To take out the svg, go ahead and use the `phantom-crowbar.js` file copied to the `example/static` directory.
Running it looks like this, for me:
```
/usr/local/bin/phantomjs js/shift-crowbar.js example-002.html shiftsvg wordshift.svg
```

Using inkscape or librsvg on my computer look like this:
```
/Applications/Inkscape.app/Contents/Resources/bin/inkscape -f $(pwd)/wordshift.svg -A $(pwd)/wordshift-inkscape.pdf

rsvg-convert --format=eps worshift.svg > wordshift-rsvg.eps
epstopdf wordshift-rsvg.eps
```

And again, feel free to tweet suggestions at [@andyreagan](https://twitter.com/andyreagan), and submit pull requests to the [source code](https://github.com/andyreagan/labMT-simple)!

Full Automation
---------------

I've wrapped up all of this into what is potentially the most backwards way to generate figure imaginable.
The `shiftPDF()` function operates the same way as the `shiftHTML()`, but uses the headless web server to render the d3 graphic, then exectues a piece of injected JS to save a local SVG, and uses command line image manipulation libraries to massage it into a PDF.

On my macbook, this works, but your mileage will most certainly vary.
