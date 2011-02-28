#include <WProgram.h>
typedef struct 
{
  volatile uint8_t  *reg;
  uint8_t prt;
   
}pin;


#define BIT_SET(REG, bit)                    ( REG |= (1UL << (bit) ) )

#define BIT_CLR(REG, bit)                    ( REG &= ~(1UL << (bit) ) )

#define BIT_TST(REG, bit, val)              ( ( (REG & (1UL << (bit) ) ) == ( (val) << (bit) ) ) )

//port mapping, to be able to use similar functions to the basic digitalwrite stuff, except much faster
pin portMap[]={{&PORTD, 0},{&PORTD,1},{&PORTD,2},{&PORTD,3},{&PORTD,4},{&PORTD,5},{&PORTD,6},{&PORTD,7},
{&PORTB,0},{&PORTB,1},{&PORTB,2},{&PORTB,3},{&PORTB,4},{&PORTB,5},{&PORTC,0},{&PORTC,1},{&PORTC,2},{&PORTC,3},{&PORTC,4},{&PORTC,5}};

void digWrite(int pn,boolean high)
{
    if(high)
    {
    
         BIT_SET(*(portMap[pn].reg),portMap[pn].prt); 
      
    }
    else
    {
       BIT_CLR(*(portMap[pn].reg),portMap[pn].prt); 
    }
}



