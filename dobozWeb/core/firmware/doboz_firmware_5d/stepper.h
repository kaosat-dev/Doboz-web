/*Stepper Management class
*/
#include <WProgram.h>
#ifndef STEPPER_H
#define STEPPER_H
class Stepper
{
  private:
    int stepPin;
    int dirPin;
    int enablePin;
    boolean direction;
    boolean isOn;
    boolean isDone;
    
    long remainingSteps;
    long steps_per_mm;
    long low_phase; //how much of a delay, in microseconds, till next step
    bool stepStarted;
    bool stepFinished;
    
    long last_time;
 
  
  public:
    Stepper();
    Stepper(int step_pin, int dir_pin, int enable_pin, long lowPhase,int stepsPmm);
    void start();
    void stop();
    void enable();
    void disable();
    void do_step();
    void step_up();
    void step_down();
    int  stepsPerMM();
    int getremainingSteps();
    
    
    void update();
    
    void change_dir();
    void set_dir(boolean dir);
    void set_steps(long steps);
    long get_steps();
    void set_lowPhaze(long low);
    boolean get_done();
};
#endif



