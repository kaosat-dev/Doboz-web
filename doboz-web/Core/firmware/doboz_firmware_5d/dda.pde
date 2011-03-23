#include "dda.h"
#include "stepper.h"
#include "configuration.h"
#include <EEPROM.h>
dda::dda()
{
  live=false;
  using_mm=true;
  
  steppers[0]=Stepper(16,13,9,500,75);//extuder//240//feedrate:95 //ideal :3000/12G1 X30 E240
  steppers[1]=Stepper(14,10,6,80,3200);//x axis//feedrate:29
  steppers[2]=Stepper(17,12,8,80,3200);//y axis//
  steppers[3]=Stepper(15,11,7,180,5200);//z axis// 
  
  
  nbSteppers=4;
  //just to be sure, although, normally stepper are off when initialised
  steppers[0].stop();
  steppers[1].stop(); 
  steppers[2].stop(); 
  steppers[3].stop(); 
  
  current_position.x=0.0;
  current_position.y=0.0;
  current_position.z=0.0;
  current_position.e=0.0;
  
  target_position.x = 0.0;
  target_position.y = 0.0;
  target_position.z = 0.0;
  target_position.e = 0.0;
  
  set_units();
  isRunning=false;
  
}

void dda::set_units()
{
  if(using_mm)
    {
      units.x = steppers[1].stepsPerMM();
      units.y = steppers[2].stepsPerMM();
      units.z = steppers[3].stepsPerMM();
      units.e = steppers[0].stepsPerMM();//ex[extruder_in_use]->stepsPerMM();
      units.f = 1.0;
    } else
    {
      units.x = X_STEPS_PER_INCH;
      units.y = Y_STEPS_PER_INCH;
      units.z = Z_STEPS_PER_INCH;
      units.e = 1.0;//ex[extruder_in_use]->stepsPerMM()*INCHES_TO_MM;
      units.f = 1.0;  
    }
}

void dda::set_units(boolean um)
{
     using_mm = um;
     set_units();
     Serial.println("setting units");
}

void dda::set_target(const FloatPoint& p)
{
        target_position = p;
        //figure our deltas.        
        delta_position = fabsv(target_position - current_position);
        
        FloatPoint squares = delta_position*delta_position;
        distance = squares.x + squares.y + squares.z;
        // If we are 0, only thing changing is e
        if(distance < SMALL_DISTANCE2)
          distance = squares.e;
        // If we are still 0, only thing changing is f
        if(distance < SMALL_DISTANCE2)
          distance = squares.f;
        distance = sqrt(distance);     
        
        //set our steps current, target, and delta
        current_steps = to_steps(units, current_position);
	target_steps = to_steps(units, target_position);
	delta_steps = absv(target_steps - current_steps);

        // find the dominant axis.
        // NB we ignore the f values here, as it takes no time to take a step in time :-)
        total_steps = max(delta_steps.x, delta_steps.y);
        total_steps = max(total_steps, delta_steps.z);
        total_steps = max(total_steps, delta_steps.e);
        
       
        
        if(total_steps == 0)
        {
           current_position=p;
           Serial.println("ok");
           return; 
        }

        #ifndef ACCELERATION_ON
                current_steps.f = target_steps.f;
        #endif

        delta_steps.f = abs(target_steps.f - current_steps.f);
        
        // Rescale the feedrate so it doesn't take lots of steps to do
        
        t_scale = 1;
        if(delta_steps.f > total_steps)
        {
            t_scale = delta_steps.f/total_steps;
            if(t_scale >= 3)
            {
              target_steps.f = target_steps.f/t_scale;
              current_steps.f = current_steps.f/t_scale;
              delta_steps.f = abs(target_steps.f - current_steps.f);
              if(delta_steps.f > total_steps)
                total_steps =  delta_steps.f;
            } else
            {
              t_scale = 1;
              total_steps =  delta_steps.f;
            }
        } 
    //////////
        x_direction = (target_position.x <= current_position.x);
	y_direction = (target_position.y >= current_position.y);
	z_direction = (target_position.z >= current_position.z);
        e_direction = (target_position.e <= current_position.e);
	f_direction = (target_position.f >= current_position.f);
        
        


        dda_counter.x = -total_steps/2;
	dda_counter.y = dda_counter.x;
	dda_counter.z = dda_counter.x;
        dda_counter.e = dda_counter.x;
        dda_counter.f = dda_counter.x;
        


    
    current_position=p;
    
     dda_start();
}


void dda::enable_steppers()
{
  for(int i=0;i<nbSteppers;i++)
  {
      steppers[i].enable();
  }
}

void dda::disable_steppers()
{
  for(int i=0;i<nbSteppers;i++)
  {
      steppers[i].disable();
  }
}

void dda::shutdown()
{
  disable_steppers();
}

