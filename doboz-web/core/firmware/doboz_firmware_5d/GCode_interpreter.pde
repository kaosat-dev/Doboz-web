#include "GCode_interpreter.h"


/* bit-flags for commands and parameters */
#define GCODE_G	(1<<0)
#define GCODE_M	(1<<1)
#define GCODE_P	(1<<2)
#define GCODE_X	(1<<3)
#define GCODE_Y	(1<<4)
#define GCODE_Z	(1<<5)
#define GCODE_I	(1<<6)
#define GCODE_N	(1<<7)
#define GCODE_CHECKSUM	(1<<8)
#define GCODE_F	(1<<9)
#define GCODE_S	(1<<10)
#define GCODE_Q	(1<<11)
#define GCODE_R	(1<<12)
#define GCODE_E	(1<<13)
#define GCODE_T	(1<<14)
#define GCODE_J	(1<<15)

#define PARSE_INT(ch, str, len, val, seen, flag) \
	case ch: \
		len = scan_int(str, &val, &seen, flag); \
		break;

#define PARSE_LONG(ch, str, len, val, seen, flag) \
	case ch: \
		len = scan_long(str, &val, &seen, flag); \
		break;

#define PARSE_FLOAT(ch, str, len, val, seen, flag) \
	case ch: \
		len = scan_float(str, &val, &seen, flag); \
		break;




//////////////////////////////////


GCodeInterpreter::GCodeInterpreter()
{
  abs_mode=false;
  cmdsize=0;
  Dda=NULL;
  last_gcode_g = -1;
}

GCodeInterpreter::GCodeInterpreter(dda* edda)
{
  abs_mode=false;
  cmdsize=0;
  Dda=edda;
  last_gcode_g = -1;
}

/*void GCodeInterpreter::parseCommand(char* cmd)
{
  byte code =  (int)search_string('G', cmd, count);
  Serial.println(code,DEC);
  
     int xmove=(int)search_string('X', cmd, count);
     int ymove=(int)search_string('Y', cmd, count);
     int zmove=(int)search_string('Z', cmd, count);
  switch (code)
  {
   case 1:

     Serial.print("Will move: x:");
     Serial.print(xmove);
     Serial.print(" y: ");
     Serial.print(ymove);
     Serial.print(" z: ");
     Serial.print(zmove);
     break;
     
   case 20:
       set_relative();
       break;
   case 21:
       set_absolute();
    break; 
    
  }
  count=0;
}*/

void GCodeInterpreter::parseCommand(char instruction[],struct GcodeParser * gc, int size)
{
        int ind=0;
	int len=0;	/* length of parameter argument */

	gc->seen = 0;


	/* scan the string for commands and parameters, recording the arguments for each,
	 * and setting the seen flag for each that is seen
	 */
	for (ind=0; ind<size; ind += (1+len))
	{
		len = 0;
		switch (instruction[ind])
		{
		        PARSE_INT('G', &instruction[ind+1], len, gc->G, gc->seen, GCODE_G);
		        PARSE_INT('M', &instruction[ind+1], len, gc->M, gc->seen, GCODE_M);
			PARSE_INT('T', &instruction[ind+1], len, gc->T, gc->seen, GCODE_T);
			PARSE_FLOAT('S', &instruction[ind+1], len, gc->S, gc->seen, GCODE_S);
			PARSE_FLOAT('P', &instruction[ind+1], len, gc->P, gc->seen, GCODE_P);
			PARSE_FLOAT('X', &instruction[ind+1], len, gc->X, gc->seen, GCODE_X);
			PARSE_FLOAT('Y', &instruction[ind+1], len, gc->Y, gc->seen, GCODE_Y);
			PARSE_FLOAT('Z', &instruction[ind+1], len, gc->Z, gc->seen, GCODE_Z);
			PARSE_FLOAT('I', &instruction[ind+1], len, gc->I, gc->seen, GCODE_I);
			PARSE_FLOAT('J', &instruction[ind+1], len, gc->J, gc->seen, GCODE_J);
			PARSE_FLOAT('F', &instruction[ind+1], len, gc->F, gc->seen, GCODE_F);
			PARSE_FLOAT('R', &instruction[ind+1], len, gc->R, gc->seen, GCODE_R);
			PARSE_FLOAT('Q', &instruction[ind+1], len, gc->Q, gc->seen, GCODE_Q);
			PARSE_FLOAT('E', &instruction[ind+1], len, gc->E, gc->seen, GCODE_E);
			PARSE_LONG('N', &instruction[ind+1], len, gc->N, gc->seen, GCODE_N);
			PARSE_INT('*', &instruction[ind+1], len, gc->Checksum, gc->seen, GCODE_CHECKSUM);
                        default:
			  break;
		}
	} 
}

