from pyparsing import *
from decimal import *  
#(Word, Literal, CaselessLiteral, Combine, Optional, nums, StringEnd,operatorPrecedence, opAssoc,ParserElement) 
#ParserElement.enablePackrat()

class GCodeParser(object):
    def convertIntegers(self,tokens):
        return int(tokens[0])
    def convertFloats(self,tokens):
        return Decimal(tokens[0])
    
    
    
    def parse(self,line):
        result=None
    
        caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        point = Literal('.')
        plusorminus = Literal('+') | Literal('-')
        number = Word(nums).setParseAction( self.convertIntegers )
        integer = Combine(Optional(plusorminus) + number).setParseAction( self.convertIntegers )
        floatnumber = Combine(integer + 
                           Optional(point + Optional(number)) + 
                           Optional(integer)
                         ).setParseAction( self.convertFloats )
    
        prefix=(Word(caps)("key")+number("value"))("prefix")
        subelement=Optional((Word(caps)("ty") +floatnumber("value")) , default="None")("element")
            
        xcmd=Optional((Literal('X')("key")+floatnumber("value")) , default=None)("xcmd")
        ycmd=Optional((Literal('Y')("key")+floatnumber("value")) , default=None)("ycmd")
        zcmd=Optional((Literal('Z')("key")+floatnumber("value")) , default=None)("zcmd")
        ecmd=Optional((Literal('E')("key")+floatnumber("value")) , default=None)("ecmd")        
        fcmd=Optional((Literal('F')("key")+floatnumber("value")) , default=None)("fcmd")   
        scmd=Optional((Literal('S')("key")+floatnumber("value")) , default=None)("scmd")     
    
        subcmd=prefix+(xcmd+ycmd+zcmd+ecmd+fcmd+scmd)("subs")
        commands=[]   
        val=0
        try:            
            content=subcmd.parseString(line)
            result=content
        except:
            pass
        return result