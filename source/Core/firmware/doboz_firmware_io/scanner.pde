#include "scanner.h"

Scanner::Scanner(int ioPort)
{
   port=ioPort; 
   xpos=0;
   zpos=0;
   isRunning=false;
   forwardPhase=true;
   scanRequested=false;
}
void Scanner::set_callback(void (*callback)(int))
{
   scanDoneCallback=callback; 
   
}

void Scanner::request_data()
{
  scanRequested=true;
}

void Scanner::scan()
{
  int height=A_READ(port);
  scanDoneCallback(height);
  scanRequested=false;
}
void Scanner::start()
{
    isRunning=true;
    xpos=0;
   zpos=0;
    forwardPhase=true;
}
void Scanner::stop()
{
   xpos=0;
   zpos=0;
   isRunning=false;
   forwardPhase=true;
   Wire.beginTransmission(OTHER_ADDRESS);
         Wire.send(STOP);
         Wire.endTransmission();
}

void Scanner::update()
{
  if(scanRequested)
  {
    scan();
  }
  
}
