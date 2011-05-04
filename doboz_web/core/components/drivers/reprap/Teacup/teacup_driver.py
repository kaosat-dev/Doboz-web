from doboz_web.core.components.drivers.driver import Driver

class TeacupDriver(Driver):
    """Driver class: intermediary element that formats commands according to a spec before they get sent to the connector"""
    def __init__(self):
        Driver.__init__(self)
        
    def format_data(self,datablock,*args,**kwargs):
        datablock=datablock.split(';')[0]
        datablock=datablock.strip()
        datablock=datablock.replace(' ','')
        datablock=datablock.replace("\t",'')

        return datablock+ "\n"
        