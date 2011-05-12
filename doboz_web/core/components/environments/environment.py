import os
import random
import logging
import imp
import inspect


from Core.HardwareNodesV2.hardware_node_manager import NodeManager 


#from pollapli.core.components.hardware_nodes import HardwareNode as hNode
import Core.HardwareNodes.sensor as sns
import Core.HardwareNodes.schedule as schd
from threading import Thread
import Queue

class Environment(object):
    def __init__(self,path,name,description="Add Description here",status="frozen"):
        self.logger=logging.getLogger("Pollapli.Core.EnvironmentManager.Environment")
        self.path=path
        self.name=name
        self.description=""
        self.status=status
        """hardware manager"""
        
        self.nodeManager=NodeManager()
        self.registered_types={}
        self.commandQueue=Queue.PriorityQueue
        
        self.registered_types["HardwareNode"]=hNode
        self.registered_types["Sensor"]=sns
        self.registered_types["Schedule"]=schd
        
    """
    ####################################################################################
    Configuration and shutdown methods
    """  
    def setup(self):
        """
        Function to instanciate the whole environment from disk (db)
        This is usually called at first start or after a server restart
        """
        self.logger.debug("Starting Configuring Environment '%s' ",self.name)
        #create db if not existent else just connect to it
        dbPath=self.path+os.sep+self.name+"_db"
        if not os.path.exists(dbPath):    
            self.db=db_manager_SQLLITE(dbPath)
            self.db.add_environment(self.name,self.description)
        else:
            self.db=db_manager_SQLLITE(dbPath)
            
      

        self.logger.info("Configuring Environment '%s': successfull",self.name)
        
    def tearDown(self):
        """
        Tidilly shutdown and cleanup after environment
        """
        self.nodeManager.tearDown()     


    def get_environmentInfo(self):
        return self.db.get_environmentInfo()
    """
    ####################################################################################
    The following functions are typically plugin related methods
    """ 
    def add_registered_hardwareTypes(self,hardwareTypes):
        """
        Adds the dictionary of validated hardwareTypes to the list of registered hardwareTypes
        """
        self.registered_types.update(hardwareTypes)
        
    def add_registered_converters(self,hardwareTypes):
        self.registered_converters.update(hardwareTypes)
        
  
        
    



    """
    ####################################################################################
    The following functions are typically hardware manager/hardware nodes and sensors related, pass through methods for the most part
    """  
    
    def add_node(self,type,name="",description="",params=None):
        """
        Add a hardware node to this environement, via its node manager (passthrough function)
        Params:
        title:the name of the node
        Desciption: short description of node
        NodeType: nodetype id
        """
      
        self.nodeManager.add_node(type,params)
        
    def remove_node(self,nodeId):
        """
        Remove a hardware node from this environement , via its node manager (passthrough function)
        Params:nodeId : the id of the node we want removed
        """
        self.nodeManager.remove_node(nodeId)
        
    def set_connectorToNode(self,nodeName):
        """
        Set a node's connector
        """
        #self.n
    
    def add_actor(self,title,description,type,mode,params,node,port):
        """
        Add an actor to this environement, via its node manager (passthrough function)
        Params:
        title:the name of the actor
        Desciption: short description of actor
        Mode: mode id
        Params: its working parameters
        Node: its parent node id
        """ 
        self.nodeManager.add_actor(node,params) 
          
    def remove_actor(self,actorId):
        """
        Remove a actor from this environement , via its node manager (passthrough function)
        Params:actorId : the id of the actor we want removed
        """
    
    def add_sensor(self,node,params):
        
        """
        Add a sensor to this environement, via its node manager (passthrough function)
        Params:
        title:the name of the sensor
        Desciption: short description of sensor
        Mode: mode id
        Node: its parent node id
        port: its pin/port (might be too arduino specific
        """ 
        self.nodeManager.add_sensor(node,params)   
        
    def remove_sensor(self,sensorId):
        """
        Remove a sensor from this environement , via its node manager (passthrough function)
        Params:sensorId : the id of the sensor we want removed
        """
        self.nodeManager.remove_sensor(sensorId)    
    
    def add_sensorType(self,title,description):
        """
        Add a sensor type to this environement : might be usefull to make this a passthrough method too , to have for example a dictionarry
        inside the node mgr which maps sensorType ids to their names or whatver
        Params:
        title:the name of the sensor type
        Desciption: short description of sensor type   
        """ 
        self.db.add_sensorType(title,description)
        
    def remove_sensorType(self,title):
        """
        Remove a sensor from this environement , via its node manager (passthrough function)
        Params:sensorId : the id of the node we want removed
        """
        self.db.delete_sensorType(title)   
    
    """
    ####################################################################################
    The following methods are typically called by the scheduler / or scheduler related
    """       
    
    #self.nodeManager.add_sensorSchedule(target,targetParams,startTime,function,functionparams,interval,title,description)
    #too db specific ?    
    def add_sensorSchedule(self,target,targetParams,startTime,function,functionparams,interval,name,description):  
        target=target.lower() 
#        if target == "environment":    
#            print("add task to environment")
#        elif target == "node":
#            print("add task to environment")
#        elif target == "sensor":
#            print("add task to sensor")   
        #print("locals",locals())
        
        sensorId=targetParams.get("sensorId",None) 
        nodeId=targetParams.get("nodeId",None) 
        #self.nodeManager.add_sensorSchedule(target,targetParams,startTime,function,functionparams,interval,name,description)
        self.nodeManager.add_sensorSchedule2(nodeId,sensorId,startTime,function,functionparams,interval,name,description)
    
    def remove_task(self,title):
        """
        Removes a task from the database as well as the scheduler
        """
        self.db.delete_task(title)
        
    def retrieve_data(self,sensorId):
        """
        Enqueue/call a data retrieval command on one sensor: this should NOT be blocking, but asynch
        """
        self.nodeManager.retieve_data(sensorId)
        
    def get_sensorData(self,nodeId,sensorId,startDate,endDate):
        pass    
        
    #too arduino specific
    def set_portDependency(self,port,parentPort,threshold,compareType):
        pass
    
    def set_trigger(self,slave,master,threshold,compareType):
        pass
    
    
    
    