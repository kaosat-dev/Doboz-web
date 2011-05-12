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
        self.requestSent=False
        self.answerComplete=False
        self.request=request
        self.answer=answer
        
    def __str__(self):
        return str(self.request)+" "+str(self.answer)
        #return "Special:"+ str(self.special)+", TwoStep:"+str(self.twoStep) +", Answer Required:"+str(self.answerRequired)+", Request:"+ str(self.request)+", Answer:"+ str(self.answer) 


class Driver(object):
    """Driver class: intermediary element that formats outgoing and incoming commands according to a spec before they get sent to the connector"""
    def __init__(self,speed=None,seperator="\n",bufferSize=8):
        self.logger = logging.getLogger("dobozweb.core.components.driver")
        self.logger.setLevel(logging.INFO)
        self.remoteInitOk=False
        self.bufferSize=bufferSize
        self.answerableCommandBuffer=[]
        self.commandBuffer=[]
        self.commandSlots=8
        
    def _format_data(self,datablock,*args,**kwargs):
        raise NotImplementedException("Please implement in sub class")
    
    def _handle_machineInit(self,datablock):
        raise NotImplementedException("Please implement in sub class")
        
    def handle_request(self,datablock,*args,**kwargs):
        cmd=Command(**kwargs)
        cmd.request=datablock
        if cmd.answerRequired and len(self.commandBuffer)<self.bufferSize+4:
            self.commandBuffer.append(cmd)
            if self.commandSlots>1:
                self.commandSlots-=1

        
    def get_next_command(self):
        cmd=None
        if self.remoteInitOk and len(self.commandBuffer)>0 and self.commandSlots>0:  
            tmp=self.commandBuffer[0]
            if not tmp.requestSent:            
                cmd=self._format_data(self.commandBuffer[0].request)
                tmp.requestSent=True
                self.logger.debug("Driver giving next command %s",str(cmd))
#            if not cmd.answerRequired:
#                pass
        else:
            if len(self.commandBuffer)>0:
                self.logger.critical("Buffer Size Exceed Machine capacity %s CommandSlots%s COMMANDBUFFER",str(len(self.commandBuffer)),str(self.commandSlots),[str(el) for el in self.commandBuffer])

        return cmd
        
        
    def handle_answer(self,datablock):
        #handles only commands that got an answer, formats them correctly and sets necesarry flags
        cmd=None        
        if not self.remoteInitOk:#machine not yet initialized
            self._handle_machineInit(datablock)
        else:       
            if len(self.commandBuffer)>0:
                try:
                    if self.commandBuffer[0].twoStep:  
                        self.commandBuffer[0].twoStep=False
                        cmd=self.commandBuffer[0]
                    else:
                        cmd=self.commandBuffer[0]
                        del self.commandBuffer[0]
                        cmd.answerComplete=True
                        cmd.answer=datablock
                        self.commandSlots+=1#free a commandSlot
                        
                except Exception as inst:
                    self.logger.critical("%s",str(inst))
            else:
                cmd=Command(answer=datablock)
                cmd.answerComplete=True
            self.logger.critical("%s",str(len(self.commandBuffer)))
        return cmd
     
           