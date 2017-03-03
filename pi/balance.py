import time
import server
import threading

from server import a_star
from ahrs import AHRS
from operator import sub

ahrs = AHRS()

ANGLE_OFFSET = -9

def read_encoder_deltas():
  counts = a_star.read_encoders()
  deltas = map(sub, counts, read_encoder_deltas.last_counts)
  read_encoder_deltas.last_counts = counts
  return deltas

read_encoder_deltas.last_counts = (0, 0)

def set_motors():
  e = read_encoder_deltas()
  p = ahrs.angle + ANGLE_OFFSET + sum(e) / 20 - server.throttle_cmd / 10
  set_motors.i += p
  set_motors.i = min(400, max(-400, set_motors.i))
  d = p - set_motors.last_p
  set_motors.last_p = p

  spd = p * 6 + set_motors.i * 1.3 + d * 13
  spd = min(300, max(-300, spd))

  if abs(ahrs.angle + ANGLE_OFFSET) <= 60:
    a_star.motors(spd + server.steering_cmd, spd - server.steering_cmd)
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

server_thread = threading.Thread(target = server.app.run, kwargs = {'host': '0.0.0.0', 'debug': False})
server_thread.daemon = True
server_thread.start()

while True:
  t = time.time()
  ahrs.update_angle_gyro()

  if t - last_tick > 0.02: # 50 Hz
    ahrs.correct_angle_accel()
    set_motors()
    last_tick = t



