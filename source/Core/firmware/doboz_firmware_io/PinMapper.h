#ifndef PINMAPPER_H
#define PINMAPPER_H


#include <WProgram.h>
/*the general mapping is as follows:
Muxed ports:
-from top to bottom on the left : ports 0 to 15
-from top to bottom on the right: ports 16 to 31
Other ports:
-32 to 34 from left to right : the pwm pins for temperature control
Additional info: 
master 4051
A->Q2(6)
B->Q3(7)
C->Q4(14)

Slave 4051
A->Q7 (12)
B->Q6(11)
C->Q5 (10)
*/
#include "pins.h"
class PinMapper
{
  public:
  int A_READ(int pin);
  int D_READ(int pin);
  void A_WRITE(int pin, int value);
  void D_WRITE(int pin, boolean highLow);
};
#define BIT_SET(REG, bit)                    ( REG |= (1UL << (bit) ) )

#define BIT_CLR(REG, bit)                    ( REG &= ~(1UL << (bit) ) )

#define BIT_TST(REG, bit, val)              ( ( (REG & (1UL << (bit) ) ) == ( (val) << (bit) ) ) )

#endif
