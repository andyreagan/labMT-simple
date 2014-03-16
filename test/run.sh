python test.py 18.01.14.txt 21.01.14.txt
echo "launching local python server..."
python -m SimpleHTTPServer 8888 &
sleep 3
open http://localhost:8888/shiftPlot.html

