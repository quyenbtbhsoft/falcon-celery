from time import sleep
import os
import celery
from pymongo import MongoClient

client = MongoClient("mongodb+srv://guest:guest@fibonacci.clxiv.mongodb.net/fibonacci?retryWrites=true&w=majority")

app = celery.Celery('tasks', broker='amqp://guest:guest@localhost:5672')

@app.task(bind = True)
def fib(self,n):
    results = [1,1]
    if n < 0:
        results = []
    elif n == 0:
        results =[0]
    elif n == 1:
        results =[1]
    elif n == 2:
        results =[1,1]    
    else:
        for i in range(n-2):
            results.append(results[len(results)-1] + results[len(results)-2])
    
    str1 = "[ " 
    for i in results:
        str1 += str(i) + " "
    str1 += "]" + os.linesep

    with open("output.txt","a+") as file1:   	
        file1.write(str(self.request.id)+" ")
        file1.write(str1)
    
    db = client.test
    db.inventory.insert_one(
        {
            "ID": "Is",
            "result": str1,
        }
    )
    
    return results  