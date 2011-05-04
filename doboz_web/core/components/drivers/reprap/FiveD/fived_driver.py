from doboz_web.core.components.drivers.driver import Driver

class FiveDDriver(Driver):
    """Driver class: intermediary element that formats commands according to a spec before they get sent to the connector"""
    def __init__(self):
        Driver.__init__(self)
        self.currentLine=1
        
    def format_data(self,datablock,*args,**kwargs):
        """
        Cleanup gcode : remove comments and whitespaces
        """
        
        datablock=datablock.split(';')[0]
        datablock=datablock.strip()
        datablock=datablock.replace(' ','')
        datablock=datablock.replace("\t",'')

        """RepRap Syntax: N<linenumber> <cmd> *<chksum>\n"""
        datablock = "N"+str(self.currentLine)+' '+datablock+''
        print("datablock",datablock)
        """ chksum = 0 xor each byte of the gcode (including the line number and trailing space)
        """     
        checksum = 0
        for c in datablock:
            checksum^=ord(c)
            
        self.currentLine+=1
        
        return datablock+'*'+str(checksum)+"\n"
        