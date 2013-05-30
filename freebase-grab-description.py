import json
import urllib
import sys
import re

query = sys.argv[1]

API_KEY = 'AIzaSyCkbwbAezPIYCzhnuw7R4gunA0hMOeRAEE'
service_search_url = 'https://www.googleapis.com/freebase/v1/search'
params = {
  'query': query,
  'filter': '(all type:/food/food)',
  'limit': 20,
#  'indent': true,
  'key': API_KEY
}
url = service_search_url + '?' + urllib.urlencode(params)
search_response = json.loads(urllib.urlopen(url).read())

if (len(search_response['result']) == 0):
  print "Error: phrase <", query, "> not found in freebase"
  exit(-1)

found_description = False
k = 0
while not found_description:
  if k >= len(search_response['result']):
    print "Error: phrase <", query, "> has no description in freebase"
    break


  firstresult = search_response['result'][k];
  freebase_id=firstresult['mid'];

  url_topic = 'https://www.googleapis.com/freebase/v1/topic' + freebase_id;
  response = json.loads(urllib.urlopen(url_topic).read())
  p = response['property']

  if '/common/topic/description' in p:
    descriptions = p['/common/topic/description']
    for i, desc in enumerate(descriptions['values']):
      print desc['value'].encode("ASCII", 'ignore')
      found_description = True

  k = k + 1
