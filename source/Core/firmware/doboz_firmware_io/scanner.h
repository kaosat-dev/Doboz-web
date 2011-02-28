#include <stdio.h>
#include <WProgram.h>

#ifndef SCANNER_H
#define SCANNER_H
class Scanner
{
  
  public:
  Scanner(int ioPort);
  void start();
  void stop();
  
  void request_data();
  void update();
  void scan();
  void set_callback(void (*callback)(int));
  
  private:
   void (*scanDoneCallback)(int);
   boolean scanRequested;
  boolean isRunning;
  boolean forwardPhase;
  int port;
  int xpos;
  int zpos;
  
  
  
  
};

#endif
