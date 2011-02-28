import logging
import os
import sys
import time


from bottle import Bottle, route, run
from bottle import send_file, redirect, abort, request, response
from bottle import TornadoServer
import bottle

from reprap_manager import ReprapManager
from point_cloud import PointCloudBuilder,PointCloud,Point




testBottle = Bottle()
testBottle.path=os.path.join(os.path.abspath("."),"Core","print_server")
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

@testBottle.route('/gcodeFiles' , method='GET')
def get_gcodeFiles():
    testBottle.logger.info("fetching gcode files")
    callback=request.GET.get('callback', '').strip()
    testBottle.logger.info("callback %s",str(callback))

    fileList=os.listdir(os.path.join(testBottle.path,"files","machine","printFiles"))
    data={"files": fileList}
    response=callback+"("+str(data)+")"
    #testBottle.logger.info("response %s",str(response))
    return response

@testBottle.route('/scanFiles' , method='GET')
def get_scanFiles():
    testBottle.logger.info("fetching scan files")
    callback=request.GET.get('callback', '').strip()
    testBottle.logger.info("callback %s",str(callback))

    fileList=os.listdir(os.path.join(testBottle.path,"files","machine","scanFiles"))
    data={"files": fileList}
    response=callback+"("+str(data)+")"
    testBottle.logger.info("response %s",str(response))
    return response


@testBottle.route('/printcommands/:command' , method='GET')
def printing(command):
    
    callback=request.GET.get('callback', '').strip()
    response=callback+"()"
    
    if command=="start":
        testBottle.logger.critical("User Requested print")
        if not testBottle.reprapManager.isStarted:
            testBottle.logger.info("starting print")
            fileName=request.GET.get('fileName', '').strip()
            testBottle.logger.info("filename %s",fileName)
            fileToPrint=os.path.join(testBottle.path,"files","machine","printFiles",fileName)
            testBottle.logger.info("filename %s",fileToPrint)
            print("pouet")
            try:     
                testBottle.reprapManager.set_sourcePath(fileToPrint)
                testBottle.reprapManager.start()
            except Exception as inst:
                testBottle.logger.critical("error in print start %s",str(inst))
    elif command=="startpause":
        try:
            testBottle.reprapManager.startPause()
        except Exception as inst:
            testBottle.logger.info("error in scan startpause %s",str(inst))    
    elif command=="stop":
        testBottle.reprapManager.stop()
    elif command=="progress":
        
        lastIndex=int(request.GET.get('LastIndex', '').strip())
        blockSize=int(request.GET.get('blockSize', '').strip())

       # testBottle.logger.critical("lastIndex %g, blocksize %g",lastIndex,blockSize)  
        try:
            points=testBottle.reprapManager.positionList[lastIndex:lastIndex+blockSize]
            points=",".join(str(pt) for pt in points)
            points='['+points+']'
            progress=testBottle.reprapManager.progress
            data={"jobType":'print',"progress":progress,"positions":str(points)}
            response=callback+"("+str(data)+")"
            #testBottle.logger.critical("print progress info %s",str(testBottle.reprapManager.positionList))  
        except Exception as inst:
            testBottle.logger.critical("error in getting print progress %s",str(inst))
        #data={"progress":testBottle.reprapManager.progress,"positions":str(testBottle.reprapManager.positionList),"lastCommand":testBottle.reprapManager.lastLine or "","file":os.path.basename(testBottle.reprapManager.sourcePath)}
        #response=callback+"("+str(data)+")"
    elif command=="manual":
        try:     
            gcode=request.GET.get('gcode', '').strip()
            testBottle.reprapManager.sendText(gcode)
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
        scanResolution=float(request.GET.get('resolution', '').strip())
        print("width",width,"height",height,"res",scanResolution)
        try:     
            testBottle.reprapManager.scan(width,height,scanResolution)
        except Exception as inst:
            testBottle.logger.info("error in starting scan %s",str(inst))     
    elif command=="startpause":
        try:
            testBottle.reprapManager.startPause()
        except Exception as inst:
            testBottle.logger.info("error in scan startpause %s",str(inst))
    elif command=="stop":
        try:
            testBottle.reprapManager.stop()
        except Exception as inst:
            testBottle.logger.info("error in stopping scan %s",str(inst))
    elif command=="status":
        try:
            data={"progress":testBottle.reprapManager.progress,"lastCommand":testBottle.reprapManager.lastLine or ""}
            response=callback+"("+str(data)+")"
            testBottle.logger.info("response %s",str(response))  
        except Exception as inst:
            testBottle.logger.info("error in getting scan status  %s",str(inst))
    elif command=="progress":
        lastIndex=int(request.GET.get('LastIndex', '').strip())
        blockSize=int(request.GET.get('blockSize', '').strip())
        testBottle.logger.info("lastIndex %s",str(lastIndex))  
        try:
            truc=testBottle.reprapManager.pointCloudBuilder.pointCloud.points[lastIndex:lastIndex+blockSize]
            truc=",".join(str(pt) for pt in truc)
            truc='['+truc+']'
            progress=testBottle.reprapManager.progress
            data={"jobType":'scan',"progress":progress,"positions":str(truc)}
            response=callback+"("+str(data)+")"
            testBottle.logger.info("response %s",str(response))  
        except Exception as inst:
            testBottle.logger.info("error in getting scan progress %s",str(inst))

    return response



@testBottle.route('/uploads/:filename')
def download(filename):
    testBottle.logger.info("pouet %s, path: %s",filename,str(os.path.join(testBottle.path,"files","uploads")))
    send_file(filename, root=os.path.join(testBottle.path,"files","machine","scanFiles"), download=filename)
  

@testBottle.route('/commands/:command' , method='GET')
def generalCommands(command):
    testBottle.reprapManager.sendText("M105")
    testBottle.reprapManager.sendText("M143")
    callback=request.GET.get('callback', '').strip()
    response=callback+"()"
    try:
       
        data={"headTemp":testBottle.reprapManager.headTemp,"bedTemp":testBottle.reprapManager.bedTemp,"lastCommand":testBottle.reprapManager.lastLine or ""}
        response=callback+"("+str(data)+")"
    except Exception as inst:
        testBottle.logger.info("error in getting machine status %s",str(inst))
    
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
    run(app=testBottle, host='localhost', port=8000, server=TornadoServer)
