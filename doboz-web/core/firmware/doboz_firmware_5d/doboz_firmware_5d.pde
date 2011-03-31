
//#define TIMER_CLOCK_FREQ 2000000.0 //2MHz for /8 prescale from 16MHz
#include <ctype.h>
#include <stdio.h>
#include <avr/pgmspace.h>

#include "stepper.h"
#include "configuration.h"
#include "commands.h"
#include "helpers.h"
#include "GCode_interpreter.h"
#include "dda.h"
#include <WString.h>
#include <avr/pgmspace.h>

bool running=false;


//Stepper steppers[4];

#define BIT_SET(REG, bit)                    ( REG |= (1UL << (bit) ) )

#define BIT_CLR(REG, bit)                    ( REG &= ~(1UL << (bit) ) )

#define BIT_TST(REG, bit, val)              ( ( (REG & (1UL << (bit) ) ) == ( (val) << (bit) ) ) )

//I2c com
#define THIS_ADDRESS 0x9
#define OTHER_ADDRESS 0x8

#include <Wire.h>

GCodeInterpreter interp;
dda DDa;


//temporary cheat

void set_ExtruderTemp(int temperature)
{
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send('E');
  Wire.send(temperature);
  Wire.endTransmission();
}

void set_BedTemp(int temperature)
{
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send('B');
  Wire.send(temperature);
  Wire.endTransmission();
}



void get_ExtruderTemp()
{
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send('U');
  Wire.endTransmission();
}

void get_BedTemp()
{
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send('V');
  Wire.endTransmission();
}

void request_3dPoint()
{
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send('D');
  Wire.endTransmission();
}





  String tmp="";
  String confirmation = "";

long now;
long then;

void setup()
{
  DDRC = DDRC | B11111111;
  DDRB = DDRB | B11111111;
  DDRD = DDRD | B11110000;
  


  Serial.begin(19200);
  Serial.println("start");
  
  DDa=dda();
  interp=GCodeInterpreter(&DDa);
  Wire.begin(THIS_ADDRESS);
  Wire.onReceive(receiveEvent);  
  then=millis();

}


#include "commands.h"

void loop()
{

 
  DDa.dda_step();
  
  uint8_t c;
  if (Serial.available() > 0)
  {
   
    c = Serial.read();
    interp.addToCommand(c);
    then=millis();
    
  }
  else
  {
    if (!DDa.isLive())
    {
      now=millis();
       if(now-then>10000)
       {
         DDa.disable_steppers();
       }
    }
    else
    {
       then=millis();
    }
  }
}

void handleCommand(int command,int value)
{
  switch(command)
    {
      /*case MOVE_LEFT:
       steppers[1].set_dir(true);
       steppers[1].start();  
      break;
      case MOVE_RIGHT:
       steppers[1].set_dir(false);
       steppers[1].start();
      break;
      case MOVE_FORWARD:
      steppers[2].set_dir(false);
        steppers[2].start();  
      break;
      case MOVE_BACK:
      steppers[2].set_dir(true);
       steppers[2].start();
      break;
      case MOVE_UP:
      steppers[3].set_dir(true);
       steppers[3].start();
       break;
      case MOVE_DOWN:
      steppers[3].set_dir(false);
       steppers[3].start();
       break; 
      case EXTRUDE_FORWARD:
      steppers[0].set_dir(false);
       steppers[0].start();
       break;
      case EXTRUDE_BACK:
      steppers[0].set_dir(true);
       steppers[0].start();
       break;
      case STOP:
      steppers[0].stop();
      steppers[1].stop(); 
      steppers[2].stop(); 
      steppers[3].stop(); 
      break;*/
      case BED_TEMP_REACHED:
      //Serial.println("bed temp reached");
      
      break;
      
      case HEAD_TEMP_REACHED:
     // Serial.println("head temp reached");
      //Serial.println("ok");
      break;
      
      case 'u'://got head temp
          //char buf[16];
         //sprintf(buf, "M105 %3d", value);
          tmp=String(value);
          confirmation =  String("M105 "+ tmp); 
         Serial.println(confirmation);
         
      break;
      
       case 'v'://got bed temp
         tmp=String(value);
         confirmation =  String("M143 "+ tmp); 
        Serial.println(confirmation);
      break;
      
      case 'd':
        tmp=String(value);
        confirmation =  String("M180 height: "+ tmp+" ok"); 
         //char buf2[16];
         //sprintf(buf, "M180 height: %4d ok", value);
         Serial.println(confirmation);   
      break;
    }
}

void receiveEvent(int howMany)
{
  
  while (Wire.available() > 0)
  {
    char c = Wire.receive();
    int v=Wire.receive();
    handleCommand(c,v);
    
  }
 
}




