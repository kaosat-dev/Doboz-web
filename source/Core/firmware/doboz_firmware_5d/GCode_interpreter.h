#ifndef GCODEINTERPRETER_H
#define GCODEINTERPRETER_H


#include "vectors.h"
#include "dda.h"
#include <WProgram.h>
#define COMMAND_SIZE 128


/* gcode line parse results */
struct GcodeParser
{
    unsigned int seen;
    int G;
    int M;
    int T;
    float P;
    float X;
    float Y;
    float Z;
    float E;
    float I;
    float J;
    float F;
    float S;
    float R;
    float Q;
    int Checksum;
    long N;
    long LastLineNrRecieved;
};

class GCodeInterpreter
{
    private:
       dda *Dda;
       boolean abs_mode;
       char commandBuffer[COMMAND_SIZE];
       
       int cmdsize;
       struct GcodeParser gc;
       int last_gcode_g;
       
       
     public:
       GCodeInterpreter(dda* edda);
       GCodeInterpreter();
       void parseCommand(char cmd[],struct GcodeParser * gc, int size);
       void processCommand(char cmd[], int size);
       void addToCommand(char c);
       void confirmCommand();
       
       void set_absolute();
       void set_relative();
       void set_home();
       
       double search_string(char key, char instruction[], int string_size);
       boolean hasCommand(char key, char instruction[], int string_size);
  
};

#endif
