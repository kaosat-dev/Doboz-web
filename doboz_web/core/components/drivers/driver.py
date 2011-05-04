class Driver(object):
    """Driver class: intermediary element that formats commands according to a spec before they get sent to the connector"""
    def __init__(self):
        pass
        
    def format_data(self,datablock,*args,**kwargs):
        raise NotImplementedException("Please implement in sub class")
        