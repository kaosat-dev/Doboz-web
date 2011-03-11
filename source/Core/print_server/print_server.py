import logging
import os
import sys
import time
import datetime

from bottle import Bottle, route, run, send_file, redirect, abort, request, response 
from bottle import TornadoServer
import bottle

#from reprap_manager import ReprapManager
from point_cloud import PointCloudBuilder,PointCloud,Point
import socket


from Core.automation.print_task import PrintTask
from Core.automation.scan_task import ScanTask


testBottle = Bottle()
testBottle.path=os.path.join(os.path.abspath("."),"Core","print_server")
printFilesPath=os.path.join(testBottle.path,"files","machine","printFiles")
scanFilesPath=os.path.join(testBottle.path,"files","machine","scanFiles")
if not os.path.exists(printFilesPath):
    os.mkdir(printFilesPath)
if not os.path.exists(scanFilesPath):
    os.mkdir(scanFilesPath)


testBottle.logger=logging.getLogger("Doboz.Core.WebServer")
testBottle.reprapManager=None
testBottle.uploadProgress=0



        
@testBottle.route('/upload', method='POST')
def do_upload():
    
    datafile = request.POST.get('datafile')
    print("filename",datafile.filename)

    try:
        testBottle.uploadProgress=0
        saved_file=open(os.path.join(testBottle.path,"files","machine","printFiles",datafile.filename),'w')
        saved_file.write(datafile.value)
        saved_file.close()
        testBottle.uploadProgress=100
    except Exception as inst:
        testBottle.logger.critical("error %s",str(inst))
        
@testBottle.route('/uploadProgress', method='GET')
def upload_progress():
     callback=request.GET.get('callback', '').strip()
     data={"progress":testBottle.uploadProgress}
     response=callback+"("+str(data)+")"
     return response



@testBottle.route('/filecommands/:command' , method='GET')
def printandscanFiles(command):
    testBottle.logger.critical("handling file commands")
    callback=request.GET.get('callback', '').strip()
    response=callback+"()"
    
    
    def fullPrintFileInfo(file):
        
            return {"fileName":str(file),"modDate": str(time.ctime(os.path.getmtime(os.path.join(testBottle.path,"files","machine","printFiles",file))))}
        
    def fullScanFileInfo(file):
            return {"fileName":str(file),"modDate": str(time.ctime(os.path.getmtime(os.path.join(testBottle.path,"files","machine","scanFiles",file))))}
        
    if command=="get_printFiles":
        fileList=os.listdir(os.path.join(testBottle.path,"files","machine","printFiles"))
        try:     
            finalFileList=map(fullPrintFileInfo, fileList)
            data={"files": finalFileList }
            response=callback+"("+str(data)+")"
        except Exception as inst:    
            testBottle.logger.critical("error in file list generation  %s",str(inst))
            
    elif command=="get_scanFiles":
        fileList=os.listdir(os.path.join(testBottle.path,"files","machine","scanFiles"))
        try:     
            finalFileList=map(fullScanFileInfo, fileList)
            data={"files": finalFileList}
            response=callback+"("+str(data)+")"
        except Exception as inst:    
            testBottle.logger.critical("error in file list generation  %s",str(inst))

    elif command=="delete_scanFile":
        fileName=request.GET.get('fileName', '').strip()
        filePath=os.path.join(testBottle.path,"files","machine","scanFiles",fileName)
        os.remove(filePath)
    elif command=="delete_printFile":
        fileName=request.GET.get('fileName', '').strip()
        filePath=os.path.join(testBottle.path,"files","machine","printFiles",fileName)
        os.remove(filePath)
    testBottle.logger.critical("response %s",str(response))
    return response


