#include "PinMapper.h"


//alternate analogRead to simplify access to ports (and specifically, muxed/shift register ports)
int PinMapper::A_READ(int pin)
{
  if(pin<32)//if the pin is an undirect, muxed pin
  {
    int demuxer=4;//needs to be replaced with something dynamic
    byte demuxr=B00010000;
    if(pin<8)
    {
      demuxer=4;
      demuxr=B00010000;
    }
    else
    {
      demuxer=5;
      demuxr=B00010100;
    }
 
  byte port=portMap[pin%8];
  port=port<<5;
  //needs to be replaced with the 3 lsb of the muxer 
  port|=demuxr;
  
  BIT_CLR(PORTB,0);
 shiftOut(dataPin, clockPin, MSBFIRST, 0x00);//first shiftout for control pannel
 shiftOut(dataPin, clockPin, MSBFIRST, port);
 BIT_SET(PORTB,0);
 return analogRead(mainAnalog);
  }
  else
  {
    return analogRead(pin-32);
  }
} 

//alternate analogWrite, see above
void PinMapper::A_WRITE(int pin,int value)
{
 
  if(pin<32)//if the pin is an undirect, muxed pin
  {
  int demuxer=4;//needs to be replaced with something dynamic
  byte port=portMap[pin/8];
  port=port<<5;
  //needs to be replaced with the 3 lsb of the muxer
  port|=B00010000;
  
  BIT_CLR(PORTB,0);
 shiftOut(dataPin, clockPin, MSBFIRST, 0x00);//first shiftout for control pannel
 shiftOut(dataPin, clockPin, MSBFIRST, port);
 BIT_SET(PORTB,0);
 analogWrite(mainAnalog,value);
  }
  else
  {
    int realPin=pin-32;
    analogWrite(realPin,value);
  }
} 


//alternate digitalRead , see above
int PinMapper::D_READ(int pin)
{
  if(pin<32)//if the pin is an undirect, muxed pin
  {
  int demuxer=4;//needs to be replaced with something dynamic
  byte port=portMap[pin/8];
  port=port<<5;
  //needs to be replaced with the 3 lsb of the muxer
  port|=B00010000;
  
 BIT_CLR(PORTB,0);
 shiftOut(dataPin, clockPin, MSBFIRST, 0x00);//first shiftout for control pannel
 shiftOut(dataPin, clockPin, MSBFIRST, port);
 BIT_SET(PORTB,0);
 return digitalRead(mainAnalog);
  }
  else
  {
   return digitalRead(pin-32); 
  }
}
//alternate digitalWrite , see above
void PinMapper::D_WRITE(int pin,boolean highLow)
{
  if(pin<32)//if the pin is an undirect, muxed pin
  {
    
  BIT_CLR(PORTB,0);
 shiftOut(dataPin, clockPin, MSBFIRST, 0x00);//first shiftout for control pannel
 shiftOut(dataPin, clockPin, MSBFIRST, B01110000);
 BIT_SET(PORTB,0);
 if(highLow)
 {
   BIT_SET(PORTC,3);
 }
 else
 {
   BIT_CLR(PORTC,3);
 }
 }
 else
 {
      if(highLow)
     {
       //find a way to find the port, and index
       //BIT_SET(PORTC,3);
     }
     else
     {
       //BIT_CLR(PORTC,3);
     }
 }
}


