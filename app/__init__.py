import json
import os
import falcon
import jwt
from app.tasks import fib
from pymongo import MongoClient
from falcon_auth import FalconAuthMiddleware, JWTAuthBackend
from datetime import datetime, timedelta

client = MongoClient("mongodb+srv://guest:guest@fibonacci.clxiv.mongodb.net/fibonacci?retryWrites=true&w=majority")

def user_loader(payload):
    print(payload)
    search_dict = payload['user']
    db = client.test
    col = db.login
    if col.count_documents(search_dict):
        return payload['user']   
    else:
        return None    

auth_backend = JWTAuthBackend(user_loader,'secret')
auth_middleware = FalconAuthMiddleware(auth_backend)

class SignUp(object):    
    auth = {
            'auth_disabled':True
        }
    def on_post(self, req, resp,username,password):      
        db = client.test
        col = db.login
        filtered_dict = {"username":username}
        if col.count_documents(filtered_dict): 
            resp.body = json.dumps("Already exist")
        else:
            db.login.insert_one(
                {
                    "username": username,
                    "password": password,
                }
            )
            resp.body = json.dumps("Success") 

class LogIn(object):
    auth = {
            'auth_disabled':True
        }
    def on_post(self,req,resp,username,password):    
        db = client.test
        col = db.login
        filtered_dict = {"username":username}
        mydoc = col.find(filtered_dict)
        if mydoc:
            for x in mydoc:
                if x["password"] == password:     
                    payload = {
                        'username':username,
                    }
                    token = auth_backend.get_auth_token(payload)
                    resp.body = token 
                else:
                    resp.body = json.dumps("Failed")                
        else:
            resp.body = json.dumps("Something wrong")     


class CheckStatus(object):
        
    def on_get(self, req, resp, task_id):   
        taskresult = "Not available" 
        with open("output.txt","r") as file2:
            for line in file2:
                a = line[:36]
                if a == task_id:
                    taskresult = line[36:len(line)]
                    break
        result = {'result': taskresult[0:len(taskresult)]}
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

app = application = falcon.API(middleware=[auth_middleware])
application.add_route('/create', CreateTask())
application.add_route('/status/{task_id}', CheckStatus())
application.add_route('/login/{username}/{password}',LogIn())
application.add_route('/signup/{username}/{password}', SignUp())