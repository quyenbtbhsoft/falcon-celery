file1 = open("output.txt","r")
for line in file1:
    print(line[0:36])
file1.close()                    