@testBottle.route('/printcommands/:command' , method='GET')
def printing(command):
    
    callback=request.GET.get('callback', '').strip()
    response=callback+"()"
    
    if command=="start":
        testBottle.logger.critical("User Requested print")
        testBottle.logger.info("adding print task")
        fileName=request.GET.get('fileName', '').strip()
        testBottle.logger.info("filename %s",fileName)
        fileToPrint=os.path.join(testBottle.path,"files","machine","printFiles",fileName)
        testBottle.logger.info("filename %s",fileToPrint)
        try:     
            testBottle.reprapManager.add_task(PrintTask(filePath=fileToPrint)) 
        except Exception as inst:
            testBottle.logger.critical("error in print start %s",str(inst))
                
    elif command=="startpause":
        try:
            testBottle.reprapManager.startPause()
        except Exception as inst:
            testBottle.logger.info("error in print startpause %s",str(inst))    
    elif command=="stop":
        try:
            testBottle.reprapManager.stop_task()
        except Exception as inst:
            testBottle.logger.info("error in print stop %s",str(inst)) 
    elif command=="progress":       
        lastIndex=int(request.GET.get('LastIndex', '').strip())
        blockSize=int(request.GET.get('blockSize', '').strip())
        try:
            truc=testBottle.reprapManager.currentTask.pointCloud.points[lastIndex:]
            truc=",".join(str(pt) for pt in truc)
            truc='['+truc+']'
            progress=testBottle.reprapManager.currentTask.progress
            data={"jobType":'print',"progress":progress,"positions":str(truc)}
            response=callback+"("+str(data)+")"
            testBottle.logger.info("response %s",str(response))  

        except Exception as inst:
            testBottle.logger.critical("error in getting print progress %s",str(inst))
        #data={"progress":testBottle.reprapManager.progress,"positions":str(testBottle.reprapManager.positionList),"lastCommand":testBottle.reprapManager.lastLine or "","file":os.path.basename(testBottle.reprapManager.sourcePath)}
        #response=callback+"("+str(data)+")"
    elif command=="status":
        try:
            data={"jobType":'print',"progress":testBottle.reprapManager.progress,"lastCommand":testBottle.reprapManager.lastLine or ""}
            response=callback+"("+str(data)+")"
            testBottle.logger.info("response %s",str(response))  
        except Exception as inst:
            testBottle.logger.info("error in getting scan status  %s",str(inst))
    elif command=="manual":
        try:     
            gcode=request.GET.get('gcode', '').strip()
            testBottle.reprapManager.connector.send_command(gcode)
        except Exception as inst:
            testBottle.logger.critical("Failure to send manual command")
       
   # testBottle.logger.info("response %s",str(response))  
    return response

@testBottle.route('/scancommands/:command' , method='GET')
def scanning(command):
    
    callback=request.GET.get('callback', '').strip()
    response=callback+"()"
    
    if command=="start":
        testBottle.logger.critical("User Requested scan")
        testBottle.logger.info("starting scan")
        width=float(request.GET.get('width', '').strip())
        height=float(request.GET.get('height', '').strip())
        resolution=float(request.GET.get('resolution', '').strip())
        saveScan=request.GET.get('saveScan', '').strip()
        passes=int(request.GET.get('passes', '').strip())
        fileName=request.GET.get('fileName', '').strip()
    
        filePath=""
        if saveScan=="true" and fileName!="":
            filePath=os.path.join(scanFilesPath,fileName+".ptcld")
            sameFileNameCount=0
            while os.path.exists(filePath):
                filePath=os.path.join(scanFilesPath,fileName+"("+str(sameFileNameCount+1)+").ptcld")
                sameFileNameCount+=1
                
        print("width",width,"height",height,"res",resolution)
        try:     
            testBottle.reprapManager.add_task(ScanTask(scanWidth=width,scanLength=height,resolution=resolution,passes=passes,filePath=filePath,saveScan=saveScan)) 
        except Exception as inst:
            testBottle.logger.critical("error in scan start %s",str(inst))
         
    elif command=="startpause":
        try:
            testBottle.reprapManager.startPause()
        except Exception as inst:
            testBottle.logger.info("error in scan startpause %s",str(inst))
    elif command=="stop":
        try:
            testBottle.reprapManager.stop_task()
        except Exception as inst:
            testBottle.logger.info("error in stopping scan %s",str(inst))
    
    elif command=="progress":
        lastIndex=int(request.GET.get('LastIndex', '').strip())
        blockSize=int(request.GET.get('blockSize', '').strip())
        testBottle.logger.info("lastIndex %s",str(lastIndex))  
        try:
            truc=testBottle.reprapManager.currentTask.pointCloud.points[lastIndex:]
            truc=",".join(str(pt) for pt in truc)
            truc='['+truc+']'
            progress=testBottle.reprapManager.currentTask.progress
            data={"jobType":'scan',"progress":progress,"positions":str(truc)}
            response=callback+"("+str(data)+")"
            testBottle.logger.info("response %s",str(response))  
        except Exception as inst:
            testBottle.logger.critical("error in getting scan progress %s",str(inst))

    return response



