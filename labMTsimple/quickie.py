if __name__ == "__main__":
  import sys
  lang = sys.argv[1]
  import codecs
  f = codecs.open("data/labMTwords-"+lang+".csv","r","utf8")
  tmp = f.read()
  f.close()

  words = tmp.split("\n")

  print len(words)
  print words[0:10]
  print words[9990:10005]

  del(words[-1])

  print len(words)
  print words[0:10]
  print words[9990:10005]

  f = codecs.open("data/labMTscores-"+lang+".csv","r","utf8")
  tmp = f.read()
  f.close()

  scores = tmp.split("\n")

  print len(scores)
  print scores[0:10]
  print scores[9990:10005]

  del(scores[-1])

  print len(scores)
  print scores[0:10]
  print scores[9990:10005]

  f = codecs.open("data/labMT1"+lang+".txt","w","utf8")
  f.write(words[0])
  f.write("\t")
  f.write("0")
  f.write("\t")
  f.write(scores[0])
  for i in xrange(1,len(scores)):
    f.write("\n")
    f.write(words[i])
    f.write("\t")
    f.write(str(i))
    f.write("\t")
    f.write(scores[i])
  f.write("\n")
  f.close()
