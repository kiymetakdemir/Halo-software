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
fileId = 0

def register(username, pw1, pw2):
    global success
    with open("users.txt", 'a') as w:
        if pw1 == pw2:
            w.write(username+" "+pw1+"\n")
            success = True
          
def login(username, password):
    global success
    global user
    user = None 
    success = False
    with open("users.txt", 'r') as u:
        lines = u.readlines()
        for line in lines:                          #check username and password
            info = line.split()
            if username == info[0] and password == info[1]:
                user = username
                success = True

def createSystemCatalog():
    col = pd.DataFrame(columns=["type","files","fields"])
    col.to_csv("SystemCatalog.csv", index=False)
    
def createLogFile():
    col = pd.DataFrame(columns=["username","occurrence","operation","status"])
    col.to_csv("haloLog.csv", index=False)
   
def createType(operation):
    global fileId
    newType = {"type":[operation[0]],"files":[str(fileId)], "fields":[" ".join(operation[2:])]}
    data = pd.DataFrame(data=newType)
    data.to_csv("SystemCatalog.csv", mode='a', index=False, header=False)
    
    fields = pd.DataFrame(columns = ["planet","id"]+operation[2:])
    fields.to_csv(str(fileId)+".csv", index=False)
    fileId += 1
    
def inheritType(operation):
    newType = operation[0]
    oldType = operation[1]
    df = pd.read_csv("SystemCatalog.csv", index_col="type")
    fields = df.loc[oldType].get("fields")
    createType([newType]+["0"]+fields.split()+operation[2:])
    
def deleteType(typeName):
    df = pd.read_csv("SystemCatalog.csv", index_col="type")
    files = str(df.loc[typeName].get("files")).split(',')
    for file in files:
        os.remove(file+".csv")
    df.drop(index=typeName, inplace=True)
    df.to_csv("SystemCatalog.csv")
    
def listType():
    global success
    df = pd.read_csv("SystemCatalog.csv")
    types = df["type"].tolist()
    with open(outputFile, "w") as f:
        for name in types:
            f.write(name+'\n')
    if len(types)==0:
        success = False
    
createSystemCatalog()
createLogFile()

with open(inputFile, 'r') as f:
    
    commands = f.readlines()
        
    for command in commands:
        operation = command.split()
        
        if operation[0]=='register' and operation[1]=='user':           #HALO Authentication Language Operations
            register(operation[2], operation[3], operation[4])   

        elif operation[0]=="login":                           
            login(operation[1], operation[2]) 
            if success:
                loggedIn = True
        elif operation[0]=="logout":    #failure if already logged out?
            userlog=user
            user = None  
            loggedIn = False
            
        elif not loggedIn:
            success = False
        else:
            if operation[1]=="type":                                  #HALO Definition Language Operations
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
                
            
            
        if operation[0]!="logout":     
            if user is None:
                userlog = "null"
            else:
                userlog = user
        if operation[0]=="login":
            command = "login"
            userlog = operation[1]
        elif operation[0]=="register":
            command = " ".join(operation[:-2])
        if success:
            status = "success"
        else:
            status = "failure"
        log = {"username":[userlog],"occurrence":[str(int(time.time()))],"operation":[command],"status":[status]}
        record = pd.DataFrame(data = log)
        record.to_csv("haloLog.csv", index=False, header=False, mode='a')
