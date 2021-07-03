#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 20 00:14:59 2021

@author: kiymet
"""
import pandas as pd
import os
import time

inputFile = "input.txt"
outputFile = "output.txt"
user = None
loggedIn = True
success = True


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
    
def listType():
    global success
    df = pd.read_csv("SystemCatalogue.csv")
    types = df["type"].tolist()
    with open(outputFile, "w") as f:
        for name in types:
            f.write(name+'\n')
    success = True
    
createSystemFiles()                   #create files

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
                    listType()
                                                                        #HALO Management Language Operations
            elif operation[1]=="record":
                pass
                
            
            
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