import json
import sys
from freebase import freebase
import re
from pprint import pprint
import flexconfig

parser = flexconfig.get_parser('~/.freebase_config')
parser.add_argument('--apikey')
parser.add_argument('--filter')
parser.add_argument('--srcannotations', required=True)
parser.add_argument('--dstannotations', required=True)

args = parser.parse_args()

annofile = args.srcannotations
newannofile = args.dstannotations


print "Parsing", annofile
with open(annofile) as f:
  annodata = json.load(f)

fb = freebase(args.apikey, args.filter)
fb.addIgnoreList ( 'embedding_vocab.txt' )
fb.addIgnoreList ( 'imagenet_vocab.txt' )

params = {
  #'mode': 'EXPAND_ALL_WORDS',
  'mode': 'EXPAND_NOUN_GROUPS',
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


