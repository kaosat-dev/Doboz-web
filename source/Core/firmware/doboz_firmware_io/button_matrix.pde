#include "button_matrix.h"
byte bMap[]={101,111,11,1,  101,111,11,1,  10,100,0,110,  10,100,0,110};


Button::Button()
{
  truthTable=NULL;
  pressed=false;
  buttonPressed=NULL;
}

Button::Button(byte truthT)
{
  truthTable=truthT;
  pressed=false;
  buttonPressed=NULL;
}


ButtonMatrix::ButtonMatrix()
{
  
  buttonMap[0]=Button(B00000101);
  buttonMap[1]=Button(B00000111);
  buttonMap[2]=Button(B00000011);
  buttonMap[3]=Button(B00000001);
  buttonMap[4]=Button(B00000101);
  buttonMap[5]=Button(B00000111);
  buttonMap[6]=Button(B00000011);
  buttonMap[7]=Button(B00000001);
  buttonMap[8]=Button(B00000010);
  buttonMap[9]=Button(B00000100);
  buttonMap[10]=Button(B00000000);
  buttonMap[11]=Button(B00000110);
  buttonMap[12]=Button(B00000010);
  buttonMap[13]=Button(B00000100);
  buttonMap[14]=Button(B00000000);
  buttonMap[15]=Button(B00000110);
  //#define buttonMap={101,111,11,1,  101,111,11,1,  10,100,0,110,  10,100,0,110};
 //buttonPressed=&toto;*/
}
ButtonMatrix::ButtonMatrix(uint8_t inPin)
{
  buttonMap[0]=Button(B00000101);
  buttonMap[1]=Button(B00000111);
  buttonMap[2]=Button(B00000011);
  buttonMap[3]=Button(B00000001);
  buttonMap[4]=Button(B00000101);
  buttonMap[5]=Button(B00000111);
  buttonMap[6]=Button(B00000011);
  buttonMap[7]=Button(B00000001);
  buttonMap[8]=Button(B00000010);
  buttonMap[9]=Button(B00000100);
  buttonMap[10]=Button(B00000000);
  buttonMap[11]=Button(B00000110);
  buttonMap[12]=Button(B00000010);
  buttonMap[13]=Button(B00000100);
  buttonMap[14]=Button(B00000000);
  buttonMap[15]=Button(B00000110);
 //shiftRegOne=shiftReg;
 inputPin=inPin;
 
}

void ButtonMatrix::setCallback(int index, void(*callBck)(void))
{
  buttonMap[index].buttonPressed=callBck;
}

void ButtonMatrix::update()
{
   now=micros();
   if(now-then>80000)
   {
     wait_till_ulocked();
     shiftRegLocked=true;
     
     byte shiftRegTwoAlt=0x04;//1st and 3rd line scans 
    for(int i=0;i<16;i++)
    {
      int line=i/4;
      if(line==0 || line==2)
     {
       shiftRegTwoAlt=0x04;
     } 
     else if(line==1 || line==3)
     {
       shiftRegTwoAlt=0x08;
     }
    
   
    byte tmpBut=bMap[i]<<5;//we only concern ourselves with the 3 highest bits   

  //clear the slave 4051 ports
   shiftRegOne&=0x1F;
   //use the current truth table
   shiftRegOne|=tmpBut;
   
   

   BIT_CLR(PORTB,0);
   shiftOut(dataPin, clockPin, MSBFIRST, shiftRegTwoAlt);//
    shiftOut(dataPin, clockPin, MSBFIRST, shiftRegOne);
    BIT_SET(PORTB,0);
   shiftRegLocked=false;  
   if(analogRead(inputPin)>100)
   {  
     
     if(buttonMap[i].buttonPressed!=NULL)
     {
       buttonMap[i].buttonPressed();
     }
   }
   
}
then=now;
} 
}


void ButtonMatrix::clear_callbacks()
{
  for(int i=0;i<16;i++)
  {
    buttonMap[i].buttonPressed=NULL;
  }
}

