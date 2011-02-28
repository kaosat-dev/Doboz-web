#define CMD_CLR 0x01
#define CMD_RIGHT 0x1C
#define CMD_LEFT 0x18
#define CMD_HOME 0x02


void init_lcd()
{
  delay(50);  
  command_nybble(0x03);
  delay(5);
  command_nybble(0x03);
  delayMicroseconds(100);
  command_nybble(0x03);
  delay(5);
  command_nybble(0x02);
  command_nybble(0x02);
  
  //needsto be cheched:
  int g_num_lines=2;
  int num_lines_ptn = g_num_lines - 1 << 3;
  int dot_format_ptn = 0x00; 
  command_nybble(num_lines_ptn | dot_format_ptn);
  delayMicroseconds(60);
  
  ///4 *bit init
  command(0x0C);
  delayMicroseconds(60);
  command(0x01);
  delay(3);
  command(0x06);
  delay(1);
  
}

void set_rs(boolean state)
{
  if(state)
  {
   shiftRegTwo|=0x01; //high
  }
  else
  {
    shiftRegTwo&=0xFE;//low
  }
}
void command_nybble(int value)
{
  set_rs(false);
  pushNybble(value);
}


void clear_lcd()
{
  wait_till_ulocked();
  shiftRegLocked=true;
    set_rs(false);
  pushByte(CMD_CLR);
  
  shiftRegLocked=false;

}

void command(int value)
{
   wait_till_ulocked();
  shiftRegLocked=true;
  set_rs(false);
  pushByte(value);
   shiftRegLocked=false;

}

void print_lcd(int value)
{
   set_rs(true);
   pushByte(value);
}
void print_lcd_str(char msg[])
{
  
   wait_till_ulocked();
  shiftRegLocked=true;
  
  uint8_t i;
   for (i=0;i < strlen(msg);i++){
    print_lcd(msg[i]);
  }
  
   shiftRegLocked=false;
 
}


void setCursor(int line_num, int x)
{
  //first, put cursor home
  command(CMD_HOME);

  //offset 40 chars in if second line requested
  if (line_num == 2){
    x += 40;
  }
  //advance the cursor to the right according to position. (second line starts at position 40).
  for (int i=0; i<x; i++) {
    command(0x14);
  }
}

void pushByte(int value)
{
  
   int val_lower = value & 0x0F;
   int val_upper = value >> 4;
  pushNybble(val_upper);
  pushNybble(val_lower); 
}
void pushNybble(int value)
{
  
 

  shiftRegTwo&=0x0F;//clear db7-DB4 
  int tmp=value<<4;
  shiftRegTwo|=tmp;
  shiftRegTwo|=0x02;
 
  //high   
  BIT_CLR(PORTB,0);
  shiftOut(dataPin, clockPin, MSBFIRST, shiftRegTwo);
  shiftOut(dataPin, clockPin, MSBFIRST, shiftRegOne);
  BIT_SET(PORTB,0);
  delayMicroseconds(1);

  //low
  shiftRegTwo&=0xFD;
  BIT_CLR(PORTB,0);
  shiftOut(dataPin, clockPin, MSBFIRST, shiftRegTwo);
  shiftOut(dataPin, clockPin, MSBFIRST, shiftRegOne);
  BIT_SET(PORTB,0);
  delay(1);
  
 
 
}