void GCodeInterpreter::processCommand(char instruction[], int size)
{
    FloatPoint fp;
    
    float fr;
    boolean axisSelected=false;
    parseCommand(instruction,&gc,size);
    cmdsize=0;
    
    Serial.print(instruction);
    Serial.print(" ");
    /* if no command was seen, but parameters were, then use the last G code as 
	 * the current command
	 */
	if ((!(gc.seen & (GCODE_G | GCODE_M | GCODE_T))) && ((gc.seen != 0) && (last_gcode_g >= 0)))
	{
		/* yes - so use the previous command with the new parameters */
		gc.G = last_gcode_g;
		gc.seen |= GCODE_G;
	}
    
  //did we get a gcode?
	if (gc.seen & GCODE_G)
  	{
		last_gcode_g = gc.G;	/* remember this for future instructions */
		fp = Dda->getCurrentPosition();
		if (abs_mode)
		{
			if (gc.seen & GCODE_X)
				fp.x = gc.X;
			if (gc.seen & GCODE_Y)
				fp.y = gc.Y;
			if (gc.seen & GCODE_Z)
				fp.z = gc.Z;
			if (gc.seen & GCODE_E)
				fp.e = gc.E;
                      
                    
		}
		else
		{
			if (gc.seen & GCODE_X)
				fp.x += gc.X;
			if (gc.seen & GCODE_Y)
				fp.y += gc.Y;
			if (gc.seen & GCODE_Z)
				fp.z += gc.Z;
			if (gc.seen & GCODE_E)
				fp.e += gc.E;
		}

		// Get feedrate if supplied - feedrates are always absolute???
		if ( gc.seen & GCODE_F )
			fp.f = gc.F;
               
                // Process the buffered move commands first
                // If we get one, return immediately

		switch (gc.G)
                {
			//Rapid move
			case 0:
                                //fr = fp.f;
                                //fp.f = FAST_XY_FEEDRATE;
                                Dda->set_target(fp);
                                //qMove(fp);
                                //fp.f = fr;
                                return;
                                
                        // Controlled move; -ve coordinate means zero the axis
			case 1:
                                  Dda->set_target(fp);
                                 //qMove(fp);
                                 return;                                  
                                
                        //go home.  If we send coordinates (regardless of their value) only zero those axes
			case 28:
                                axisSelected = false;
                                if(gc.seen & GCODE_X)
                                {
                                  Dda->zero_X();
                                  axisSelected = true;
                                }
                                if(gc.seen & GCODE_Y)
                                {
                                  Dda->zero_Y();
                                  axisSelected = true;
                                }                                
                                if(gc.seen & GCODE_Z)
                                {
                                 Dda->zero_Z();
                                  axisSelected = true;
                                }
                                if(!axisSelected)
                                {
                                 Dda->zero_all();
                                }
                               // where_i_am.f = SLOW_XY_FEEDRATE;     // Most sensible feedrate to leave it in                    

				return;


                          default:
                                break;
                }
                
		// Non-buffered G commands
                // Wait till the buffer q is empty first
                    
                  //while(!qEmpty()) delay(WAITING_DELAY);
                  //delay(2*WAITING_DELAY); // For luck
		  switch (gc.G)
		  {

  			 //Dwell
			case 4:
				delay((int)(gc.P + 0.5)); 
                                confirmCommand();
				break;

			//Inches for Units
			case 20:
                                Dda->set_units(false);
                                confirmCommand();
				break;

			//mm for Units
			case 21:
                                Dda->set_units(true);
                                confirmCommand();
				break;

			//Absolute Positioning
			case 90: 
				abs_mode = true;
                                confirmCommand();
				break;

			//Incremental Positioning
			case 91: 
				abs_mode = false;
                                confirmCommand();
				break;

			//Set position as fp
			case 92: 
                                FloatPoint fpTmp;
                                fpTmp=Dda->getCurrentPosition();
                                axisSelected = false;
                                if(gc.seen & GCODE_X)
                                {
                                  //Dda->home_X();
                                  fpTmp.x=gc.X;
                                  axisSelected = true;
                                }
                                if(gc.seen & GCODE_Y)
                                {
                                  //Dda->home_Y();
                                  fpTmp.y=gc.Y;
                                  axisSelected = true;
                                }                                
                                if(gc.seen & GCODE_Z)
                                {
                                  fpTmp.z=gc.Z;
                                 //Dda->home_Z();
                                  axisSelected = true;
                                }
                                if(gc.seen & GCODE_E)
                                {
                                  fpTmp.e=gc.E;
                                 //Dda->home_E();
                                  axisSelected = true;
                                }
                                if(!axisSelected)
                                {
                                 Dda->set_home(); 
                                }
                                else
                                {
                                    Dda->setCurrentPosition(fpTmp);
                                }

                                
                                confirmCommand();
				break;

			default:
                          confirmCommand();
                          break;
				//Serial.println("ok");
		  }
        }
       
                 //find us an m code.
      	if (gc.seen & GCODE_M)
      	{
              switch (gc.M)
	      {
                  case 101:
                    //Dda->extruder_forward();
		    //Dda->start_extruder();
                    confirmCommand();
		    break;
                  case 102:
		    //Dda->extruder_backwards();
		    //Dda->start_extruder();
                    confirmCommand();
		    break;
                  case 103:
		    //Dda->stop_extruder();
                    confirmCommand();
		    break;
                  //custom code for temperature control
		    case 104:
		    if (gc.seen & GCODE_S)
	            {
                        set_ExtruderTemp((int)gc.S);
		        
		    }
		    break;

			//custom code for temperature reading
		    case 105:
                     if (gc.seen)
	            {           
                           get_ExtruderTemp();
                    }

			break;
                  //set bed temperature
                  case 140:
                          if (gc.seen & GCODE_S)
	            {
                        set_BedTemp((int)gc.S);
		        
		    }
			break;
                    case 143:
                          if (gc.seen )
	            {
                        get_BedTemp();
		        
		    }
			break;

                  //get 3d point scan
                  case 180:
                          if (gc.seen)
	            {                    
                        request_3dPoint();
		        
		    }
			break;
  
                  default:
                          confirmCommand();
                          break;
                
              }  
      	}
}

