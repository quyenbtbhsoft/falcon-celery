from time import sleep
import os
import celery

app = celery.Celery('tasks', broker='amqp://guest:guest@localhost:5672')

@app.task
def fib(n):
    results = [0,1]
    if n < 0:
        results = []
    elif n == 0:
        results =[0]
    elif n == 1:
        results =[0, 1]
    else:
        for i in range(n-1):
            results.append(results[len(results)-1] + results[len(results)-2])

    with open("output.txt","a") as file1:   	
        file1.write("[")
        for i in range(len(results)):
            file1.write(str(results[i]) + " ")
        file1.write(str(result[len(result)]))    
        file1.write("]"+os.linesep)
        file1.write(os.linesep)
    
    return results  