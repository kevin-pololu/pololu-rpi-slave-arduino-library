import time

from ahrs import AHRS
from a_star import AStar
from operator import sub

ahrs = AHRS()
a_star = AStar()

ANGLE_OFFSET = -8

def read_encoder_deltas():
  counts = a_star.read_encoders()
  deltas = map(sub, counts, read_encoder_deltas.last_counts)
  read_encoder_deltas.last_counts = counts
  return deltas

read_encoder_deltas.last_counts = (0, 0)

def set_motors():
  p = ahrs.angle + ANGLE_OFFSET + sum(read_encoder_deltas()) / 20
  set_motors.i += p
  set_motors.i = min(400, max(-400, set_motors.i))
  d = p - set_motors.last_p
  set_motors.last_p = p

  spd = p * 6 + set_motors.i * 1.3 + d * 11
  spd = min(300, max(-300, spd))

  if abs(ahrs.angle + ANGLE_OFFSET) <= 60:
    a_star.motors(spd, spd)
  else:
    a_star.motors(0, 0)

  return

set_motors.last_p = 0
set_motors.i = 0

ahrs.enable_imu()
print 'Calibrating...'
ahrs.calibrate_gyro()
print 'done'
ahrs.reset_angle_accel()
last_tick = time.time()

while True:
  t = time.time()
  ahrs.update_angle_gyro()

  if t - last_tick > 0.02: # 50 Hz
    ahrs.correct_angle_accel()
    set_motors()
    last_tick = t



