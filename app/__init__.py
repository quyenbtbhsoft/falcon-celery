import json
import os
import falcon
from app.tasks import fib
from pymongo import MongoClient
#from falcon_auth import FalconAuthMiddleware, BasicAuthBackend
#from core.utils import json_serializer

client = MongoClient("mongodb+srv://guest:guest@fibonacci.clxiv.mongodb.net/fibonacci?retryWrites=true&w=majority")

#user_loader = lambda username, password: {'username':username}
#auth_backend = BasicAuthBackend(user_loader)
#auth_middleware = FalconAuthMiddleware(auth_backend,exempt_routes=['/exempt'],exempt_method=['HEAD'])
#application = falcon.API(middleware=[auth_middleware,JSONTranslator()])

class CheckStatus(object):

    def on_get(self, req, resp, task_id):           
        taskresult = "Not available" 
        with open("output.txt","r") as file2:
            for line in file2:
                a = line[:36]
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
    
    def on_post(self, req, resp,username,password):
        db = client.test
        col = db.login
        filtered_dict = {"username":username}
        if col.count_documents(filtered_dict):
            resp.body = json.dump("Already exist")
        else:
            db.login.insert_one(
                {
                    "username": username,
                    "password": password,
                }
            )   

class LogIn(object):
    
    def on_get(self,req,resp,username,password):
        db = client.test
        col = db.login
        filtered_dict = {"username":username}
        if col.count_documents(filtered_dict):
            mydoc = col.find(filtered_dict)
            for x in mydoc:
                if x["password"] == password:    
                    resp.body = json.dumps("Success")
                else:
                    resp.body = json.dumps("Failed")                
        else:
            resp.body = json.dumps("Something wrong") 

class JSONTranslator():
    def process_request(self, re, resp):
        if req.content_length in (None,0):
            return     
        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest(
                "Empty request body. A valid JSON document is required."
            )
        try:
            req.context['request'] = json.loads(body.decode('utf-8'))
        except (ValueError,UnicodeDecodeError):
            raise falcon.HTTPError(
                falcon.HTTP_753,
                'Malformed JSON. Could not decode the request body.'
                'The JSON was incorrect or not encoded as UTF-8'
            )
    def process_response(self, req, resp):
        if 'response' not in resp.context:
            return

        resp.body = json.dumps(
            resp.context['response'],
            default = json_serializer
        )            


application = falcon.API()

application.add_route('/create', CreateTask())
application.add_route('/status/{task_id}', CheckStatus())
application.add_route('/login/{username}/{password}',LogIn())
application.add_route('/signup/{username}/{password}', SignUp())