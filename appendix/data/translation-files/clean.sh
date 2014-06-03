for REF in Arabic Chinese English French German Indonesian Korean Portuguese Russian Spanish
do 
    for COMP in Arabic Chinese English French German Indonesian Korean Portuguese Russian Spanish
    do 
	wget http://www.uvm.edu/~eclark/TranslationAppendixCharts/TransValChart_${REF}_${COMP}.txt
    done
done

perl -i -pe 's/ \],//g' *.txt

perl -i -pe 's/\[ //g' *.txt

for REF in Arabic Chinese English French German Indonesian Korean Portuguese Russian Spanish
do 
    for COMP in Arabic Chinese English French German Indonesian Korean Portuguese Russian Spanish
    do 
	sed -ie '1d' TransValChart_${REF}_${COMP}.txt
    done
done

