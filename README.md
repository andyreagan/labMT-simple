labMT-simple
============

TL;DR
a simple labMT usage script


a python module for using the labMT1.0 dataset
no dependencies, unless using the plot function
  (then we use matplotlib)

Usage
-----

In python:
```python
  tmpstr = 'a happy sentence'
  from storyLab import microscope
  lens = microscope(0)
  from storyLab import happiness
  happs = happiness(tmpstr,lens)
```
In a shell:
```bash
  alias happiness="$(pwd)/storyLab.py"
  cat storyLab.py | happiness
  storyLab.py happiness
```
