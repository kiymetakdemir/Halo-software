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
    
                
def createNewFile(typename):
    
    df = pd.read_csv("SystemCatalog.csv", index_col="type") #get type info
    filenum = df.loc[typename].get("filenum")
    files = df.loc[typename].get("files")
    fieldnames = df.loc[typename].get("fields")
    
    fields = pd.DataFrame(columns = ["planet","id"]+fieldnames.split()) #create file
    filename = typename+str(filenum)+".csv"
    fields.to_csv(filename, index=False)
    
    df.loc[typename, "filenum"] =filenum + 1                #update system catalog
    df.loc[typename, "files"] = files + " " + filename
    df.to_csv("SystemCatalog.csv")
    
def createSystemFiles():
    col = pd.DataFrame(columns=["type","filenum","files","fieldnum","fields"])
    col.to_csv("SystemCatalog.csv", index=False)
    
    col = pd.DataFrame(columns=["username","occurrence","operation","status"])
    col.to_csv("haloLog.csv", index=False)
    
    col = pd.DataFrame(columns=["username","password"])
    col.to_csv("users.csv", index=False)
   
def createType(operation):
    typename = operation[0]
    fieldnum = operation[1]
    fields = operation[2:]
    newType = {"type":[typename],"filenum":[1],"files":[typename+"0"+".csv"],"fieldnum":[fieldnum],"fields":[" ".join(operation[2:])]}
    data = pd.DataFrame(data=newType)
    data.to_csv("SystemCatalog.csv", mode='a', index=False, header=False)
    
    fields = pd.DataFrame(columns = ["planet","id"]+fields)
    fields.to_csv(typename+"0"+".csv", index=False)
    
def inheritType(operation):
    newType = operation[0]
    oldType = operation[1]
    newFields = operation[2:]
    df = pd.read_csv("SystemCatalog.csv", index_col="type")
    fields = df.loc[oldType].get("fields")
    fieldnum = df.loc[oldType].get("fieldnum") + len(newFields)
    createType([newType]+[fieldnum]+fields.split()+newFields)
    
def deleteType(typeName):
    df = pd.read_csv("SystemCatalog.csv", index_col="type")
    files = df.loc[typeName].get("files").split()
    for file in files:
        os.remove(file)
    df.drop(index=typeName, inplace=True)
    df.to_csv("SystemCatalog.csv")
    
def listType():
    global success
    df = pd.read_csv("SystemCatalog.csv")
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
            userlog=user
            user = None  
            loggedIn = False
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
        
