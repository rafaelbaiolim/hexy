
Arcbotics hexapod robot frame with Raspberry Pi Zero and Adafruit 16 channel I2C servo driver
- [Hexy Documentation](http://hexyrobot.wordpress.com)
- [Hexy Transcript](https://medium.com/@mithi/a-raspberry-pi-hexy-transcript-62533c69a566)

Quickstart
----------
 
The easiest way to get this up and running, on your raspberry pi zero is to do the following on the terminal via ssh.

```
$ ssh YOUR.RPI.IP.ADDR -l pi 
$ cd /home/pi
$ git clone https://github.com/mithi/hexy.git
$ sudo python setup.py install
$ python -m hexy.demo.demo1
$ python -m hexy.demo.demo2
$ python -m hexy.demo.demo3
```

Class Hierarchy:
```
HexapodCore > Hexapod > HexapodPro > DancingHexapod
```

Sample usage when running python interpreter from anywhere in your system... 

```
>>> from hexy.robot.hexapod import Hexapod
>>> hexy = Hexapod()
>>> hexy.boot_up()
>>> hexy.walk(swing = 25, repetitions = 10)
>>> hexy.walk(swing = -25, repetitions = 10)
>>> hexy.rotate(offset = 40, repetitions = 7)
>>> hexy.rotate(offset = -40, repetitions = 7)
>>> hexy.shut_down()
```

Also try this...

```
>>> from hexy.robot.pro import HexapodPro
>>> hexy = HexapodPro()
>>> hexy.lie_flat()
>>> hexy.get_up()
>>> hexy.shake_head()
>>> hexy.wave()
>>> hexy.point()
>>> hexy.type_stuff()
>>> hexy.lie_down()
>>> hexy.off()
```

And this :)

```
>>> from hexy.robot.dancing import DancingHexapod
>>> hexy = DancingHexapod()
>>> hexy.boot_up()
>>> hexy.night_fever()
>>> hexy.default()
>>> hexy.dance_tilt()
>>> hexy.squat(angle = 60)
>>> hexy.thriller()
>>> hexy.lie_down()
>>> hexy.curl_up(die = True)
```
Configuration & Calibration V2
------------------------------
V2 has the same idea and execution of V1 tool.
Execute GUI V2 using: 
```
python scripts/v2/detect_controllers.py
```
The configs. will be applied to current 
selected radio box on RIGHT, LEFT and HEAD area, 
each area has one Controller and Channel.

> VNC session will need to be setted with a resolution 
of  at least 1024x768, increase GPU memory 
for better process result too. 
Use [Raspberry Pi doc](https://www.raspberrypi.org/documentation/configuration/config-txt/memory.md). to apply appropried value. 

![alt text](https://raw.githubusercontent.com/rafaelbaiolim/hexy/config/scripts/v2/screen/servo-tester_v2.png)

Configuration & Calibration V1
------------------------------
You may have your servo controllers on different addresses,
or your servos plugged into different ports. You will also
have to calibrate the min and max range of each of your
servos, since these settings vary from servo to servo.

These settings are all stored in the hexy.cfg file. To help
with this task, there is a GUI program scripts/detect_controllers.py.

To use this program:
 1. First, edit the "controllers" line in hexy.cfg to contain
    the addresses of your controllers. i2cdetect on the command
    line can help you learn what to put here. See https://learn.adafruit.com/adafruit-16-channel-servo-driver-with-raspberry-pi/configuring-your-pi-for-i2c
    for tips on how to do this.
 2. Next, run "python scripts/v1/detect_controllers.py" from the top
    level hexy directory. This will pop up a GUI, so you need
    to have a VNC session open to your raspberry pi for this to
    work.
 3. Within the gui, go one-by-one for each joint and make sure
    it is assigned to the correct controller and port. You can
    use "test min," "test center," "test max" both to make sure
    you are using the correct controller/port, and also to
    calibrate the minimum and maximum setting for each servo.
    Make sure you click "save" after you are done with each joint.
    This will save the settings back to the hexy.cfg file.
    
