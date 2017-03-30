import os  
from collections import defaultdict
import csv,json
import arangoModule
import requests

csvfile = open('ITFinal.csv', 'rU')
fieldnames = ("name")
fieldnames = ("count","question","answer")
ignored = []
reader = csv.DictReader(csvfile, fieldnames)
for row in reader:
    print row
    func_list = ['spacyExtractor', 'nltkExtractor']
    headers = {'content-type': 'application/json'}
    url = 'http://localhost:5000/pipelineFilter'
    ques_entities = json.loads(requests.request("POST", url, data=json.dumps({"texts": [row['question']], "pipeline_list": func_list}), headers=headers).text)
    print ques_entities
    attribs={"question":row['question'],"answer":row['answer'],"ques_entities":ques_entities['results']}
    res=arangoModule.add("it_ques_ans",attribs)['_key']

   

