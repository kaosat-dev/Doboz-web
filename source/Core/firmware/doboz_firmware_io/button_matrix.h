#include <stdio.h>

#ifndef PINMAPPER_H
#include "PinMapper.h"
#endif

#ifndef BUTTONMATRIX_H
#define BUTTONMATRIX_H
/*Class for handling the button matrix and its callback functions etc*/
class Button
{
    private:
      byte truthTable;
      boolean  pressed;
      
    public:
      Button();
      Button(byte truthT); 
      void (*buttonPressed)(void);
    
};

class ButtonMatrix
{
  
  private:
  //  void (*buttonPressed)(void);
    long now;
    long then;
    Button buttonMap[16];
   // byte *shiftRegOne;
    uint8_t inputPin;
    
  public:
    ButtonMatrix();
    ButtonMatrix(uint8_t inPin);
    void update();
    void setCallback(int index, void(*callBck)(void));
    void clear_callbacks();
   // int (*pt2Function)(float, char, char) = NULL; 
};
#endif


