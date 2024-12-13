#include <webots/robot.h>
#include <webots/keyboard.h>
#include <webots/motor.h>
#include <stdio.h>

#define TIME_STEP 64

int main() {
  wb_robot_init();
  
  WbDeviceTag arm1 = wb_robot_get_device("joint1");
  WbDeviceTag arm2 = wb_robot_get_device("joint2");
  WbDeviceTag arm3 = wb_robot_get_device("joint3");

  wb_motor_set_position(arm1, INFINITY);
  wb_motor_set_position(arm2, INFINITY);
  wb_motor_set_position(arm3, INFINITY);

  wb_keyboard_enable(TIME_STEP);

  while (wb_robot_step(TIME_STEP) != -1) {
    int key = wb_keyboard_get_key();  

    if (key == WB_KEYBOARD_UP) {
      wb_motor_set_velocity(arm1, 1.0);  
    } else if (key == WB_KEYBOARD_DOWN) {
      wb_motor_set_velocity(arm1, -1.0); 
    } else {
      wb_motor_set_velocity(arm1, 0.0);  
    }

    if (key == WB_KEYBOARD_RIGHT) {
      wb_motor_set_velocity(arm2, 1.0);  
    } else if (key == WB_KEYBOARD_LEFT) {
      wb_motor_set_velocity(arm2, -1.0); 
    } else {
      wb_motor_set_velocity(arm2, 0.0); 
    }

    if (key == 'A') {
      wb_motor_set_velocity(arm3, 1.0);  
    } else if (key == 'D') {
      wb_motor_set_velocity(arm3, -1.0); 
    } else {
      wb_motor_set_velocity(arm3, 0.0);  
    }
  }

  wb_robot_cleanup();

  return 0;
}
