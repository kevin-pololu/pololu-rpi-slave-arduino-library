import time
import server
import threading

from server import a_star
from ahrs import AHRS
from pygame import mixer
from os import path

ahrs = AHRS()

ANGLE_OFFSET = -8.5

def subtract_16_bit(a, b):
  diff = (a - b) & 0xFFFF
  if (diff & 0x8000):
    diff -= 0x10000
  return diff
  
def read_encoder_deltas():
  counts = a_star.read_encoders()
  deltas = map(subtract_16_bit, counts, read_encoder_deltas.last_counts)
  read_encoder_deltas.last_counts = counts
  return deltas

read_encoder_deltas.last_counts = (0, 0)

def set_motors():
  e = read_encoder_deltas()
  a = ahrs.angle + ANGLE_OFFSET
  p = a + sum(e) / 20 - server.throttle_cmd / 10
  set_motors.i += p
  set_motors.i = min(400, max(-400, set_motors.i))
  d = p - set_motors.last_p
  set_motors.last_p = p

  spd = p * 5 + set_motors.i * 1.3 + d * 15
  spd = min(300, max(-300, spd))

  if abs(a) <= 60:
    a_star.motors(spd + server.steering_cmd, spd - server.steering_cmd)
    if not set_motors.up:
      set_motors.up = True
      set_motors.up_time = time.time()

    if server.music_enable and not mixer.music.get_busy():
      mixer.music.play(-1)
    elif not server.music_enable and mixer.music.get_busy():
      mixer.music.stop()


  elif set_motors.up:
    a_star.motors(0, 0)
    set_motors.up = False
    mixer.music.stop()
    if time.time() - set_motors.up_time > 3:
      fail.play()
    print "fell over! angle with offset: {}".format(a)

  return

set_motors.up = False
set_motors.up_time = 0
set_motors.last_p = 0
set_motors.i = 0

mixer.pre_init(frequency=44100, channels=1)
mixer.init()
mixer.music.load(path.join('media', 'music.ogg'))
fail = mixer.Sound(path.join('media', 'fail.ogg'))

bat_v = float(a_star.read_battery_millivolts()[0]) / 1000
print "Battery voltage: {:.2f} V ({:.2f} V/cell)".format(bat_v, bat_v / 6)
ahrs.enable_imu()
print 'Calibrating...'
ahrs.calibrate_gyro()
print 'done'
ahrs.reset_angle_accel()
last_tick = time.time()


server_thread = threading.Thread(target = server.app.run, kwargs = {'host': '0.0.0.0', 'debug': False})
server_thread.daemon = True
server_thread.start()

try:
  while True:
    t = time.time()
    ahrs.update_angle_gyro()

    if t - last_tick > 0.02: # 50 Hz
      ahrs.correct_angle_accel()
      set_motors()
      last_tick = t

finally:
  a_star.motors(0, 0)

