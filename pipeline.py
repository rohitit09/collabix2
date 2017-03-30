import nltk
from spacy.en import English
# import inflection
from textblob import TextBlob
from flask import Flask, jsonify
import re
import gc
import enchant
from nltk.corpus import stopwords
from multiprocessing import Queue
import threading
#from services.logFile import infoLog, errorLog

parser = English()
app = Flask(__name__)
enchant_obj = enchant.Dict("en_US")
cachedStopWords = stopwords.words("english")
cachedStopWords.remove('not')

def nltkExtractor(query, callback=None):
    # print "threading nltk extractor.",query
    nouns_list = []
    try:
        for sentence in query['texts']:
            sentence = sentence.replace(".", " ")

            tokens = nltk.word_tokenize(sentence)
            tagged = nltk.pos_tag(tokens)
            del tokens
            for tag in tagged:
                print (tag(0))
                print (tag(1))
                if tag[1] == 'NN' or tag[1] == 'NNP' or tag[1] == 'VB' or tag[1] == 'VBP' or tag[1] == 'VBD' or tag[1] == 'VBG' or tag[1] == 'VBN' or tag[1] == 'VBZ':
                    if tag[0].lower() not in nouns_list and tag[0].lower() not in cachedStopWords:
                        if re.match("^[a-zA-Z0-9_]*$", tag[0].lower()[0]):
                            word = tag[0].lower()
                            if word[-1] == '/':
                                word = word[:-1]
                            nouns_list.append(word)
        if callback is None:
            gc.collect()
            #infoLog("nltkExtractor == %s" %nouns_list)
            return jsonify({"entities": nouns_list})
        gc.collect()
        callback.put( { "entities" : nouns_list, "function": "nltkExtractor"  } )

    except:
        if callback is None:
            gc.collect()
            return jsonify({"entities": nouns_list})

        gc.collect()
        callback.put( { "entities" : nouns_list, "function": "nltkExtractor" } )        


def textBlobExtractor(query, callback=None):
    nouns_list = []
    try:
        for sentence in query['texts']:
            sentence = sentence.replace(".", " ")

            text = TextBlob(sentence)
            phrase_text = text.noun_phrases
            del text
            for noun_phrase in phrase_text:
                # noun_phrase = inflection.singularize(noun_phrase)
                if not re.match("^[a-zA-Z0-9_]*$", noun_phrase.lower()[-1]):  # Removing special chars from last
                    noun_phrase = noun_phrase[:-1]
                if re.match("^[a-zA-Z0-9_]*$", noun_phrase.lower()[0]):
                    if noun_phrase.lower() not in nouns_list and noun_phrase.lower() not in cachedStopWords:
                        noun_phrase = noun_phrase.lower()
                        noun_phrase_list = noun_phrase.split()
                        phrase_list = []
                        for phrase in noun_phrase_list:
                            if phrase[-2] == ' ':
                                phrase = phrase[:(len(phrase) - 2)] + phrase[(len(phrase) - 1):]  # fixing words like 'king s'
                            if phrase[-1] == '/':
                                phrase = phrase[:-1]

                            if phrase[0] == '$' and re.match("^[0-9]*$", phrase[1]):  # removing entities like '$400'
                                if ' ' in phrase:
                                    i = phrase.index(' ')
                                    if not re.match("^[a-zA-Z]*$", phrase[i + 1]):  # allowing entities like '$400 rupees'
                                        continue
                                else:
                                    continue
                            if not re.match("^[a-zA-Z-Z0-9_$]*$", phrase[0]):
                                continue
                            phrase_list.append(phrase)
                        noun_phrase = " ".join(phrase_list)
                        del phrase_list
                        nouns_list.append(noun_phrase)

        if callback is None:
            gc.collect()
            #infoLog("textBlobExtractor == %s" %nouns_list)
            return jsonify({"entities": nouns_list})
        gc.collect()
        callback.put( { "entities" : nouns_list, "function": "textBlobExtractor"  } )

    except:
        if callback is None:
            gc.collect()
            return jsonify({"entities": nouns_list})
        gc.collect()
        callback.put( { "entities" : nouns_list, "function": "textBlobExtractor"  } )


