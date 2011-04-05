#ifndef DDA_H
#define DDA_H


#include "vectors.h"
#include <WProgram.h>

class dda
{
  
  private:
  
    boolean live ;
  
    float distance;  
    FloatPoint units;            // Factors for converting either mm or inches to steps
    boolean using_mm;
    
    LongPoint dda_counter;  
    FloatPoint target_position;
    FloatPoint current_position;
    FloatPoint delta_position;
    
    FloatPoint home;
    
    LongPoint target_steps;
    LongPoint current_steps;
    LongPoint delta_steps;
    
    volatile long total_steps;            // The number of steps to take along the longest movement axis
    int total_steps_index;
    
    boolean  x_direction;
    boolean  y_direction;
    boolean  z_direction;
    boolean  e_direction;
    boolean  f_direction;
    
    boolean real_move;
	
    int nbSteppers;
    Stepper steppers[4];
    
    
    long t_scale;     
    long timestep;
    volatile boolean feed_change;   // Flag to know if feedrate has changed
    boolean isRunning;
    
     volatile boolean x_can_step;             // Am I not at an endstop?  Have I not reached the target? etc.
    volatile boolean y_can_step;
    volatile boolean z_can_step;
    volatile boolean e_can_step;
    volatile boolean f_can_step;
    
  
    
    boolean xCanStep(long current, long target, boolean dir);
    boolean yCanStep(long current, long target, boolean dir);
    boolean zCanStep(long current, long target, boolean dir);
    boolean eCanStep(long current, long target, boolean dir);
    boolean fCanStep(long current, long target, boolean dir);
  
    
    public:
      dda();
      void set_units(boolean um);
      void set_units();
      void set_target(const FloatPoint& p);
      
      FloatPoint getCurrentPosition();
      void setCurrentPosition(const FloatPoint& p);
      void zero_X();
      void zero_Y();
      void zero_Z();
      void zero_all();
      
      void set_home();
      void home_X();
      void home_Y();
      void home_Z();
      void home_E();

      void dda_step();
      
      void dda_start();
      void dda_stop();
      
      
      void enable_steppers();
      void disable_steppers();
      void shutdown();
      long calculate_feedrate_delay(const float& feedrate);
      
      void save_position();//saves current position and stepping information to eeprom memory
      void load_position();//loads current position and stepping information from eeprom memory//needs to be called at startup
      boolean isLive();
      void extruder_forward();
      void extruder_backwards();
      void stop_extruder();
      void start_extruder();
        String currentCommand;//hack
};


inline long dda::calculate_feedrate_delay(const float& feedrate)
{  
        
	// Calculate delay between steps in microseconds.  Here it is in English:
        // (feedrate is in mm/minute, distance is in mm)
	// 60000000.0*distance/feedrate  = move duration in microseconds
	// move duration/total_steps = time between steps for master axis.

	return round( (distance*60000000.0) / (feedrate*(float)total_steps) );	
}






inline boolean dda::xCanStep(long current, long target, boolean dir)
{
  if (target == current)
		return false;
  return true;
}

inline boolean dda::yCanStep(long current, long target, boolean dir)
{
  if (target == current)
		return false;
  return true;
}

inline boolean dda::zCanStep(long current, long target, boolean dir)
{
  if (target == current)
		return false;
  return true;
}

inline boolean dda::eCanStep(long current, long target, boolean dir)
{
  if (target == current)
		return false;
  return true;
}

inline boolean dda::fCanStep(long current, long target, boolean dir)
{
  if (target == current)
		return false;
  return true;
}


#endif
