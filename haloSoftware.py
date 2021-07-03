#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 20 00:14:59 2021

@author: kiymet
"""
import pandas as pd
import os
import time
from typing import Counter

inputFile = "input.txt"
outputFile = "output.txt"
user = None
loggedIn = True
success = True

pagecount=8
linecount=12
fieldcount=12


def register(username, pw1, pw2):
    global success
    df = pd.read_csv("users.csv")
    if username in df["username"].values or pw1!=pw2:
        success = False
    else:
        user = {"username":[username], "password":[pw1]}
        data = pd.DataFrame(data=user)
        data.to_csv("users.csv", mode='a', index=False, header=False)
        success = True
          
def login(username, password):
    global success
    global user
    user = None 
    success = False
    df = pd.read_csv("users.csv")
    if username in df["username"].values:
        users = pd.read_csv("users.csv", index_col = "username")
        pw = users.loc[username].get("password")
        if pw == password:
            user = username
            success = True
            
def logout():
    global loggedIn
    global success
    global userlog
    global user
    if not loggedIn:
        success = False
    else:
        userlog=user
        user = None  
        loggedIn = False
        success = True
    
def createEmptyFile(filename):
    with open(filename, 'w') as f:
        for i in range(1,9):
            f.write("1,"+str(i)+",$,$,$,$,$,$,$,$,$,$,$\n")
            for j in range(11):
                if i==8 and j==10:
                    f.write(",,,,,,,,,,,")
                else:
                    f.write(",,,,,,,,,,,\n")
                
def createNewFile(typename):
    df = pd.read_csv("SystemCatalogue.csv", index_col="type") #get type info
    filenum = df.loc[typename].get("filenum")
    files = df.loc[typename].get("files")
    
    #create file
    filename = typename+str(filenum)+".txt"
    createEmptyFile(filename)
    
    df.loc[typename, "filenum"] =filenum + 1                #update system catalog
    df.loc[typename, "files"] = files + " " + filename
    df.to_csv("SystemCatalogue.csv")
    
def deleteLastFile(typename):
    df = pd.read_csv("SystemCatalogue.csv", index_col="type") #get file names
    files = df.loc[typename].get("files")
    filelist = files.split()
    filenum = df.loc[typename].get("filenum")
    
    filename = filelist[-1]             #delete file
    os.remove(filename)
    
    df.loc[typename, "filenum"] =filenum - 1                #update system catalog
    df.loc[typename, "files"] = " ".join(filelist[:-1])
    df.to_csv("SystemCatalogue.csv")
    
    
def createSystemFiles():
    col = pd.DataFrame(columns=["type","filenum","files","fieldnum","fields"])
    col.to_csv("SystemCatalogue.csv", index=False)
    
    col = pd.DataFrame(columns=["username","occurrence","operation","status"])
    col.to_csv("haloLog.csv", index=False)
    
    col = pd.DataFrame(columns=["username","password"])
    col.to_csv("users.csv", index=False)
   
def createType(operation):
    global success
    typename = operation[0]
    df = pd.read_csv("SystemCatalogue.csv")
    types = df["type"].tolist()
    if typename in types:
        success = False
    else:
        fieldnum = int(operation[1])+2
        fields = ["planet", "id"]+operation[2:]
        newType = {"type":[typename],"filenum":[1],"files":[typename+"0.txt"],"fieldnum":[fieldnum],"fields":[" ".join(fields)]}
        data = pd.DataFrame(data=newType)
        data.to_csv("SystemCatalogue.csv", mode='a', index=False, header=False)
        df = pd.read_csv("SystemCatalogue.csv", index_col="type")    #sort
        df.sort_index(inplace=True)
        df.to_csv("SystemCatalogue.csv")
        filename = typename+"0.txt"
        createEmptyFile(filename)
        success = True
    
def inheritType(operation):
    global success
    newType = operation[0]
    oldType = operation[1]
    df = pd.read_csv("SystemCatalogue.csv")
    types = df["type"].tolist()
    if newType in types or oldType not in types:
        success = False
    else:
        newFields = operation[2:]
        df = pd.read_csv("SystemCatalogue.csv", index_col="type")
        fields = df.loc[oldType].get("fields").split()[2:]
        fieldnum = df.loc[oldType].get("fieldnum")-2 + len(newFields)
        createType([newType]+[fieldnum]+fields+newFields)
        success = True
    
def deleteType(typeName):
    global success
    df = pd.read_csv("SystemCatalogue.csv")
    types = df["type"].tolist()
    if typeName not in types:
        success = False
    else:
        df = pd.read_csv("SystemCatalogue.csv", index_col="type")
        files = df.loc[typeName].get("files").split()
        for file in files:
            os.remove(file)
        df.drop(index=typeName, inplace=True)
        df.to_csv("SystemCatalogue.csv")
        success = True
    
def listType(out_file):
    global success
    df = pd.read_csv("SystemCatalogue.csv")
    types = df["type"].tolist()
    
    for name in types:
        out_file.write(name+'\n')
    success = True
    



def organizer(record, num_fields):
    tmp = ''
    for i in range(num_fields):
        tmp = tmp + record[i] + " "
    return tmp

def searchRecord(type, key):
    key = key.strip('\n')
    #burada system katalog okunacak ve name ile ilgili olan dosyalar önümüze serilecek ya da kac dosya oldugu
    
    ######### the below interval will be commented
    #db_file = name + "0.txt" #bu aslında bir array of files olucak ya da olmayadabilir
    #db_files = []
    #db_files.append(db_file)
    #########    

    df = pd.read_csv("SystemCatalogue.csv", index_col="type")
    db_files = df.loc[type].get("files").split(" ") #file list
    num_fields = df.loc[type].get("fieldnum") #number of fields

    for i in db_files:
        file = open(i, 'r')
        
        for j in range(8):
            page_header = file.readline() # page header
            page_header = page_header.strip('\n')
            page_info = page_header.split(',')
            page_id = page_info[1]
            if page_info[0] == '1': # if page is empty not found since if we come to an empty page there is no need to a further look
                print("search unsuccesful")
                break #return
            
            page_entries = page_info[2:] #taken just the entry info
            


            if key in page_entries:
                for k in range(11):
                    record = file.readline()
                    record = record.split(',')
                    if record[1] == key:
                        #### record found
                        temp = organizer(record, num_fields)
                        file.close()
                        return (i, j, k, temp) # return file name page id record order 
            else:
                for k in range(11):
                    file.readline()
   
       
        file.close()
        

    

    return -1,-1,-1,-1


def addRecord(record_info):

    
    nextfile=0 ## recordu yerleştiremezsek ve yeni filea geçmek gerekiyorsa 0 kalıcak
    fileindex=-1 ## index of the file that record will be placed
    while(nextfile==0):
        fileindex=fileindex+1




        file=record_info[0]+str(fileindex)+".txt"
        tempfile="temp.txt"
        transferrecord="null"
        with open(file, 'r+') as f, open(tempfile, 'w') as myfile2:

            recordplaced=0
    
            for k in range(pagecount):   ## there are 8 pages
                
                lines =[]
                lines.extend(f.readline() for i in range(linecount)) ## read the pages in order

                
                pageheader = lines[0].split(',')

                
                if(pageheader[0]=="1"):
                    pageheader[0]=0  ## artık bu page boş değil
                
                
                index=0
                for i in range(2,(linecount+1)):
                    
                    

                    if "$" in pageheader[i] and recordplaced==0 : ##pageheader boşsa direkt yerleştir
                        recordplaced=1
                        nextfile=1
                        index=i
                        pageheader[index]= record_info[1]
                        listToStr = ','.join([str(elem) for elem in pageheader])
                        if(i==linecount):
                            lines[0]=listToStr+"\n"
                        else:
                            lines[0]=listToStr ## page header güncellendi
                        numberoffields=len(record_info) ## burayı sistem katologtan çekicem
                        lines[index-1]="E226-S187,"
                        for i in range(1,numberoffields):
                            lines[index-1]=lines[index-1]+record_info[i]+","

                        lines[index-1]=lines[index-1]+","*(fieldcount-numberoffields-1)+"\n"
                        #lines[index-1]="E226-S187,"+record_info[1]+","+record_info[2]+","+record_info[3]+","*(fieldcount-numberoffields)+"\n"
                        
                        break
                    
                    
                    elif pageheader[i].isnumeric() or pageheader[i][:-1].isnumeric() :
                        if pageheader[i].isnumeric()==False:
                            pageheader[i]=pageheader[i][:-1]
                       
                         
                        if int(record_info[1])>int(pageheader[i]) and recordplaced==0:   ## convert integer value of the string, burayı long yapabiliriz
                            recordplaced=1
                            nextfile=1
                            index=i
                            for p in range(linecount-1,index-2, -1):  ##if the new primary key is bigger than other shift others in page header and entry
                                
                                
                                if(p==linecount-1) and pageheader[linecount]!="$\n" : ## eğer page tamamen doluysa ve yeni gelen record bu page'e yerleşecekse son recordu al ve işlemleri yeniden yap
                                    
                                    transferrecord=lines[linecount-1]
                                    
                                    
                                    
                                    

                                    

                                lines[p]=lines[p-1]

                                if(p==linecount-1):
                                    pageheader[p+1]=pageheader[p]+"\n"
                                else:
                                    pageheader[p+1]=pageheader[p]

                                
            
                            pageheader[index]= record_info[1]

                            listToStr = ','.join([str(elem) for elem in pageheader])
                            if(i==linecount):
                                lines[0]=listToStr+"\n"
                            else:
                                lines[0]=listToStr ## page header güncellendi
                            numberoffields=len(record_info) ## burayı sistem katologtan çekicem
                            lines[index-1]="E226-S187,"
                            for i in range(1,numberoffields):
                                lines[index-1]=lines[index-1]+record_info[i]+","

                            lines[index-1]=lines[index-1]+","*(fieldcount-numberoffields-1)+"\n"

                            #lines[index-1]="E226-S187,"+record_info[1]+","+record_info[2]+","+record_info[3]+","*(fieldcount-numberoffields)+"\n"


                            
                            break





                #print(pageheader)
                
                #print(lines[0])        
                
            
                for i in range(linecount):
                    myfile2.write(lines[i])

                
                    

        os.remove(file)
        os.rename(tempfile, file)
        if(transferrecord!="null"):
                op=[]
                    
                list=transferrecord.split(',')
                
               
                
                
                op.append(record_info[0])
                for z in range(1,(len(list)-1)):
                    
                    
                    op.append(list[z])


                
                addRecord(op )


def deleteRecord(record_info):


    
    a,b,c,d = searchRecord(record_info[0], record_info[1])
    file=a
    tempfile="temp1.txt"
    transferrecord="null"
    transferrecordfromfile="null"
    print(a,b,c)
   
    with open(file, 'r+') as f, open(tempfile, 'w') as myfile2:
        
        checknextpage=0
        checknextfile=0
        
        for k in range(pagecount):
           
            lines=[]
            
            lines.extend(f.readline() for i in range(linecount)) ## read the pages in order
            
            

            

            
            if k==b:  ## record in the (k+1)th page
                pageheader = lines[0].split(',')

                if(c==0 and pageheader[3]=="$"): ## If I delete the first entry and the next record is empty that's mean page is now empty
                    pageheader[0]=1 ## tüm entrleer silindi page headerdaki parametreyi 1 yap
                

                if(k<7): ## bir sonraki page'e bakıcaz
                    for i in range(c+2,(linecount+1)):
                        
                        
                        if(i==12):
                            if  pageheader[12]!="$\n":
                                #print("bir sonraki pageden al")
                                #checknextpage=[1,k]
                                checknextpage=1
                                lines1=[]

                                lines1.extend(f.readline() for i in range(linecount)) ## read the next page
                                pageheader1 = lines1[0].split(',')
                                
                                if pageheader1[0]=="1": ## bir sonraki page boşsa
                                    lines[11]=","*11+"\n"
                                    pageheader[12]="$\n"
                                else:
                                    lines[11]=lines1[1] ## take the first line in the next page
                                    pageheader[12]=pageheader1[2]+"\n"
                                    pageheader2 = lines1[1].split(',')
                                    pageheader2[1]=-1## inputlarda primary key -1 olamaz o yüzden -1 yapıp bunu recursion ile silicem
                                    listToStr1 = ','.join([str(elem) for elem in pageheader2])
                                    lines1[1]=listToStr1
                                    pageheader1[2]=-1
                                    listToStr2 = ','.join([str(elem) for elem in pageheader1])
                                    lines1[0]=listToStr2

                                    transferrecord=lines1[1]
                                    
               
                                
                                


                                

                        
                        

                        elif(i==11): ## sondan ikinciye "\n"koymak istemiyoruz
                            pageheader[11]=pageheader[12][:-1]
                            lines[10]=lines[11]
                        else:
                            pageheader[i]=pageheader[i+1]

                            lines[i-1]=lines[i]

                        listToStr = ','.join([str(elem) for elem in pageheader])
                        lines[0]=listToStr
                    
                elif(k==7): ## bir sonraki file'a bakıcaz
                    for i in range(c+2,(linecount+1)):
                        
                        
                        if(i==12):
                            if  pageheader[12]!="$\n":                           
                                checknextfile=1
                                lines1=[]

                                file1=a[:-5]+str(int(a[-5:-4])+1)+a[-4:] ## find the next file
                                tempfile2="temp2.txt"
                                
                                with open(file1, 'r+') as f1,open(tempfile2, 'w') as myfile3:

                                    lines1.extend(f1.readline() for i in range(linecount)) ## read the next file's first page
                                    pageheader1 = lines1[0].split(',')
                                    
                                    if pageheader1[0]=="1": ## bir sonraki page boşsa
                                        lines[11]=","*11+"\n"
                                        pageheader[12]="$\n"
                                    else:
                                        lines[11]=lines1[1] ## take the first line in the next page
                                        pageheader[12]=pageheader1[2]+"\n"
                                        
                                        pageheader2 = lines1[1].split(',')
                                        pageheader2[1]=-1## inputlarda primary key -1 olamaz o yüzden -1 yapıp bunu recursion ile silicem #
                                        listToStr1 = ','.join([str(elem) for elem in pageheader2])
                                        lines1[1]=listToStr1
                                        pageheader1[2]=-1 ##pageheadrı -1 yapıyorum 
                                        listToStr2 = ','.join([str(elem) for elem in pageheader1])
                                        lines1[0]=listToStr2

                                        transferrecordfromfile=lines1[1]
                                        for i in range(linecount):  ## write the first page 
                                            myfile3.write(lines1[i])
                                        
                                        for k in range(pagecount-1): ## diğer pageleri okuyuorum
                                            lines1=[]
                                            lines1.extend(f1.readline() for i in range(linecount)) ## diğre filedaki diğer pageleri okuyorum
                                            for i in range(linecount):  ## diğer pageleri yazıyorum
                                                myfile3.write(lines1[i])
                                        
                                os.remove(file1)   
                                os.rename(tempfile2, file1)      ## 2. fileı güncelleiyorum  
                                
                                


                                

                        
                        

                        elif(i==11): ## sondan ikinciye "\n"koymak istemiyoruz
                            pageheader[11]=pageheader[12][:-1]
                            lines[10]=lines[11]
                        else:
                            pageheader[i]=pageheader[i+1]

                            lines[i-1]=lines[i]

                        listToStr = ','.join([str(elem) for elem in pageheader])
                        lines[0]=listToStr    
                                    


                     

        
            for i in range(linecount):
                myfile2.write(lines[i])

            if(checknextpage==1):
                for i in range(linecount):
                    myfile2.write(lines1[i]) 
            checknextpage=0
            
    os.remove(file)
    os.rename(tempfile, file)
    if(transferrecord!="null"):
        op=[]            
        list=transferrecord.split(',')
                        
        op.append(record_info[0])
        op.append(list[1])
                    
       
                    
        deleteRecord(op)      
    
    if(transferrecordfromfile!="null"):  ## 2. filedan data aldıysam o datayı 2. filedan sil
        op=[]            
        list=transferrecordfromfile.split(',')
                        
        op.append(record_info[0])
        op.append(list[1])

        print(op)
                    
       
                    
        deleteRecord(op) 


def listRecords(type, outfile):
    global success
    df = pd.read_csv("SystemCatalogue.csv", index_col="type")
    data_files = df.loc[type].get("files").split(" ") #file list
    num_fields = df.loc[type].get("fieldnum") #number of fields
    count = 0
    for i in data_files:
        file = open(i, 'r')
        for j in range(8):
            page_header = file.readline() # page header
            page_header = page_header.strip('\n')
            page_info = page_header.split(',')
            if page_info[0] == '1': # if page is empty not found since if we come to an empty page there is no need to a further look
                success = False if count == 0 else True
                return   
            temp = ''
            for k in range(11):
                record = file.readline()
                record = record.split(',')
                if record[0] == '':
                    success = False if count == 0 else True
                    return
                outfile.write(organizer(record, num_fields) + '\n')
                count = count+1

 



createSystemFiles()                   #create files

out_file = open(outputFile, 'w')

with open(inputFile, 'r') as f:         #read input file
    
    commands = f.readlines()
        
    for command in commands:
        command = command.strip()
        operation = command.split()
        
        if operation[0]=='register' and operation[1]=='user':           #HALO Authentication Language Operations
            register(operation[2], operation[3], operation[4])   

        elif operation[0]=="login":                           
            login(operation[1], operation[2]) 
            if success:
                loggedIn = True
        elif operation[0]=="logout":
            logout()
        elif not loggedIn:		#if not logged in skip
             success = False
        else:
            if operation[1]=="type":                                    #HALO Definition Language Operations
                if operation[0]=="create":
                    createType(operation[2:])
                elif operation[0]=="inherit":
                    inheritType(operation[2:])
                elif operation[0]=="delete":
                    deleteType(operation[2])
                elif operation[0]=="list":
                    listType(out_file)
                                                                        #HALO Management Language Operations
            elif operation[1]=="record":
                if operation[0]=="create":
                    addRecord(operation[2:]) 
                elif operation[0]=="delete":
                    deleteRecord(operation[2:])
                elif operation[0] == "list":
                    listRecords(operation[2], out_file)
            
            
        if operation[0]!="logout":                                      #write log
            userlog = "null" if user is None else user

        if operation[0]=="login":
            command = "login"
            userlog = operation[1]
            
        elif operation[0]=="register":
            command = " ".join(operation[:-2])

        status = "success" if success else "failure"

        log = {"username":[userlog],"occurrence":[str(int(time.time()))],"operation":[command],"status":[status]}
        record = pd.DataFrame(data = log)
        record.to_csv("haloLog.csv", index=False, header=False, mode='a')

out_file.close()