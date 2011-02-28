#include <stdlib.h> // for malloc and free
void* operator new(size_t size) { return malloc(size); }
void operator delete(void* ptr) { free(ptr); } 


#ifndef PINMAPPER_H
#include "PinMapper.h"
#endif
/*
Ckaos Sep15 2010

*/



#define PWMTest 9
#define PWMTest2 3

//#define mainAnalog 3

//I2c com
#define THIS_ADDRESS 0x8
#define OTHER_ADDRESS 0x9


/*
MSB -> flag for button detected on/off on last sweep
3 LSB -> 4051 slave truthtable codes
0 1 2 3
4 5 6 7
8 9 10 11
12 13 14 15*/
//byte buttonMap[]={101,111,11,1,  101,111,11,1,  10,100,0,110,  10,100,0,110};

#include <EEPROM.h>
#include <Wire.h>


#include "commands.h"
#include "heater.h"
#include "scanner.h"

#include "button_matrix.h"
#include "lcd_menu.h"




#include <EEPROM.h>

PinMapper pinMapper;
//LcdMenu mmenu;
ButtonMatrix buttonm(3);
Heater bed(&pinMapper,41,11, 0, 2, 0.12,0.8,false);
Heater head(&pinMapper,35,9, 0,7, 0.2,0.3,true);
Scanner scanner(13);



void left()
{
  
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send(MOVE_LEFT);
  Wire.endTransmission();
}

void right()
{
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send(MOVE_RIGHT);
  Wire.endTransmission();
}
void up()
{
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send(MOVE_UP);
  Wire.endTransmission();
}
void down()
{
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send(MOVE_DOWN);
  Wire.endTransmission();
}
void fwd()
{
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send(MOVE_FORWARD);
  Wire.endTransmission();
}
void bck()
{
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send(MOVE_BACK);
  Wire.endTransmission();
}

void extFwd()
{
   Serial.println("ext");
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send(EXTRUDE_FORWARD);
  Wire.endTransmission();
}

void extBck()
{
   Serial.println("ext");
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send(EXTRUDE_BACK);
  Wire.endTransmission();
}

void stooop()
{
   Serial.println("ext");
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send(STOP);
  Wire.endTransmission();
}


long now=0;
long then=0;


void save_to_mem(int value)
{
  EEPROM.write(0, value);
}
int load_from_mem()
{
  return EEPROM.read(0);
}


MenuItem *currentItem;
MenuItem one=MenuItem("Status");
MenuItem two=MenuItem("Manual Control");
MenuItem three=MenuItem("Settings");
MenuItem four=MenuItem("Info");

BoolMenu autoMenu=BoolMenu("Manual",false);

NumericMenu testMen=NumericMenu("Bed Temp",25,5,&bed,&Heater::set_target_temperature);
NumericMenu testMen2=NumericMenu("Head Temp",75,5,&head,&Heater::set_target_temperature);
InfoMenu bedtempDisplay=InfoMenu("Bed ",&bed,&Heater::get_temperature);
InfoMenu headtempDisplay=InfoMenu("Head ",&head,&Heater::get_temperature);
MenuItem versionInfo=MenuItem("DobozIo: v0.1");

void truc()
{
  //mmenu.prev();
  currentItem=currentItem->prev_sibling();
   init_lcd();
  
  currentItem->print();
}

void machin()
{
 // mmenu.next();
 currentItem=currentItem->next_sibling();
 init_lcd();
 currentItem->print();
}

void upMenu()
{
  
  if(currentItem->get_parent()!=NULL)
 {  
   currentItem=currentItem->get_parent();
 }
  init_lcd();
 currentItem->print();
}

void downMenu()
{
  
  if(currentItem->get_child(0)!=NULL)
 {  
   currentItem=currentItem->get_child(0);
 }
  init_lcd();
 currentItem->print();
}

void valueSet()
{
  currentItem->set();
}

void valUp()
{
  currentItem->nextValue();
  Serial.println("valup");
}
void valDown()
{
  currentItem->prevValue();
   Serial.println("valdown");
}

void reset_shiftreg()
{
  BIT_CLR(PORTB,0);
    shiftOut(dataPin, clockPin, MSBFIRST, 0x00);
    shiftOut(dataPin, clockPin, MSBFIRST, 0x00);
  BIT_SET(PORTB,0);
}



boolean shiftRegLocked=false;
//for shiftreg synchronization , in order not to get garbled lcd display since the lcd display and the buttons etc use the same shiftreg
void wait_till_ulocked()
{
  while(shiftRegLocked)
  {
  }
}

