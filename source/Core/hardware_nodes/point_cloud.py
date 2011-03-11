import uuid
import os

class Point(object):
    """
    Simple 3d point storage
    """
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
    def __str__(self):
        string="%f,%f,%f" %(self.x,self.z,self.y)
        return string
    def alt_str(self):
        string="%f %f %f" %(self.x,self.z,self.y)
        return string
    
class PointBuffer(object):
    """
    Simple 3d point storage
    """
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
        
class PointCloud(object):
    """
    Simple 3d pointcloud storage
    """
    def __init__(self,width=0,length=0):
        self.points = []
        self.lines=[]
        self.width=width
        self.length=length
        """Maximum amount of points per line"""
    def add_point(self,point):
        self.points.append(point)    
    def __str__(self):
        string=",".join(str(pt) for pt in self.points)
        string='['+string+']'
        return string
    
    def save(self,path):
        string="\t\n".join(pt.alt_str() for pt in self.points)
        #if we have a name to save to or not 
        
        filePath=""
        if os.path.basename(path)!='':
            filePath=path
        else:
            fileName= str(uuid.uuid4())+".ptcld"
        
        filePath=os.path.join(path,fileName)
        file=open(filePath,'w')
        file.write("//X Y Z\t\n")
        file.write(string)
        file.close()
        

class Triangle(object):
    def __init__(self,pt1,pt2,pt3):
        self.point1=pt1
        self.point2=pt2
        self.point3=pt3
    def __str__(self):
        strRepr="Tri:["+str(self.point1)+"\r\n"+str(self.point2)+"\r\n"+str(self.point3)+"]\r\n"
        return strRepr
    
class Mesh(object):
    def __init__(self,pointCloud):
        self.pointCloud=pointCloud
        self.faces=[]
    def generate_faces(self):
        for index,point in enumerate(self.pointCloud.points):
            print(point)

class PointCloudBuilder(object):
    def __init__(self,precision=1,width=1,length=1,passes=1):
        self.width=width
        self.length=length
        self.precision=precision
        self.xOffset=precision
        self.yOffset=precision
        self.pointCloud=PointCloud(width,length)
        
        self.passes=passes
        self.currentPass=0
        
        self.rowIndex=0
        self.rows=int(length/precision)
        
        self.columnIndex=0
        self.columns=int(width/precision)
         
        self.forward=True       
        self.currentPoint=Point(0,0,0)
        
        self.totalColumnChanges=0
        self.finished=False;

    def add_point(self,z):  
        self.pointCloud.add_point(Point(self.currentPoint.x,self.currentPoint.y,z))
        self.currentPoint.z=z
        if self.currentPass<self.passes:
            if self.columnIndex<= self.columns:
                if self.forward:    
                    if self.rowIndex>=self.rows:
                        """
                        This is when the catesian bot switches direction to scan the next line
                        """
                        self.forward=not self.forward
                        self.columnIndex+=1
                        self.currentPoint.x+=self.xOffset
                        self.totalColumnChanges+=1
                        #print("changing column forward","total :", self.totalColumnChanges)
                    else:
                        self.rowIndex+=1
                        self.currentPoint.y+=self.yOffset
                else:
                    if self.rowIndex<=0:
                        self.forward=not self.forward
                        self.columnIndex+=1
                        self.currentPoint.x+=self.xOffset
                        self.totalColumnChanges+=1
                        #print("changing column back","total :", self.totalColumnChanges)
                    else:
                        self.rowIndex-=1
                        self.currentPoint.y-=self.xOffset
            else:
                #finished a pass
                self.currentPoint.x=0
                self.currentPoint.y=0
                self.rowIndex=0
                self.columnIndex=0
                self.currentPass+=1
        else:
            self.finished=True
            #self.currentPoint.x=0
            #self.currentPoint.y=0
    
    
   
    def add_point_simple(self,x,y,z):
        """
        Add a point, no calculation involved
        """
        self.pointCloud.add_point(Point(x,y,z))
    
    def generate_mesh(self):
        totalPoints=len(self.pointCloud.points)
        points=self.pointCloud.points
        print("total points",totalPoints)
        triangles=[]
        xIndex=0
        yIndex=0
        
        """First tri """
        for i in range(0,self.rows): 
            point1=points[yIndex]
            point2=points[2*self.rows-yIndex-1]
            point3=points[yIndex+1]
            tri=Triangle(point1,point2,point3)
            triangles.append(tri)
            print(str(tri))
            yIndex+=1
        
        


           
                    

if __name__=="__main__":
    Pt=point(2.1,0.2,3.5)
    print(Pt)