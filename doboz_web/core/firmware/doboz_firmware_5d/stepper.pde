Stepper::Stepper()
{
    stepPin=-1;
    dirPin=-1;
    enablePin=-1;
    direction=false;   
    isOn=false;
    remainingSteps=0;
    isDone=true;
    
}
Stepper::Stepper(int step_pn, int dir_pn, int enable_pn, long lowphase, int stepsPmm)
{
    stepPin=step_pn;
    dirPin=dir_pn;
    enablePin=enable_pn;
    
    //direction
    digWrite( dirPin,LOW);
    //disable
    digWrite( enablePin,HIGH);


    low_phase=lowphase;
    
    remainingSteps=0;
    last_time=0;
    stepStarted=false;
    stepFinished=true;
    
    steps_per_mm=stepsPmm;
    isOn=false;
    isDone=true;
    //digitalWrite(enablePin,LOW);
}

void Stepper::start()
{

  if(!isOn)
  {
  digWrite(enablePin,LOW);
  //remainingSteps=steps_per_mm;
  last_time=micros();
  stepStarted=false;
  stepFinished=true;
  isOn=true;
  isDone=false;
  }

}

void Stepper::stop()
{
  digWrite(enablePin,HIGH);
   isOn=false;
  //BIT_SET(PORTB, 0); 
}



void Stepper::update()
{
  if(remainingSteps>=0 && !isDone)
  {
    remainingSteps--;
     digWrite(stepPin, HIGH);
     digWrite(stepPin, LOW);
     delayMicroseconds(low_phase);
   
    }
  else
  {
    stop();
    isDone=true;
  }
    /*if (!stepStarted)
    {
         
        //BIT_CLR(PORTC, 1) ; //low
        digWrite(stepPin, HIGH);
        stepStarted=true;
        stepFinished=false;       
        last_time=micros();
     }
     else
     {  
         long currentTime=micros();
         long elapsed=currentTime-last_time;
                
        if(!stepFinished)
        {
          if(elapsed>=low_phase)
          {
            
                
            digWrite(stepPin, LOW);
            stepFinished=true;
            remainingSteps--;
            last_time=currentTime;
          
          }
        }
        else
        {
          if(elapsed>=low_phase)
          {
            stepStarted=false;
          }
        }
}
    */ 
 

}


int Stepper::stepsPerMM()
{
   return  steps_per_mm;
}

int Stepper::getremainingSteps()
{
   return remainingSteps; 
}

void Stepper::change_dir()
{
  direction=!direction;
  digWrite(dirPin,direction); 
}

void Stepper::do_step()
{
   digWrite(stepPin, HIGH);
    digWrite(stepPin, LOW);
  /*Serial.println(low_phase);
        for(int i=0;i<=remainingSteps;i++)
        {
        digitalWrite(stepPin, HIGH);
	delayMicroseconds(2);
	digitalWrite(stepPin, LOW); 
        delayMicroseconds(low_phase);
        }
        digitalWrite(dirPin,!digitalRead(dirPin));*/
}
void Stepper::set_dir(boolean dir)
{
  direction=dir;
  digWrite(dirPin,direction); 
}

void Stepper::set_steps(long steps)
{
  remainingSteps=steps;
}

void Stepper::enable()
{
  digWrite(enablePin,LOW);
  stepStarted=false;
  stepFinished=true;
  last_time=micros();
  isOn=true; 

}

void Stepper::disable()
{
  digWrite(enablePin,HIGH);
  stepStarted=false;
  stepFinished=true;
  isOn=false;
  isDone=false; 
}

 boolean Stepper::get_done()
 {
    return isDone; 
 }
 long Stepper::get_steps()
 {
    return remainingSteps; 
 }

 
 void Stepper::set_lowPhaze(long low)
 {
    low_phase=low; 
    Serial.print("low phase ");
    Serial.println(low_phase);
 }
