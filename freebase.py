import json
import urllib
import re
import nltk
import multireplace

class freebase:

  
  def __init__(self, apikey, defaultfilter):
    ''' Contructor for the freebase class: set up API key and default type filter options '''
    self.apikey = apikey 
    self.defaultfilter = defaultfilter
    
    # some pre-defined URL's
    self.service_search_url = 'https://www.googleapis.com/freebase/v1/search'
    self.service_topic_url = 'https://www.googleapis.com/freebase/v1/topic'

    self.ignoreList = set()

  def addIgnoreList ( self, ignorelistfn ):
    ''' Add a list (filename) of words that will be ignored for the expanding operations '''
    with open(ignorelistfn) as f:
      for line in f:
        self.ignoreList.add ( line.rstrip().lower() )
    print 'Length of the ignore list is', len(self.ignoreList)

  def set_default_params ( self, params ):
    if not 'mode' in params:
      params['mode'] = 'EXPAND_EVERY_WORD'
    if not 'use_only_first_sentence' in params:
      params['use_only_first_sentence'] = False
    return params

  def expandAllWords ( self, s, params ):
    """ Expand all out-of-vocabulary words """
    newsentence = ""

    search_response = self.query ( s, self.defaultfilter )
    if not search_response < 0:
      d = self.obtainDescription ( search_response, params['use_only_first_sentence'] );
      if len(d)>0:
        newsentence = "( " + d + " )";

    words = re.findall( '\w+', s )
    for word in words:
      d = word
      if not word in self.ignoreList:
        print "Searching for", word
        search_response = self.query ( word, self.defaultfilter )
        if not search_response < 0:
          desc = self.obtainDescription ( search_response, params['use_only_first_sentence'] );
          if len(desc)>0:
            d = "( " + word + " : " + desc + " )"
        else:
          print "Unable to find", word
      else:
        print "Ignoring", word
     
      if len(newsentence) > 0:
        newsentence = newsentence + " " + d
      else:
        newsentence = d
    
    return newsentence


  def getNounGroups ( self, s ):
    tokens = nltk.word_tokenize(s)
    tagged_tokens = nltk.pos_tag( tokens )
    grammar = "NP: {(<NN>|<NNP>)+}"
    cp = nltk.RegexpParser(grammar)
    parsed_sentence = cp.parse(tagged_tokens)

    noungroups = []
    for e in parsed_sentence:
      if not isinstance(e,tuple):
        terms = []
        for term in e:
          terms.append( term[0] )
        
        noungroup = ' '.join(terms)
        noungroups.append( noungroup )

    return noungroups

  def expandNounGroups ( self, s, params ):
    ''' Expand only groups of nouns with freebase descriptions '''

    noungroups = self.getNounGroups ( s )
   
    print "Noun groups:", ';'.join(noungroups)

    # obtain freebase descriptions for each noungroup if available 
    rep_hash = {}
    for noungroup in noungroups:
      if not noungroup in self.ignoreList:
        print "Trying to expand noun group", noungroup
        search_response = self.query ( noungroup, self.defaultfilter )
        if not search_response < 0:
          desc = self.obtainDescription ( search_response, params['use_only_first_sentence'] );
          if len(desc)>0:
            d = "( " + noungroup + " : " + desc + " )"
            rep_hash[noungroup] = d
    
    if len(rep_hash)>0:
      print rep_hash
      newsentence = multireplace.mreplace ( s, rep_hash )
    else:
      newsentence = s

    return newsentence
    

  def expandSentence ( self, sentence, params ): 
    ''' Expand words in the sentence with freebase descriptions when available '''
    
    print "Processing:", sentence
    s = sentence.lower()

    params = self.set_default_params( params )

    # Method EXPAND_ALL_WORDS: expand all out-of-vocabulary words
    if params['mode'] == 'EXPAND_ALL_WORDS':
      newsentence = self.expandAllWords ( s, params )
    # Method EXPAND_NOUN_GROUPS: expand all noun groups
    elif params['mode'] == 'EXPAND_NOUN_GROUPS':
      newsentence = self.expandNounGroups ( s, params ) 
    else:
      print "Mode unknown:", params['mode']
      return ""

    print "Output:", newsentence
    
    return newsentence



  def query ( self, querystring, filterstring ):
    ''' Perform a freebase query with a given query string and filter '''
    params = {
      'query': querystring,
      'filter': filterstring,
      'limit': 20,
      'key': self.apikey
    }
    
    url = self.service_search_url + '?' + urllib.urlencode(params)
    search_response = json.loads(urllib.urlopen(url).read())
        
        
    if 'error' in search_response:
      print "# Freebase error:", search_response['error']
      return -1

    if (len(search_response['result']) == 0):
      return -1

    return search_response



  def obtainDescription (self, search_response, use_only_first_sentence):
    ''' Obtain a description for a search response '''

    description = ""
    found_description = False
    k = 0

    while not found_description:
      if k >= len(search_response['result']):
        break

      firstresult = search_response['result'][k];
      freebase_id=firstresult['mid'];

      params = {
        'key': self.apikey
      }

      url_topic = self.service_topic_url + freebase_id + '?' + urllib.urlencode(params);
      response = json.loads(urllib.urlopen(url_topic).read())
     
      if 'error' in response:
        print "# Freebase error:", response['error']
        return description

      if not 'property' in response:
        break

      p = response['property']

      if '/common/topic/description' in p:
        descriptions = p['/common/topic/description']
        for i, desc in enumerate(descriptions['values']):
          description = desc['value'].encode("ASCII", 'ignore')
          found_description = True
      k = k + 1

    if use_only_first_sentence:
      m = re.search ('^[^\.]+', description)
      if m:
        description = m.group()

    return description
