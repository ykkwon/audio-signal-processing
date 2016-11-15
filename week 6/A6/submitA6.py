### The only things you'll have to edit (unless you're porting this script over to a different language) 
### are at the bottom of this file.
import urllib
import urllib2
import email
import email.message
import email.encoders
import sys
import pickle
import json
import base64
import numpy as np
import subprocess
import os

""""""""""""""""""""
""""""""""""""""""""

class NullDevice:
    def write(self, s):
        pass

def submit():   
    print '==\n== Submitting Solutions: Programming Assignment-1\n=='
 
    (email, password) = loginPrompt()
    if not email:
        print '!! Submission Cancelled'
        return
    
    print '\n== Connecting to Coursera ... '
    
    # Part Identifier
    (partIdx, sid) = partPrompt()
    
    # submitting all the parts at once
    if partIdx == 'all':
        rep = submitSolution_all_parts(email, password)
        #print rep
        if 'element' in rep:
            print '\n== Your submission has been accepted and will be graded shortly.'
        else:
            wrongSubmission()     
        
    # error in the process
    elif partIdx == 'error':
        print '== Submission Cancelled'
        return
    
    # submiting one part
    elif isinstance(partIdx, int):
        if partIdx in range(len(partIds)):
            rep = submitSolution(email, password, output(partIdx), partIdx)
            #print rep
            if 'element' in rep:
                print '\n== Your submission has been accepted and will be graded shortly.'
            else:
                wrongSubmission()            
        else:
            print '== Wrong number of part, Submission Cancelled'
            return
    


# =========================== LOGIN HELPERS - NO NEED TO CONFIGURE THIS =======================================

def loginPrompt():
    email = raw_input('Login (Email adress):')
    password = raw_input('Submission Token (from the assignment page. This is NOT your own account\'s password): ')
    return email, password

def partPrompt():
    print 'Hello! These are the assignment parts that you can submit:'
    counter = 0
    for part in partFriendlyNames:
        counter += 1
        print str(counter) + ') ' + partFriendlyNames[counter - 1]
    print '\n== Once your parts are correct, you have to submit them all at once by entering "all"'
    partIdx = raw_input('Please enter which part you want to submit (1-' + str(counter) + ' or all): ')   
    try:
        partIdx = int(partIdx)-1
        return (partIdx, partIds[partIdx-1] )
    except ValueError, IndexError: 
        if partIdx == 'all':
            return ('all','all')
        else:
            return ('error', 'error')

def submit_url():
    """Returns the submission url."""
    return "https://www.coursera.org/api/onDemandProgrammingScriptSubmissions.v1"
    #return "https://class.coursera.org/" + URL + "/assignment/submit"

def get_parts(partIdx, output):
    part = LIST_PARTIDS[partIdx]
    parts = {}
    for parti in LIST_PARTIDS:
        parts[parti] = {}
    output = output + '\n\n\n' + source(partIdx) # concatenating with the source code for log
    #print source(partIdx)
    parts[part] = {"output" : output}
    return parts
    
def submitSolution(email_address, secret, output, partIdx):
    """Submits a solution to the server. Returns (result, string)."""
    output_64_msg = email.message.Message()
    output_64_msg.set_payload(output)
    email.encoders.encode_base64(output_64_msg)
    parts = get_parts(partIdx, output_64_msg.get_payload())
    
    values = { "assignmentKey" : ASSIGNMENT_KEY, \
             "submitterEmail" : email_address, \
             "secret" : secret, \
             "parts" : parts, \
           }
    response = send_request_new(values)
    return response

def get_all_parts(outputs):
    parts = {}
    for idx, parti in enumerate(LIST_PARTIDS):
        parts[parti] = {"output" : outputs[idx]}
    return parts

def submitSolution_all_parts(email_adress, secret):
    """Submit all parts at once"""
    outputs = []
    for idx in range(len(LIST_PARTIDS)):
        out = output(idx)
        output_64_msg = email.message.Message()
        output_64_msg.set_payload(out)
        email.encoders.encode_base64(output_64_msg)
        outputs.append(output_64_msg.get_payload() + '\n\n\n' + source(idx)) # concatenating the source code for log
    parts = get_all_parts(outputs)
    values = { "assignmentKey" : ASSIGNMENT_KEY, \
             "submitterEmail" : email_adress, \
             "secret" : secret, \
             "parts" : parts, \
           }
    response = send_request_new(values)
    return response
    
# old version that do not support long text
def send_request(values):
    req = 'curl -s -X POST -H "Cache-Control: no-cache" -H "Content-Type: application/json" -d ' +\
    "'" + str(json.dumps(values)) + "' " + \
    "'https://www.coursera.org/api/onDemandProgrammingScriptSubmissions.v1'"
    print '\n== The request sent to Coursera: \n' + req
    output = subprocess.check_output(req, shell=True)
    return output

