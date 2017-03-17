from flask import Flask, jsonify, request
from nltk.corpus import stopwords
from PyDictionary import PyDictionary
import spelling
import os
import pipeline
import json
import requests
import re

dictionary=PyDictionary()
cachedStopWords = stopwords.words("english")
cachedStopWords.remove('not')
app = Flask(__name__)

def spellingCorrection(text):
  model_answer = " ".join([spelling.correction(item) for item in text['model_answer'].split()])
  answer = " ".join([spelling.correction(item) for item in text['answer'].split()])
  return {"model_answer": model_answer, "answer": answer}

def removeStopWords(text):
  model_answer = re.sub('\W+'," ", text['model_answer'].strip().lower())
  answer = re.sub('\W+'," ", text['answer'].strip().lower())
  formatted_model_answer = " ".join([item for item in model_answer.split() if item not in cachedStopWords])
  formatted_answer = " ".join([item for item in answer.split() if item not in cachedStopWords])
  return {"model_answer": formatted_model_answer, "answer":formatted_answer}

def checkEntities(text):
  model_answer = text['model_answer']
  answer = text['answer']
  func_list = ['spacyExtractor', 'nltkExtractor']
  headers = {'content-type': 'application/json'}
  url = 'http://localhost:5000/pipelineFilter'
  model_answer_entities = json.loads(requests.request("POST", url, data=json.dumps({"texts": [model_answer], "pipeline_list": func_list}), headers=headers).text)
  answer_entities = json.loads(requests.request("POST", url, data=json.dumps({"texts": [answer], "pipeline_list": func_list}), headers=headers).text)
  for model_answer_entity in model_answer_entities['results']:
    if model_answer_entity not in answer_entities['results']:
      if True not in [True for syn in (dictionary.synonym(model_answer_entity)) if(syn in answer)]:
        return {"status": False, "model_answer_entities": model_answer_entities['results'], "answer_entities": answer_entities['results']}
  return {"status": True, "model_answer_entities": model_answer_entities['results'], "answer_entities": answer_entities['results']}

@app.route("/answerCheck",methods=["POST"])
def answerCheck():
  text = request.json
  text = removeStopWords(text)
  text = pipeline.convertSynonyms(text)
  text = spellingCorrection(text)
  result = checkEntities(text)
  return jsonify(result)

# Entity Extractor Pipeline Wrapper.
@app.route('/pipelineFilter', methods=['POST'])
def pipelineFilter():
  try:
    entity_extractor_functions_list = request.json.get('pipeline_list',None)
    results = pipeline.pipelineFilterWrapperV2(request.json, cachedStopWords, entity_extractor_functions_list)
    return jsonify(json.loads(results.get_data().decode('utf8')))
  except Exception as e:
    return jsonify({"error": str(e), "results": []})

if __name__ == "__main__":
  app.run( host="0.0.0.0", debug=True, threaded=True ,use_reloader=True, port=int(os.environ.get('flask_port',5000)) )
