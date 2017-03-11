// Copyright Pololu Corporation.  For more information, see https://www.pololu.com/
reset_drive = true
block_set_drive = false
mouse_dragging = false

function init() {
  poll()
  $("#joystick").bind("touchstart",touchmove)
  $("#joystick").bind("touchmove",touchmove)
  $("#joystick").bind("touchend",touchend)
  $("#joystick").bind("mousedown",mousedown)
  $(document).bind("mousemove",mousemove)
  $(document).bind("mouseup",mouseup)
}

function poll() {
  /*$.ajax({url: "status.json"}).done(update_status)*/
  setTimeout(poll, 100)
  if(reset_drive && !block_set_drive)
  {
    setDrive(0,0);
    reset_drive = false
  }
}

function update_status(json) {
  s = JSON.parse(json)
  $("#button0").html(s["buttons"][0] ? '1' : '0')
  $("#button1").html(s["buttons"][1] ? '1' : '0')
  $("#button2").html(s["buttons"][2] ? '1' : '0')

  $("#battery_millivolts").html(s["battery_millivolts"])

  $("#analog0").html(s["analog"][0])
  $("#analog1").html(s["analog"][1])
  $("#analog2").html(s["analog"][2])
  $("#analog3").html(s["analog"][3])
  $("#analog4").html(s["analog"][4])
  $("#analog5").html(s["analog"][5])

  setTimeout(poll, 100)
}

function touchmove(e) {
  e.preventDefault()
  touch = e.originalEvent.touches[0] || e.originalEvent.changedTouches[0];
  dragTo(touch.pageX, touch.pageY)
}

function mousedown(e) {
  e.preventDefault()
  mouse_dragging = true
}

function mouseup(e) {
  if(mouse_dragging)
  {
    e.preventDefault()
    mouse_dragging = false
    reset_drive = true
  }
}

function mousemove(e) {
  if(mouse_dragging)
  {
    e.preventDefault()
    dragTo(e.pageX, e.pageY)
  }
}

function dragTo(x, y) {
  elm = $('#joystick').offset();
  x = x - elm.left;
  y = y - elm.top;
  w = $('#joystick').width()
  h = $('#joystick').height()

  x = (x-w/2.0)/(w/2.0)
  y = (y-h/2.0)/(h/2.0)

  if(x < -1) x = -1
  if(x > 1) x = 1
  if(y < -1) y = -1
  if(y > 1) y = 1

  reset_drive = false
  setDrive(Math.round(-y * 100), Math.round(x * 100))
}

function touchend(e) {
  e.preventDefault()
  reset_drive = true
}

function setDrive(throttle, steering) {
  $("#joystick").html("Throttle: " + throttle + "<br>Steering: "+ steering)

  if(block_set_drive) return
  block_set_drive = true

  $.ajax({url: "drive/"+throttle+","+steering}).done(setDriveDone)
}

function setDriveDone() {
  block_set_drive = false
}

function setLeds() {
  led0 = $('#led0')[0].checked ? 1 : 0
  led1 = $('#led1')[0].checked ? 1 : 0
  led2 = $('#led2')[0].checked ? 1 : 0
  $.ajax({url: "leds/"+led0+","+led1+","+led2})
}

function setMusic() {
  music_enable = $('#music')[0].checked ? 1 : 0
  $.ajax({url: "music/"+music_enable})
}

function playNotes() {
  notes = $('#notes').val()
  $.ajax({url: "play_notes/"+notes})
}

function speak() {
  text = $('#speak-text').val()
  $.ajax({url: "speak/"+text})
}

function shutdown() {
  if (confirm("Really shut down the Raspberry Pi?"))
    return true
  return false
}