boolean directControl=false;
//to switch between direct control and menu system
void switch_mode()
{
   
    directControl=!directControl; 
    
    Serial.println(directControl);
     if(directControl)
    {
      buttonm.clear_callbacks();
      buttonm.setCallback(15,&switch_mode);
        buttonm.setCallback(0,&extFwd);
        buttonm.setCallback(8,&extBck);
        buttonm.setCallback(5,&stooop);
         buttonm.setCallback(4,&left);
         buttonm.setCallback(6,&right);
        buttonm.setCallback(2,&up);
         buttonm.setCallback(10,&down);
         
       buttonm.setCallback(9,&fwd);
       buttonm.setCallback(1,&bck);
    }
    else
    {
      buttonm.clear_callbacks();
      buttonm.setCallback(15,&switch_mode);
      buttonm.setCallback(1,&truc);
      buttonm.setCallback(9,&machin);
      buttonm.setCallback(4,&upMenu);
      buttonm.setCallback(6,&downMenu);
      buttonm.setCallback(5,&valueSet);
      
      buttonm.setCallback(3,&valUp);
      buttonm.setCallback(7,&valDown);
    }
}

void HeadTemperatureReached()
{
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send(HEAD_TEMP_REACHED);
  Wire.endTransmission();
}

void BedTemperatureReached()
{
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send(BED_TEMP_REACHED);
  Wire.endTransmission();
}

void GetHeadTemp(int headTemp)
{
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send('u');
  Wire.send(headTemp);
  Wire.endTransmission();
}

void GetBedTemp(int bedTemp)
{
  Wire.beginTransmission(OTHER_ADDRESS);
  Wire.send('v');
  Wire.send(bedTemp);
  Wire.endTransmission();
}

void scanRequested(int height)
{
  Wire.beginTransmission(OTHER_ADDRESS);
   Wire.send('d');
  Wire.send(height);
  Wire.endTransmission();
}



void setup()
{
   DDRB = DDRB | B00000001;
   DDRC = DDRC | B00000000;   
   DDRD = DDRD | B11101000;
   Wire.begin(THIS_ADDRESS);
   Wire.onReceive(receiveEvent);
  
   Serial.begin(19200);  
 
  init_lcd();
  print_lcd_str("Initialising ");
  setCursor(2,0);
  print_lcd_str("...");

  bed.set_callback(&BedTemperatureReached);
  bed.set_tempRequestedcallback(&GetBedTemp);
  
  head.set_callback(&HeadTemperatureReached);
   head.set_tempRequestedcallback(&GetHeadTemp);
  
  scanner.set_callback(&scanRequested);
/*mmenu=LcdMenu();
mmenu.add_item(&one);
mmenu.add_item(&two);
mmenu.add_item(&three);
mmenu.add_item(&four);
mmenu.add_item(&testMen);
mmenu.add_item(&testMen2);*/


one.add_sibling(true,&two);
one.add_sibling(true,&three);
one.add_sibling(true,&four);


one.add_child(&bedtempDisplay);
one.add_child(&headtempDisplay);

three.add_child(&testMen);
three.add_child(&testMen2);

two.add_child(&autoMenu);

four.add_child(&versionInfo);


buttonm.setCallback(1,&truc);
buttonm.setCallback(9,&machin);
buttonm.setCallback(4,&upMenu);
buttonm.setCallback(6,&downMenu);
buttonm.setCallback(5,&valueSet);

buttonm.setCallback(3,&valUp);
buttonm.setCallback(7,&valDown);


buttonm.setCallback(15,&switch_mode);

currentItem=&one;
currentItem->print();

 bed.set_target_temperature(0); 
 head.set_target_temperature(0); 
}




void loop()
{
  
  buttonm.update();

  bed.update();
  head.update();
  scanner.update();
  
 
  if(Serial.available()>0)
  {
     char cmd=Serial.read();
     Serial.println(cmd);
     if(cmd==START_SCAN)
    {
       scanner.scan();
       Serial.println("starting scan");
    } 
    else if(cmd==STOP_SCAN)
    {
      scanner.stop(); 
      Serial.println("stopping scan");
    }
    
  }
  


}

#define NUMTEMPS2 20
short tempTabl[NUMTEMPS2][2] = {
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

int  convert(int rawtemp)
{
  
  
  
  
  int temperature;
  byte i;
   for (i=1; i<NUMTEMPS2; i++)
   {
      if (tempTabl[i][0] > rawtemp)
      {
         int realtemp  = tempTabl[i-1][1] + (rawtemp - tempTabl[i-1][0]) * (tempTabl[i][1] - tempTabl[i-1][1]) / (tempTabl[i][0] - tempTabl[i-1][0]);

         if (realtemp > 255)
            realtemp = 255;

         temperature = realtemp;

         break;
      }
   }

   // Overflow: We just clamp to 0 degrees celsius
   if (i == NUMTEMPS2)
   temperature = 0;
   return temperature;
}



void receiveEvent(int howMany)
{
  

  while (Wire.available() > 0)
  {
    
    char c = Wire.receive();
    int v=Wire.receive();
    //Serial.println(v,DEC);
    handleCommand(c,v);
   
  }

}

void handleCommand(int command,int value)
{
  switch(command)
    {
      case 'E':
        head.set_target_temperature(value);     
      break;
       case 'B':
        bed.set_target_temperature(value);     
      break;
      case 'U':
        head.requestTemperature();     
      break;
       case 'V':
        bed.requestTemperature();     
      break;
      case 'D':
        scanner.request_data();
      break;
    }
}

 double search_string(char key, char instruction[], int string_size)
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

