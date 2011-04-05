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
    
    def save(self,filePath):
        string="\t\n".join(pt.alt_str() for pt in self.points)
#        #if we have a name to save to or not 
#        
#        filePath=""
#        if os.path.basename(path)!='':
#            filePath=path
#        else:
#            fileName= str(uuid.uuid4())+".ptcld"
#        
#        filePath=os.path.join(path,fileName)
        file=open(filePath,'w')
        file.write("//X Y Z\t\n")
        file.write(string)
        file.close()
