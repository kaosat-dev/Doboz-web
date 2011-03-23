#ifndef POSITIONING_H
#define POSITIONING_H


#include "stepper.h"
#include "configuration.h"
#include "vectors.h"

struct Axis
{
    FloatPoint current_position;
    FloatPoint start_position;//defaults to 0
    FloatPoint end_position;
};


class Positionning
{
  private:
    Axis X_axis;
    Axis Y_axis;
    Axis Z_axis;
  
};

#endif
