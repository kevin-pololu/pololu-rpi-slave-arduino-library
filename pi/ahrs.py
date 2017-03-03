import lsm6
import time
import math

class AHRS(object):
  def __init__(self):
    self.imu = lsm6.LSM6()
    self.angle = 0
    self.gyro_y_offset = 0
    self.last_update = time.time()

  def enable_imu(self):
    self.imu.enable()

  def calibrate_gyro(self, readings = 1000):
    self.gyro_y_offset = 0
    for _ in range(readings):
      while not self.imu.gyro_data_available():
        pass
      self.gyro_y_offset += self.imu.read_gyro().y
    self.gyro_y_offset /= readings

  def update_angle_gyro(self):
    gy = self.imu.read_gyro().y - self.gyro_y_offset
    t = time.time()
    dt = t - self.last_update
    self.last_update = t
    self.angle += gy * 0.070 * dt
    return self.angle

  def read_angle_accel(self):
    a = self.imu.read_accel()
    return math.atan2(a.z, a.x) * 180 / math.pi

  def reset_angle_accel(self):
    self.angle = self.read_angle_accel()
    self.last_update = time.time()

  def correct_angle_accel(self):
    a = self.imu.read_accel()
    magnitude = math.sqrt((a.x * 0.000244) ** 2 + (a.y * 0.000244) ** 2 + (a.z * 0.000244) ** 2)

    # confidence is 0 at magnitude 0.8, 1 at 1, 0 at 1.2
    confidence = 1 - 5 * abs(1 - magnitude)
    confidence = max(0, min(1, confidence))
    weight = confidence / 10

    self.angle = weight * self.read_angle_accel() + (1 - weight) * self.angle


    



    
    
  
