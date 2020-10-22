import json
import os
import falcon
from app.tasks import fib

class CheckStatus(object):

    def on_get(self, req, resp, task_id):           
        taskresult = "Not available" 
        with open("output.txt","r") as file2:
            for line in file2:
                a = line.split()
                if a[0] == task_id:
                    taskresult = line[36:len(line)]
                    break
        result = {'result': taskresult}
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
        with open("output.txt","a") as file1:
            file1.write(task.id + " ")
        resp.body = json.dumps(result)


application = falcon.API()
application.add_route('/create', CreateTask())
application.add_route('/status/{task_id}', CheckStatus())