@testBottle.route('/uploads/:filename')
def download(filename):
    testBottle.logger.info("pouet %s, path: %s",filename,str(os.path.join(testBottle.path,"files","uploads")))
    send_file(filename, root=os.path.join(testBottle.path,"files","machine","scanFiles"), download=filename)
  

@testBottle.route('/commands/:command' , method='GET')
def generalCommands(command):
    callback=request.GET.get('callback', '').strip()
    response=callback+"()"
    if command == "machineStatus":
        testBottle.reprapManager.sendText("M105")
        testBottle.reprapManager.sendText("M143")
        try:
            data={"headTemp":testBottle.reprapManager.headTemp,"bedTemp":testBottle.reprapManager.bedTemp,"lastCommand":testBottle.reprapManager.lastLine or ""}
            response=callback+"("+str(data)+")"
        except Exception as inst:
            testBottle.logger.info("error in getting machine status %s",str(inst))
    
    elif command=="jobStatus":   
        try: 
            """We list all the tasks  + add info if any progress of the current one """
            tasks=[str(task) for task in testBottle.reprapManager.tasks]
            
            running='false'
            if testBottle.reprapManager.currentTask: 
                running='true'
            currentInfo='{"running": %s,"task": %s}' %(running, testBottle.reprapManager.currentTask or '""' ) 
            data={"tasks": tasks,"current":currentInfo} 
            response=callback+"("+str(data)+")"
        except Exception as inst:
            testBottle.logger.critical("error in getting job status  %s",str(inst))     
            
        testBottle.logger.critical("response %s",str(response))  
    return response

@testBottle.route('/longpolling/:command' , method='GET')
def longpollresponder(command):
    testBottle.logger.info("Doing longPoll")
    machin=False
    #while (not testBottle.lineparseEventRecieved):
    #    pass
    testBottle.lineparseEventRecieved=False
            
    import random
    progress=random.randint(0,100)
    data={"progress":progress,"lastLine":testBottle.lastRecievedLine}
    callback=request.GET.get('callback', '').strip()
    response=callback+"("+str(data)+")"
    testBottle.logger.info("response %s",str(response))  
   
    #return response

""""""""""""""""""""""""""""""""""""
""" static files"""
""""""""""""""""""""""""""""""""""""
@testBottle.route('/:filename')
def static_file(filename):
    print("static ","filename",filename)
    send_file(filename, root=os.path.join(testBottle.path,'files',"static"))

@testBottle.route('/js/:path#.+#')
def server_static(path):
    send_file(path, root=os.path.join(testBottle.path,"files","static","js"))
    
@testBottle.route('/css/:path#.+#')
def server_static(path):
    send_file(path, root=os.path.join(testBottle.path,"files","static","css"))    


""""""""""""""""""""""""""""""""""""
def start_webServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 0))
    hostIp=s.getsockname()[0]
    testBottle.logger.critical("Server Started, listening on  %s:8000",str(hostIp))
    testBottle.host=hostIp+':8000'
    run(app=testBottle, host=hostIp, port=8000, server=TornadoServer)