def send_request_new(values):
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }
    url = submit_url()  
    #data = urllib.urlencode(values)
    try:
        req = urllib2.Request(url, json.dumps(values), headers)
        response = urllib2.urlopen(req)
        string = response.read().strip()
        #print values
        return string
    except Exception as e:
# using requests module
        try:
            import requests
        except ImportError:
            raise Exception('Something got wrong. Try installing Requests module and retry ("pip install requests")')
        r = requests.post(url, headers=headers, data=str(json.dumps(values)))
        #print values, r.content
        return r.content

## This collects the source code (just for logging purposes) 
def source(partIdx):
    # open the file, get all lines
    f = open(sourceFiles[partIdx])
    src = f.read() 
    f.close()
    # This was used for encoding the source code
    source_64_msg = email.message.Message()
    source_64_msg.set_payload(src)
    email.encoders.encode_base64(source_64_msg)
    return source_64_msg.get_payload()

def convertNpObjToStr(obj):
    """
    if input object is a ndarray it will be converted into a dict holding dtype, shape and the data base64 encoded
    """
    if isinstance(obj, np.ndarray):
        obj = np.ascontiguousarray(obj)# this is a very important step, because many times the np object doesn't have its content in continous memory
        data_b64 = base64.b64encode(obj.data)
        return json.dumps(dict(__ndarray__=data_b64,dtype=str(obj.dtype),shape=obj.shape))
    return json.dumps(obj)

def wrongOutputTypeError(outType):
    print "The output data type of your function doesn't match the expected data type (" + str(outType) + ")."
    print "== Submission failed: Please correct and resubmit."

def wrongSubmission():
    print "\n== Submission failed: Please check your email and token again and resubmit."
    
############ BEGIN ASSIGNMENT SPECIFIC CODE - YOU'LL HAVE TO EDIT THIS ##############

from A6Part1 import estimateF0
from A6Part2 import segmentStableNotesRegions
from A6Part3 import estimateInharmonicity

# DEFINE THE ASSIGNMENT KEY HERE
ASSIGNMENT_KEY = '_FSTOFmcEeaE1Aq9ydCvpw'

# DEFINE THE PartIds in this list for each PA
LIST_PARTIDS = ['O5dhP', 'rBYjr', 'kRUA0'] ################## CHANGE THE PART IDS HERE !!

# the "Identifier" you used when creating the part
partIds = ['A6-part-1', 'A6-part-2', 'A6-part-3']

# used to generate readable run-time information for students
partFriendlyNames = [ 'Estimate fundamental frequency in polyphonic audio signal', 
                      'Segmentation of stable note regions in an audio signal',
                      'Compute amount of inharmonicity present in a sound'] 

# source files to collect (just for our records)
sourceFiles = ['A6Part1.py', 'A6Part2.py', 'A6Part3.py']

def output(partIdx):
    """Uses the student code to compute the output for test cases."""
    outputString = ''
    dictInput = pickle.load(open("testInputA6.pkl"))  ## load the dictionary containing output types and test cases
    testCases = dictInput['testCases']
    outputType = dictInput['outputType']
  
    if partIdx == 0: # This is A6-part-1: 
        pID = 'A6-part-1'
        for line in testCases[pID]:
            answer = estimateF0(**line)
            if outputType[pID][0] == type(answer):
                outputString += convertNpObjToStr(answer) + '\n'
            else:
                wrongOutputTypeError(outputType[pID][0])
                sys.exit(1)
  
    elif partIdx == 1: # This is A6-part-2:
        pID = 'A6-part-2'
        for line in testCases[pID]:
            answer = segmentStableNotesRegions(**line)
            if outputType[pID][0] == type(answer):
                if answer.shape[1] !=2:
                    print "Shape of the returned numpy array doesn't match the expected shape (k,2). Number of columns returned are " + str(answer.shape[1]) + "."
                outputString += convertNpObjToStr(answer) + '\n'
            else:
                wrongOutputTypeError(outputType[pID][0])
                sys.exit(1)      
      
    elif partIdx == 2: # This is A6-part-3:
        pID = 'A6-part-3'
        for line in testCases[pID]:
            answer = estimateInharmonicity(**line)
            if outputType[pID][0] == type(answer):
                outputString += convertNpObjToStr(answer) + '\n'
            elif outputType[pID][0] == float and str(type(answer)).count('float') >0:
                outputString += convertNpObjToStr(answer) + '\n'
            else:
                wrongOutputTypeError(outputType[pID][0])
                sys.exit(1)         

    return outputString.strip()

submit()