def spacyExtractor(query,callback=None):
    entities_list, location, organisation, person, date = [], [], [], [], []
    try:
        for text in query['texts']:
            nlp_obj = parser(text)
            for entity in list(nlp_obj.ents):
                if entity.label_ == "GPE":
                    location.append(str(entity))
                if entity.label_ == "ORG":
                    organisation.append(str(entity))
                elif entity.label_ == "PERSON":
                    person.append(str(entity))
                elif entity.label_ == "DATE":
                    date.append(str(entity))
                else:
                    pass

                if str(entity) not in entities_list:
                    entities_list.append(str(entity))
            new = []
            for token in nlp_obj:
                print ("token-",str(token))
                print ("pos",token.pos_)
                new.append({"token.pos_": token.pos_, "token": str(token)})
                if token.pos_ == 'PROPN' or token.pos_ == 'NOUN' or token.pos_ == 'VERB':
                    token = str(token)
                    if token not in entities_list:
                        entities_list.append((str(token)).lower())
        if callback is None:
            gc.collect()
            #infoLog("spacyExtractor == %s" %entities_list)
            return jsonify({"entities": entities_list, "location": location, "organisation": organisation, "person": person, "date": date})
        gc.collect()
        callback.put( { "entities" : entities_list, "function": "spacyExtractor" , "location": location, "organisation": organisation, "person": person, "date": date   } )
    except Exception as e:
        #errorLog("Error while extracting entities in spacyExtractor from pipline, error --> %s" %str(e))
        if callback is None:
            gc.collect()
            return jsonify({"entities": entities_list, "location": location, "organisation": organisation, "person": person, "date": date})
        gc.collect()
        callback.put( { "entities" : entities_list, "function": "spacyExtractor", "location": location, "organisation": organisation, "person": person, "date": date   } )

# This function calls all the entity extractor functions(In Parallel) and returns the combined results.
def pipelineFilterWrapperV2(request, stop, entity_extractor_functions_list=None):
  """Sample Input.

  {"texts":["Facebook added about $335.34B billion"]}
  """
  gc.collect()
  if entity_extractor_functions_list is None:
    task_list = [nltkExtractor, textBlobExtractor, spacyExtractor]
  else:
    task_list = []
    for item in entity_extractor_functions_list:
      if item == 'nltkExtractor':
        task_list.append(nltkExtractor)
      elif item == 'textBlobExtractor':
        task_list.append(textBlobExtractor)
      elif item == 'spacyExtractor':
        task_list.append(spacyExtractor)
      else:
        pass

  max_task = len(task_list)
  callback = [ Queue() ] * max_task
  pipe_list = []
  appendRef = pipe_list.append

  payload = request
  if type([]) != type(payload['texts']):
    payload['texts'] = [payload['texts']]

  for x in range( max_task ):
    appendRef(   threading.Thread(target=task_list[x] , args=( payload , callback[x] ) ) )
  
  for x in pipe_list:
    x.start()

  for x in pipe_list:
    x.join()

  results, date, organisation, location, person = [], [], [], [], []
  try:
    for x in callback:
      entities = x.get()
      entity_keys = ['date', 'entities', 'organisation', 'location', 'person']
      for entity_key in entity_keys:
        entities_data = entities.get(entity_key,[])

        for entity in entities_data:
          if len(entity) > 1:
            if not re.match("^[a-zA-Z0-9_]*$", entity.lower()[-1]):  # Removing special chars from last
              entity = entity[:-1]

            if not re.match("^[a-zA-Z0-9_#]*$", entity.lower()[0]):  # removing entities like '$400' or '+9'
              if ' ' in entity:
                i = entity.index(' ')
                if not re.match("^[a-zA-Z]*$", entity[i + 1]):  # allowing entities like '$400 rupees'
                  continue
              else:
                continue
            if entity.lower() not in stop and entity not in stop:
              if entity_key == "entities":
                  results.append((str(entity)).lower())
              elif entity_key == "date":
                  date.append((str(entity)).lower())
              elif entity_key == "organisation":
                  organisation.append((str(entity)).lower())
              elif entity_key == "location":
                  location.append((str(entity)).lower())
              elif entity_key == "person":
                  person.append((str(entity)).lower())
              else:
                pass
      del entities

    results, date, organisation, location, person = set(results), set(date), set(organisation), set(location), set(person)
    results, date, organisation, location, person = list(results), list(date), list(organisation), list(location), list(person)

    gc.collect()
    return jsonify({"results": results, "date": date, "organisation": organisation, "location": location, "person": person})
  except:
    gc.collect()
    return jsonify({"results": results})

def convertSynonyms(text):
    answer = text['answer']
    converted_answer = answer
    nlp_obj = parser(answer)
    for token in nlp_obj:
        if token.pos_ == 'PROPN' or token.pos_ == 'NOUN':
            converted_answer = converted_answer.replace(str(token),nltk.stem.WordNetLemmatizer().lemmatize(str(token),'n'))
        elif token.pos_ == 'VERB':
            converted_answer = converted_answer.replace(str(token),nltk.stem.WordNetLemmatizer().lemmatize(str(token),'v'))
            token = str(token)
    text['answer'] = converted_answer
    return text
