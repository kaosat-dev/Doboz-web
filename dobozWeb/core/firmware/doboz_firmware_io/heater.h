#include <stdio.h>
#include <WProgram.h>
#ifndef PINMAPPER_H
#include "PinMapper.h"
#endif

/*
Heater class: manages a heating element, whether it is the extuder heater or the heated bed etc
*/
#ifndef HEATER_H
#define HEATER_H
class Heater
{
  private:
    PinMapper *pinMapper;
    int  heater_pin;
    int sensor_pin;
    

    int temperature;
    int target_temperature;
    int max_temperature;
    
    //for PID:
    long previousTime;
    float error;
    float previousError;
    float integral;
    float Kp;//proportionnal constant
    float Ki;//integral constant
    float Kd;//derivative constant 
    
    boolean bangBang;
    boolean targetTemperatureReached;
    void (*TemperatureReachedCallback)(void);
    void (*TemperatureRequestedCallback)(int);
    boolean temperatureRequested;
    boolean CallbackCalled;
    
   public:
     Heater();
     Heater(PinMapper *pinMapr,int heaterPin, int sensorPin, int targetTemperature,float kp,float ki, float kd, boolean bangBang);
     void update();
     void start();
     void stop();
     
     
     void read_temperature();
     int get_temperature();
     void set_target_temperature(int target);
     void set_max_temperature(int max);
     void set_callback(void (*callback)(void));
     
     void set_tempRequestedcallback(void (*callback)(int));
     void requestTemperature();
     
     void do_pid();
};
#endif
