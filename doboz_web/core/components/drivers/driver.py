import logging

class Command(object):
    """Base command class, encapsulate all request and answer commands, also has a 'special' flag for commands that do no participate in normal flow of gcodes : i
    ie for example , regular poling of temperatures for display (the "OK" from those commands MUST not affect the line by line sending/answering of gcodes)
    """
    def __init__(self,special=False,twoStep=False,answerRequired=False,request=None,answer=None):
        """
        Params:
        special: generally used for "system" commands such as M105 (temperature read) as oposed to general, print/movement commands
        TwoStep: used for commands that return data in addition to "Ok"
        AnswerRequired: for commands that return an answer
        AnswerComplete: flag that specified that an answer is complete
        Request: OPTIONAL: the sent command
        Answer: what answer did we get
        """
        self.special=special
        self.twoStep=twoStep
        self.answerRequired=answerRequired
        self.answerComplete=False
        self.request=request
        self.answer=answer
        
    def __str__(self):
        return str(self.answer)
        #return "Special:"+ str(self.special)+", TwoStep:"+str(self.twoStep) +", Answer Required:"+str(self.answerRequired)+", Request:"+ str(self.request)+", Answer:"+ str(self.answer) 


class Driver(object):
    """Driver class: intermediary element that formats outgoing and incoming commands according to a spec before they get sent to the connector"""
    def __init__(self,speed=None,seperator="\n",bufferSize=8):
        self.logger = logging.getLogger("dobozweb.core.components.driver")
        self.logger.setLevel(logging.INFO)
        self.remoteInitOk=False
        self.commandBuffer=[]
        self.waitBuffer=[]

        
    def format_data(self,datablock,*args,**kwargs):
        raise NotImplementedException("Please implement in sub class")
    
    def handle_machineInit(self,datablock):
        raise NotImplementedException("Please implement in sub class")
        
    def handle_request(self,datablock,*args,**kwargs):
        if 'answerRequired' in kwargs:    
            if kwargs['answerRequired'] :
                self.commandBuffer.append(Command(**kwargs))
                                      
        return self.format_data(datablock)
        
    def handle_answer(self,datablock):
        #handles only commands that got an answer, formats them correctly and sets necesarry flags
        cmd=None        
        if not self.remoteInitOk:#machine not yet initialized
            self.handle_machineInit(datablock)
        else:       
            if len(self.commandBuffer)>0:
                try:
                    if self.commandBuffer[len(self.commandBuffer)-1].twoStep:  
                        self.commandBuffer[len(self.commandBuffer)-1].twoStep=False
                        cmd=self.commandBuffer[len(self.commandBuffer)-1]
                    else:
                        cmd=self.commandBuffer.pop()
                        cmd.answerComplete=True
                        cmd.answer=datablock
                except Exception as inst:
                    self.logger.critical("%s",str(inst))
            else:
                cmd=Command(answer=datablock)
                cmd.answerComplete=True
            self.logger.critical("%s",str(len(self.commandBuffer)))
        return cmd
     
           