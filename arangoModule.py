from arango import ArangoClient
import os
import gc
import re
#from services.logFile import infoLog, errorLog, criticalLog
# Initialize the ArangoDB client as root
client = ArangoClient(protocol='http',host=os.environ.get('arango_db','localhost'),port=8529,username=os.environ.get('db_username','root'), password=os.environ.get('db_pass','forward123'))

# infoLog("Arango_db IP value --- %s" %os.environ.get('arango_db','localhost'))
# infoLog("Arango_db USER value --- %s" %os.environ.get('forwardlane_db_username','root'))
# infoLog("Arango_db PASS value --- %s" %os.environ.get('forwardlane_db_pass',''))
db_name = 'it_db' #os.environ['forwardlane_db']
#infoLog("Arango_db DB --- %s" %os.environ.get('forwardlane_db','forwardlane'))

db = client.db("it_db")
try:
  db.properties()
except Exception as e:
  print 'e -->', e
  # db = client.create_database(db_name, username=db_uname, password=db_passwd)

else:
  print "Database Connection Successfull!"

# Retrieve the properties of the new database

# Create another database, this time with a predefined set of users

def add(collectionName , data):
    if data is None:
        return None
    else:
      testcollection = db.collection(collectionName)
    result = testcollection.insert(data)
    gc.collect()
    return result


def get(collectionName, query):
    testcollection = db.collection(collectionName)
    record = testcollection.find(query)
    dataCollection = []
    for student in record:
        dataCollection.append(student)
    if len(dataCollection)<=0:
      return None
    gc.collect()
    return dataCollection


def getMany(collectionName, query):
    testcollection = db.collection(collectionName)

    totalData = []
    for x in query:
      print x
      record = testcollection.find({ "entity" : [x] }) 
      #print record
      if record is not None:
        for r in record:
          #print "entered"
          totalData.append( r )
    '''  
    record = testcollection.find(query)
    dataCollection = []
    for student in record:
        dataCollection.append(student)
    if len(dataCollection)<=0:
      return None
    #print len(dataCollection)
    '''
    if len(totalData)<=0:
      return None
    #print totalData
    gc.collect()
    return totalData

def get_test(collectionName, query):
    # print "get arngod query ->", query
    testcollection = db.collection(collectionName)
    record = testcollection.find(query)
    dataCollection = []
    # print 'record found -->', record
    for student in record:
        dataCollection = student
    if len(dataCollection)<=0:
      return None
    gc.collect()
    return dataCollection

def update(collectionName, data):
  testcollection = db.collection(collectionName)
  gc.collect()
  return testcollection.update(data)

def queryArrayValue(collectionName, text, field):
  cursor = db.aql.execute("FOR a IN "+collectionName+" FILTER '"+text+"' IN a['"+field+"'] RETURN a")
  data = []
  if cursor is not None:
    for r in cursor:
      data.append(r)

  if len(data)<=0:
    return None
  gc.collect()
  return data

def getById(collectionName, id, database=None):
  try:
    testcollection = db.collection(collectionName)
    gc.collect()
    return testcollection.get(id)
  except Exception  as e:
    gc.collect()
    return { "status" : 400 , "message" : str(e) }

def getMultipleIds(collectionName, ids, database=None):
  try:
    dataCollection = db.collection(collectionName)
    result = dataCollection.get_many(ids)
    if len(result)>0:
      gc.collect()
      return result

    return None
  except Exception as e:
    return { "status" : 400 , "message" : str(e) }
