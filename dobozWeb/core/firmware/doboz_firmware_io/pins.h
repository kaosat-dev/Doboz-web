static byte shiftRegOne=B10101100;//state of first shift reg
static byte shiftRegTwo=B10100000;//state of 2nd shift reg (lcd+ buttons)
static uint8_t dataPin=7;//PD7;
static uint8_t clockPin=6;//PD6;
static uint8_t latchPin=8;//PB0;
#define mainAnalog (uint8_t) 3
//#define buttonMap={101,111,11,1,  101,111,11,1,  10,100,0,110,  10,100,0,110};
static byte portMap[]={0,100,010,110,1,101,11,111};

