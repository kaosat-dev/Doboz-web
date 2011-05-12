from doboz_web.core.components.drivers.driver import Driver

class FiveDDriver(Driver):
    """Driver class: intermediary element that formats commands according to a spec before they get sent to the connector"""
    def __init__(self,category="reprap",speed=19200,seperator="\n",bufferSize=8):
        Driver.__init__(self,category=category,speed,seperator,bufferSize)
        self.currentLine=1
        
    def _handle_machineInit(self,datablock):
        if "start" in datablock :
            self.remoteInitOk=True
            self.logger.critical("Machine Initialized")
        else:
            raise Exception("Machine NOT INITIALIZED")
    def _format_data(self,datablock,*args,**kwargs):
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
        