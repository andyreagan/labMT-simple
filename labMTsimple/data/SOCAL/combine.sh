cat google_dict.txt adj_dictionary1.11.txt adv_dictionary1.11.txt int_dictionary1.11.txt noun_dictionary1.11.txt verb_dictionary1.11.txt > all_dictionaries.txt

iconv -f iso-8859-1 -t utf-8 all_dictionaries.txt > all_dictionaries-utf8.txt
