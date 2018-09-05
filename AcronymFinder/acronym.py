# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 17:02:28 2018

@author: Sravani
"""
import re
import sys
from nltk.corpus import stopwords

stopWords = set(stopwords.words('english'))


#check if it is an acronym
def isAcronym(word):
    if(len(word)>=3 and len(word)<=8 and word.isupper()):
       return True
    return False
#check and remove the braces
def check_and_remove_braces(word):
    newword=word
    length=len(word)
    if((word[0]=='(' or word[0]=='{' or word[0]=='[') and (word[length-1]==')' or word[length-1]=='}' or word[length-1]==']')):
        newword=word[1:length-1]
    
    return newword
#get the list of possible words in the window
def possible_words(window,wordlist):
    res=[]
    for words in wordlist:
        res.append(words)    
    return res
#builds LCS Matrix
def build_LCS_Matrix(X,Y):
    m=len(X)
    n=len(Y)
    c=[[0 for j in range(n+1)] for i in range(m+1)]
    b=[[0 for j in range(n+1)] for i in range(m+1)]
    m=len(X)
    n=len(Y)
    for i in range(1,m+1):
        for j in range(1,n+1):
            if(X[i-1]==Y[j-1]):
                c[i][j]=c[i-1][j-1]+1
                b[i][j]='D'
            elif(c[i-1][j]>=c[i][j-1]):
                c[i][j]=c[i-1][j]
                b[i][j]='U'
            else:
                c[i][j]=c[i][j-1]
                b[i][j]='L'
    return c,b
#parse the LCS matrix to get the vector list
def parse_LCS_matrix(b,start_i,start_j,m,n,lcs_length,stack,vectorlist):
    for i in range(start_i,m+1):
       for j in range(start_j,n+1):
           if(b[i][j]=='D'):
               stack.append((i,j))
               if(lcs_length==1):
                   vector=build_vector(stack,n)
                   vectorlist.append(vector)
                   
               else:
                   parse_LCS_matrix(b,i+1,j+1,m,n,lcs_length-1,stack,vectorlist)
                   stack.pop()
                   
    
    return vectorlist

def build_vector(stack,n):
    vector=[0]*n
    for i,j in stack:
        vector[j-1]=i
    return vector

def vector_values(V,types):
    i=1
    for i,x in enumerate(V):
        if x is not None:
            start=i
            break
    V_rev=V[::-1]
    for i,x in enumerate(V_rev):
        if x is not None:
            end=i
            break
    
    dict={}
    dict['size']=end-start+1
    dict['distance']=(len(V)-1)-end
    dict['misses']=0
    dict['stopcount']=0
    for i in range(start,end+1):
        if(V[i]>0 and types[i]=='s'):
            dict['stopcount']=dict['stopcount']+1
        elif(V[i]==0 and types[i]!='s'):
            dict['misses']=dict['misses']+1
    
    return dict

def compare_Vectors(A,B,types):
    vector_A=vector_values(A,types)
    vector_B=vector_values(B,types)
    
    if(vector_A['misses']>vector_B['misses']):
        return B
    elif(vector_A['misses']<vector_B['misses']):
        return A
    if (vector_A['stopcount'] > vector_B['stopcount']):
        return B
    elif (vector_A['stopcount'] < vector_B['stopcount']):
        return A
    if (vector_A['distance'] > vector_B['distance']):
        return B
    elif (vector_A['distance'] < vector_B['distance']):
        return A
    if (vector_A['size'] > vector_B['size']):
        return B
    elif (vector_A['size'] < vector_B['size']):
        return A
    return A



#this function gets the definiton of acronym
def getDefinition(acronym,words):
    leaders=[x[0].lower() for x in words]
    types=[]
    for word in words:
        if word.lower() in stopWords:
            types.append('s')
        else:
            types.append('w')
    ai=acronym.lower()
    li=''.join(leaders)
    
    m=len(ai)
    n=len(li)
    
    #LCS Matrix
    c,b=build_LCS_Matrix(ai,li)
    #building results vector by parsing the matrix
    result_vector=parse_LCS_matrix(b,0,0,m,n,c[m][n],[],[])
    #if words not found
    if(not result_vector):
        return "No definition found"
    
    #comparing vectors for the possible match
    final_Vector=result_vector[0]
    
    for i in range(1,len(result_vector)):
        final_Vector = compare_Vectors(final_Vector, result_vector[i], types)
        
    #finding the starting and ending index of acronym words
    start = next((i for i, x in enumerate(final_Vector) if x), None)
    V_rev = final_Vector[::-1]
    end   = next((i for i, x in enumerate(V_rev) if x), None)
    end   = (len(final_Vector)-1) - end
    
    #forming the list of words for acronym definition and returning it
    result=[]
    for i,x in enumerate(final_Vector):
        if (i>=start and i<=end):
             result.append(words[i])

    return ' '.join(result)
    
    return final_Vector

def acronymFinder(f):
    #filename='myText.txt'
    contents=''
    window=0
    acronymDef={}
    #f=open(filename,'r')
    
    for line in f.readlines():
        contents += line
    contents=list(contents.split())
    
    for word in contents:
        if(isAcronym(word)):
            currindex=contents.index(word)
            #check for the braces and remove if any
            word=check_and_remove_braces(word)
            window=2*len(word)
           
            if(currindex-window<0):
                startindex=0
            else:
                startindex=currindex-window
            #get all possible words in the window and store in a dict
            possible=possible_words(window,contents[startindex:currindex])
            acronymDef[word]=possible
    
    result={}
    for index in acronymDef:
        #get the definition of each acronym
        result[index]=getDefinition(index,acronymDef[index])
    
    return result        
#driver code

#read file from input
filename=sys.argv[1]
try:
    f=open(filename,'r')
    acronymdef=acronymFinder(f)
    print("-----------------------------")
    print("Acronym and their Definitions")
    print("-----------------------------")
    for item in acronymdef:
        print(item +'-'+acronymdef[item])
    f.close()   
except IOError:
    print('cannot open this file')

#f=open('myText.txt','r')
#print(acronymFinder(f))
    