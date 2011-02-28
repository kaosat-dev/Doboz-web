

//int X_MAX_FEEDRATE;//en mm/s
//int Y_MAX_FEEDRATE;

#define X_STEPS_PER_MM 3200
#define Y_STEPS_PER_MM 3200
#define Z_STEPS_PER_MM 6400
#define E_STEPS_PER_MM 3200


#define X_STEPS_PER_INCH 3200
#define Y_STEPS_PER_INCH 3200
#define Z_STEPS_PER_INCH 6400
#define E_STEPS_PER_INCH 3200


// The number of mm below which distances are insignificant (one tenth the
// resolution of the machine is the default value).

#define SMALL_DISTANCE 0.01 // *RO

// Useful to have its square

#define SMALL_DISTANCE2 (SMALL_DISTANCE*SMALL_DISTANCE) // *RO


//our maximum feedrates in mm/minute
#define FAST_XY_FEEDRATE 115.0
#define FAST_Z_FEEDRATE  80.0


// Data for acceleration calculations
// Comment out the next line to turn accelerations off
#define ACCELERATION_ON
#define SLOW_XY_FEEDRATE 80.0 // Speed from which to start accelerating
#define SLOW_Z_FEEDRATE 40
