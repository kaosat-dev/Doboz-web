NextPointContinuous=0##do a line , then continue back with column offset
NextPointBackAndForth=1#do a line , then move back + column offset and start new line in the same direction as the first

LocalPasses=0#do consecutive passes on same point before moving on to the next one
GlobalPasses=1#do consecutive passes on point cloud before redoing it s
import logging

from core.Tools.point_cloud2 import *

class PointCloudBuilder(object):
    def __init__(self,resolution=1,width=1,length=1,passes=1,passMethod=0,nextPointMethod=0,passCombineMethod=0):
        self.logger=logging.getLogger("Doboz.core.PointCloudBuilder")
        self.resolution=resolution
        self.width=width
        self.length=length
        self.passes=passes
        self.passMethod=passMethod
        self.nextPointMethod=nextPointMethod
        self.passCombineMethod=passCombineMethod
        
        self.currentPass=0

        
        if self.resolution==0:
            raise Exception("Precision can't be zero")
        
        self.rowIndex=0
        self.rows=int(length/resolution)
        
        self.columnIndex=0
        self.columns=int(width/resolution)
        
        self.currentPoint=Point(0,0,0)
        self.finished=False
        
        self.pointCloud=PointCloud();
        self.pointIndex=0
        
        self.Even=True
        
         
    def add_point(self,z):
        if self.passCombineMethod==0:
            self.currentPoint.z=z
            self.pointCloud.add_point(Point(self.currentPoint.x,self.currentPoint.y,z))
        elif self.passCombineMethod==1:
            if self.currentPass==0:
                self.pointCloud.add_point(Point(self.currentPoint.x,self.currentPoint.y,z/self.passes))
            else:
                self.pointCloud.points[self.pointIndex].z+=z/self.passes
  
    def next_point_continuous(self):
        """
        If it is even move forward,else move "backwards"
        """
        self.pointIndex+=1
        if self.Even:
            self.currentPoint.y+=self.resolution
            if self.currentPoint.y>self.length:
                self.currentPoint.y=self.length
                self.currentPoint.x+=self.resolution 
                self.Even=not self.Even
        else:
            self.currentPoint.y-=self.resolution
            if self.currentPoint.y<0:
                self.currentPoint.y=0
                self.currentPoint.x+=self.resolution 
                self.Even=not self.Even
                
        if self.currentPoint.x>self.width:
            #if all passes done, scan is done, if not , restart
            self.currentPass+=1
            if self.currentPass>=self.passes:
                self.finished=True
            else:
                self.currentPoint.x=0
                self.currentPoint.y=0
                self.pointIndex=0        
                    
    def next_point_backandforth(self):
        """
        After each column's end ; increases column index and position, and goes back to row zero
        """
        self.currentPoint.y+=self.resolution
        if self.currentPoint.y>self.length:
            self.pointIndex+=1
            self.currentPoint.y=0  
            self.currentPoint.x+=self.resolution  
            
        if self.currentPoint.x>self.width:
            #if all passes done, scan is done, if not , restart
            self.currentPass+=1
            if self.currentPass>=self.passes:
                self.finished=True
            else:
                
                self.currentPoint.x=0
                self.currentPoint.y=0
                self.pointIndex=0
            
                
            
            