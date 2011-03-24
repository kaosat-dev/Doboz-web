#include "heater.h"


#define NUMTEMPS 20
short tempTable[NUMTEMPS][2] = {
   {1, 841},
   {54, 255},
   {107, 209},
   {160, 184},
   {213, 166},
   {266, 153},
   {319, 142},
   {372, 132},
   {425, 124},
   {478, 116},
   {531, 108},
   {584, 101},
   {637, 93},
   {690, 86},
   {743, 78},
   {796, 70},
   {849, 61},
   {902, 50},
   {955, 34},
   {1008, 3}
};



Heater::Heater()
{
  target_temperature=temperature= max_temperature=0;
  error=0;
  CallbackCalled=true;
  targetTemperatureReached=false;
  temperatureRequested=false;

}

Heater::Heater(PinMapper *pinMapr,int heaterPin, int sensorPin, int targetTemperature,float nkp,float nki, float nkd,boolean bangbang)
{
  pinMapper= pinMapr;
  heater_pin=heaterPin;
  sensor_pin=sensorPin;
  bangBang=bangbang;
  
  //pinMode(sensor_pin,OUTPUT);
  //pinMode(heater_pin,OUTPUT);
  
  target_temperature=targetTemperature;
  temperature=0;
  previousTime=millis();
  
  error=0;
  Kp=nkp;
  Ki=nki;
  Kd=nkd;
  CallbackCalled=true;
  targetTemperatureReached=false;
  temperatureRequested=false;

  
}

void Heater::start()
{
  //BIT_SET(heater_pin,HIGH
  
 // analogWrite(heater_pin,HIGH);
}

void Heater::stop()
{
  //digitalWrite(heater_pin,LOW);
}

void Heater::update()
{
    if(temperatureRequested)
    {
      TemperatureRequestedCallback(temperature);
      temperatureRequested=false;
    }
  
   if(abs(temperature-target_temperature)<2)
         {
           
           if(!CallbackCalled)
           {
           TemperatureReachedCallback();
           CallbackCalled=true;
           }
         }
         
         
  
  
  long currentTime=millis();
  long timeDelta=currentTime-previousTime;
  
  if(timeDelta>10)
  {  
     read_temperature();  
     if(bangBang)
    {
      if(temperature<=target_temperature)
      {
       pinMapper->A_WRITE( heater_pin,255);
      }
      else
      {
      pinMapper->A_WRITE( heater_pin,0);
      }
    }
    else
    {
      float dt = 0.001*(float)(timeDelta);
      error = (float)(target_temperature - temperature);
      integral += error*dt;
      float derivative = (error - previousError)/dt;
      previousError = error;
      
      int output = (int)(error*Kp + integral*Ki + derivative*Kd);
      output = constrain(output, 0, 255);
      
      
     previousTime=currentTime;
    
   
     pinMapper->A_WRITE( heater_pin,output);
    }
   
   // Serial.println(temperature);
  }
  
 
}



void Heater::read_temperature()
{

   int raw = 0;
  for(int i = 0; i < 3; i++)
    raw += pinMapper->A_READ( sensor_pin);
    
  raw = raw/3;
 
    byte i;

  // TODO: This should do a binary chop

  for (i=1; i<NUMTEMPS; i++)
  {
    if (tempTable[i][0] > raw)
    {
      temperature  = tempTable[i-1][1] + 
        (raw - tempTable[i-1][0]) * 
        (tempTable[i][1] - tempTable[i-1][1]) /
        (tempTable[i][0] - tempTable[i-1][0]);

      break;
    }
  }

  // Overflow: Set to last value in the table
  if (i >= NUMTEMPS) temperature = tempTable[i-1][1];


}

//returns the current temperature
int Heater::get_temperature()
{
  return temperature;
}

void Heater::set_target_temperature(int targetTemperature)
{
  target_temperature=targetTemperature;
  CallbackCalled=false;

  previousTime = millis();
  previousError = 0;
  integral = 0;  

}

void Heater::requestTemperature()
{
  temperatureRequested=true;
}

void Heater::set_max_temperature(int maxTemperature)
{
  max_temperature=maxTemperature;
}

void Heater::do_pid()
{
 // analogWrite(heater_pin,255);
}

void Heater::set_callback(void (*callback)(void))
{
   TemperatureReachedCallback=callback; 
   
}

void Heater::set_tempRequestedcallback(void (*callback)(int))
{
  TemperatureRequestedCallback=callback;
}
