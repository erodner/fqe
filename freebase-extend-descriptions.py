import json
import sys
from freebase import freebase
import re
from pprint import pprint


if not len( sys.argv ) == 3: 
  print "Usage: ", sys.argv[0], ": <json-file-with-descriptions> <json-output>"
  sys.exit(-1)

annofile = sys.argv[1]
newannofile = sys.argv[2]


print "Parsing", annofile
with open(annofile) as f:
  annodata = json.load(f)

fb = freebase('AIzaSyCkbwbAezPIYCzhnuw7R4gunA0hMOeRAEE', '(all type:/food/food)')
fb.addIgnoreList ( '../text_embedding/spelling/embedding_vocab.txt' )
fb.addIgnoreList ( '../text_embedding/spelling/imagenet_vocab.txt' )

params = {
  'mode': 'EXPAND_ALL_WORDS',
  'use_only_first_sentence': True
}

#print fb.expandSentence ( 'Wheaties cereals, please', params )

newannodata = {}
for index,imgfile in enumerate(annodata):
  print "== ", imgfile, '%5.2f %%'%(100*index/len(annodata))
  descriptions = annodata[imgfile]
  newannodata[imgfile] = []
  for d in descriptions:
    new_d = fb.expandSentence ( d, params )
    newannodata[imgfile].append ( new_d )

print "Saving everything to", newannofile
with open(newannofile,'w') as fout:
  json.dump ( newannodata, fout, sort_keys=True, indent=4)