void GCodeInterpreter::addToCommand(char c)
{
  
  if (c != '\n')
  {
    commandBuffer[cmdsize]=c;
    cmdsize++;
  }
  else
  {
     commandBuffer[cmdsize] = 0;
     processCommand(commandBuffer,cmdsize);   
     cmdsize=0;
  }
  
}

void GCodeInterpreter::confirmCommand()
{
   Serial.println("ok"); 
}



void GCodeInterpreter::set_absolute()
{
 Serial.println("Setting absolute"); 
}

void GCodeInterpreter::set_relative()
{
 Serial.println("Setting relative"); 
}

void GCodeInterpreter::set_home()
{
  
}


//look for the number that appears after the char key and return it
double GCodeInterpreter::search_string(char key, char instruction[], int string_size)
{
	char temp[10] = "";

	for (byte i=0; i<string_size; i++)
	{
		if (instruction[i] == key)
		{
			i++;      
			int k = 0;
			while (i < string_size && k < 10)
			{
				if (instruction[i] == 0 || instruction[i] == ' ')
					break;

				temp[k] = instruction[i];
				i++;
				k++;
			}
			return strtod(temp, NULL);
		}
	}
	
	return 0;
}

//look for the command if it exists.
boolean GCodeInterpreter::hasCommand(char key, char instruction[], int string_size)
{
	for (byte i=0; i<string_size; i++)
	{
		if (instruction[i] == key)
			return true;
	}
	
	return false;
}


int scan_float(char *str, float *valp, unsigned int *seen, unsigned int flag)
{
	float res;
	int len;
	char *end;
     
	res = (float)strtod(str, &end);
	len = end - str;

	if (len > 0)
	{
		*valp = res;
		*seen |= flag;
	}
	else
		*valp = 0;
	return len;	/* length of number */
}

int scan_int(char *str, int *valp, unsigned int *seen, unsigned int flag)
{
	int res;
	int len;
	char *end;

	res = (int)strtol(str, &end, 10);
	len = end - str;

	if (len > 0)
	{
		*valp = res;
		*seen |= flag;
	}
	else
		*valp = 0;
          
	return len;	/* length of number */
}

int scan_long(char *str, long *valp, unsigned int *seen, unsigned int flag)
{
	long res;
	int len;
	char *end;

	res = strtol(str, &end, 10);
	len = end - str;

	if (len > 0)
	{
		*valp = res;
		*seen |= flag;
	}
	else
		*valp = 0;
          
	return len;	/* length of number in ascii world */
}

