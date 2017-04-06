from flask import Flask, jsonify, request,render_template
from nltk.corpus import stopwords
from PyDictionary import PyDictionary
import spelling
import os
import pipeline
import json
import requests
import re
import difflib

dictionary=PyDictionary()
cachedStopWords = stopwords.words("english")
cachedStopWords.remove('not')
app = Flask(__name__)
ques_mark_word=["how","when","what","where","why"]


#below commented code is written for answer checking by mohit
# def spellingCorrection(text):
#   model_answer = " ".join([spelling.correction(item) for item in text['model_answer'].split()])
#   answer = " ".join([spelling.correction(item) for item in text['answer'].split()])
#   return {"model_answer": model_answer, "answer": answer}

# def removeStopWords(text):
#   model_answer = re.sub('\W+'," ", text['model_answer'].strip().lower())
#   answer = re.sub('\W+'," ", text['answer'].strip().lower())
#   formatted_model_answer = " ".join([item for item in model_answer.split() if item not in cachedStopWords])
#   formatted_answer = " ".join([item for item in answer.split() if item not in cachedStopWords])
#   return {"model_answer": formatted_model_answer, "answer":formatted_answer}

# def checkEntities(text):
#   model_answer = text['model_answer']
#   answer = text['answer']
#   func_list = ['spacyExtractor', 'nltkExtractor']
#   headers = {'content-type': 'application/json'}
#   url = 'http://localhost:5000/pipelineFilter'
#   model_answer_entities = json.loads(requests.request("POST", url, data=json.dumps({"texts": [model_answer], "pipeline_list": func_list}), headers=headers).text)
#   answer_entities = json.loads(requests.request("POST", url, data=json.dumps({"texts": [answer], "pipeline_list": func_list}), headers=headers).text)
#   for model_answer_entity in model_answer_entities['results']:
#     if model_answer_entity not in answer_entities['results']:
#       if True not in [True for syn in (dictionary.synonym(model_answer_entity)) if(syn in answer)]:
#         return {"status": False, "model_answer_entities": model_answer_entities['results'], "answer_entities": answer_entities['results']}
#   return {"status": True, "model_answer_entities": model_answer_entities['results'], "answer_entities": answer_entities['results']}

# @app.route("/answerCheck",methods=["POST"])
# def answerCheck():
#   text = request.json
#   text = removeStopWords(text)
#   text = pipeline.convertSynonyms(text)
#   text = spellingCorrection(text)
#   result = checkEntities(text)
#   return jsonify(result)


# def spellingCorrectionques(text):
#   question = " ".join([spelling.correction(item) for item in text['question'].split()])
#   return {"question": question}


# to remove stopwords from user query
def removeStopWordsques(text):
  question = re.sub('\W+'," ", text['question'].strip().lower())
  question = " ".join([item for item in question.split() if item not in cachedStopWords])
  return {"question": question}

#function used to preform query related task and generate response
def chatResponse(text,userquery):
  question = text['question']
  count=[]
  resulted_entity=[]
  func_list = ['spacyExtractor', 'nltkExtractor']
  headers = {'content-type': 'application/json'}
  url = 'http://localhost:8000/pipelineFilter'
  entities = json.loads(requests.request("POST", url, data=json.dumps({"texts": [question], "pipeline_list": func_list}), headers=headers).text)
  ques_text= userquery.split(" ")
  # below code adding question mark word like what,how to entity list
  for i in ques_mark_word: 
    if i in ques_text:
      k=entities['results']
      k.append(i)
      entities['results']=k

  #here we are fetching data from database and matching user query with fetched data based on entity matched count
  # also here we are calculating matched text score of user query with fetched data
  import arangoModule
  db=arangoModule.db
  result=list(db.aql.execute("for u in it_ques_ans return u"))
  for ques in result:
    count=[]
    for entity in entities['results']:
      if entity in ques['ques_entities']:
        count.append(entity)
    temp=" ".join(count)
    score=difflib.SequenceMatcher(None, temp.lower(), userquery.lower()).ratio()# for creating a matched score of userquery with fetched data
    res={"usr_ques_extarcted_entity":entities['results'],"matched_entity":count,"count":len(count),"ques_key":ques['_key'],"entity_in_ques":ques['ques_entities'],"question":ques['question'],"score":score,"answer":ques['answer']}
    resulted_entity.append(res)
  # sorting the data based on count value
  resulted_entity = sorted(resulted_entity , key=lambda k: k['count'] , reverse=True )

  # result after performing all  above task
  if resulted_entity[0]['count']>0:
    return {"status": True,"result":resulted_entity[0]}
  else:
    resulted_entity[0]['answer']="data not matched"
    return {"status": False,"result":resulted_entity[0]}


#TO generate output of userquery 
@app.route("/matchquestion",methods=["POST"])
def matchQuestion():
  "input: what is income tax?"
  #input sholud be a simple line of stirng
  text = request.json
  print 'text', text
  text1={"question":text}
  text = removeStopWordsques(text1)
  text = pipeline.convertSynonyms({"answer":text['question']})
  #text = spellingCorrectionques({"question":text['answer']})
  result = chatResponse({"question":text['answer']},text1['question'])
  return jsonify(result)




# Entity Extractor Pipeline Wrapper API.
# here we are extracing entities from user query
@app.route('/pipelineFilter', methods=['POST'])
def pipelineFilter():
  try:
    entity_extractor_functions_list = request.json.get('pipeline_list',None)
    results = pipeline.pipelineFilterWrapperV2(request.json, cachedStopWords, entity_extractor_functions_list)
    results=json.loads(results.get_data().decode('utf8'))
    text=request.json['texts']
    text1=text[0].split(" ")
    for i in ques_mark_word:
      if i in text1:
        k=results['results']
        k.append(i)
        results['results']=k
    return jsonify(results)
  except Exception as e:
    return jsonify({"error": str(e), "results": []})

#route to show chat on web
@app.route('/chat')
def webprint():
    return render_template('chat.html') 


if __name__ == "__main__":
  app.run( host="0.0.0.0", debug=True, threaded=True ,use_reloader=True, port=int(os.environ.get('flask_port',8000)) )