void dda::dda_step()
{ 
    x_can_step = xCanStep(current_steps.x, target_steps.x, x_direction);
    y_can_step = yCanStep(current_steps.y, target_steps.y, y_direction);
    z_can_step = zCanStep(current_steps.z, target_steps.z, z_direction);
    e_can_step = eCanStep(current_steps.e, target_steps.e, e_direction);
    f_can_step = fCanStep(current_steps.f, target_steps.f, f_direction);
   live = (x_can_step || y_can_step || z_can_step  || e_can_step || f_can_step &&isRunning);

// Wrap up at the end of a line

  if(!live)
  {
     
      if(isRunning)
      {
        Serial.println("ok");
        isRunning=false;
      }
      return;
  }
  else
  {
    real_move = false;
  
      
		if (x_can_step)
		{
			dda_counter.x += delta_steps.x;
			if (dda_counter.x > 0)
			{
				steppers[1].do_step();
                                real_move = true;
				dda_counter.x -= total_steps;
				
				if (!x_direction)
					current_steps.x++;         
				else
					current_steps.x--;
			 }
		}

		if (y_can_step)
		{
			dda_counter.y += delta_steps.y;
			
			if (dda_counter.y > 0)
			{
				steppers[2].do_step();
                                real_move = true;
				dda_counter.y -= total_steps;

				if (y_direction)
					current_steps.y++;
				else
					current_steps.y--;
			}
		}
		
		if (z_can_step)
		{
			dda_counter.z += delta_steps.z;
			
			if (dda_counter.z > 0)
			{
				steppers[3].do_step();
                                real_move = true;
				dda_counter.z -= total_steps;
				
				if (z_direction)
					current_steps.z++;
				else
					current_steps.z--;
			}
		}

		if (e_can_step)
		{
			dda_counter.e += delta_steps.e;
			
			if (dda_counter.e > 0)
			{
                                
				steppers[0].do_step();
                                real_move = true;
				dda_counter.e -= total_steps;
				
				if (!e_direction)
					current_steps.e++;
				else
					current_steps.e--;
			}
		}
		
		if (f_can_step)
		{
			dda_counter.f += delta_steps.f;
			
			if (dda_counter.f > 0)
			{
				dda_counter.f -= total_steps;
				if (f_direction)
					current_steps.f++;
				else
					current_steps.f--;
                                feed_change = true;
			} else
                                feed_change = false;
		}

				
      // wait for next step.
      // Use milli- or micro-seconds, as appropriate
      // If the only thing that changed was f keep looping
  
                if(real_move && feed_change)
                {
                  timestep = t_scale*current_steps.f;
                  timestep = calculate_feedrate_delay((float) timestep);
                  delayMicroseconds(timestep*1.0);//delayMicroseconds(timestep*1.25);
                }
                else
                {
                 delayMicroseconds(75); 
                }
               
                feed_change = false;
     
     }
}

void dda::dda_start()
{
    live=true;
    isRunning=true;
    enable_steppers();
    //set required direction for each
    steppers[0].set_dir(e_direction);
    steppers[1].set_dir(x_direction);
    steppers[2].set_dir(y_direction);
    steppers[3].set_dir(z_direction);
}

void dda::dda_stop()
{
   live=false; 
   disable_steppers();
}

FloatPoint dda::getCurrentPosition()
{
  return current_position;
}

//added to set current coordinate
void dda::setCurrentPosition(const FloatPoint& p)
{
  current_position=p;
  home=p;
}

void dda::zero_X()
{
    FloatPoint tmp=current_position;
    tmp.x=home.x;
    set_target(tmp);
}

void dda::zero_Y()
{
    FloatPoint tmp=current_position;
    tmp.y=home.y;
    set_target(tmp);
}

void dda::zero_Z()
{
     FloatPoint tmp=current_position;
    tmp.z=home.z;
    set_target(tmp);
}

void dda::zero_all()
{
  FloatPoint tmp;
  tmp.x=0;
  tmp.y=0;
  tmp.z=0;
  tmp.e=0;
  tmp.f=0;
  set_target(tmp);
}

void dda::set_home( )
{
  current_position.x=0;
  current_position.y=0;
  current_position.z=0;
  current_position.e=0;
  current_position.f=0;
  home=current_position;
}

void dda::home_X()
{
  current_position.x=0;
  home.x=0;
}

void dda::home_Y()
{
  current_position.y=0;
  home.y=0;
}

void dda::home_Z()
{
  current_position.z=0;
  home.z=0;
}

void dda::home_E()
{
  current_position.e=0;
  home.e=0;
}


boolean dda::isLive()
{
 return live; 
}

void dda::save_position()
{
  int sz=sizeof(float);
  int pos=0;
  EEPROM.write(pos, current_position.x);
  pos+=sz;
  EEPROM.write(pos, current_position.y);
  pos+=sz;
  EEPROM.write(pos, current_position.z);
}

void dda::start_extruder()
{
  steppers[0].start(); 
}
void dda::extruder_forward()
{   
  e_direction=true; 
}
void dda::extruder_backwards()
{
   e_direction=false; 
}

void dda::stop_extruder()
{
 steppers[0].stop(); 
}



