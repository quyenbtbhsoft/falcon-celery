import json
import os
import falcon
from app.tasks import fib
from pymongo import MongoClient

client = MongoClient("mongodb+srv://guest:guest@fibonacci.clxiv.mongodb.net/fibonacci?retryWrites=true&w=majority")

class CheckStatus(object):

    def on_get(self, req, resp, task_id):           
        taskresult = "Not available" 
        with open("output.txt","r") as file2:
            for line in file2:
                a = line[:36]
                print(a)
                print(task_id)
                if a == task_id:
                    taskresult = line[36:len(line)]
                    break
        result = {'result': taskresult[0:len(taskresult)-1]}
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(result)

class CreateTask(object):

    def on_post(self, req, resp):
        raw_json = req.stream.read()
        result = json.loads(raw_json, encoding='utf-8')
        task = fib.delay(int(result['number']))
        resp.status = falcon.HTTP_200
        result = {
           'task_id': task.id
            }
        resp.body = json.dumps(result)
    

class SignUp(object):
    def on_post(self, req, resp):
        db = client.test
        raw_json = req.stream.read()
        result = json.loads(raw_json,encoding='utf-8')
        col = db.login
        myquery = {"ID":result['id']}
        doc = col.find(myquery)
        if doc is None:
            db.login.insert_one(
            {
            "ID": result['id'],
            "password": result['password'],
            }
            )
        else:
            resp.body = json.dump("Already exist")    

class LogIn(object):
    def on_get(self,req,resp,id,password):
        db = client.test
        col = db.login
        myquery = {"ID":id}
        doc = col.find(myquery)
        if doc["password"] == password:
            resp.body = json.dumps("Success")
        else:
            resp.body = json.dumps("Something wrong") 

application = falcon.API()
application.add_route('/create', CreateTask())
application.add_route('/status/{task_id}', CheckStatus())
application.add_route('/login/{id}/{password}',SignUp())
application.add_route('/signup', SignUp())