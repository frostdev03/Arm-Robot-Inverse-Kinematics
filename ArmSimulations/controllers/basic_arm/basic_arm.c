#include <webots/robot.h>
#include <stdio.h>

#define TIME_STEP 64

int main() {

  wb_robot_init();
  
    WbDeviceTag arm1 = wb_robot_get_device("joint1");
    WbDeviceTag arm2 = wb_robot_get_device("joint2");
    WbDeviceTag arm3 = wb_robot_get_device("joint3");
        
    int counter = 0;

  while (wb_robot_step(TIME_STEP) != -1) {
  
  if(counter < 40)
  {
    wb_motor_set_position(arm1, INFINITY);
    wb_motor_set_velocity(arm1, -0.5);
  }
  if(counter > 40 & counter < 60)
  {
    wb_motor_set_velocity(arm1, 0.0);
    wb_motor_set_position(arm2, INFINITY); 
    wb_motor_set_velocity(arm2, 0.5);
  }
  if(counter > 60 & counter < 80)
  {
    wb_motor_set_velocity(arm2, 0.0);
    wb_motor_set_position(arm3, INFINITY);
    wb_motor_set_velocity(arm3, -0.5);
  }
  if(counter > 80)
  {
    wb_motor_set_velocity(arm3, -0.5); 
  }
    
    counter = counter + 1;

  };

  wb_robot_cleanup();

  return 0;
}
