#!/usr/bin/env python
"""
Command to scan the i2c bus to locate controllers.
"""

import sys, argparse, logging
import wx

from hexy import config
from hexy.comm.pwm import PWM


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        width = 400
        height = 600
        
        # A "-1" in the size parameter instructs wxWidgets to use the default size.
        # In this case, we select 200px width and the default height.
        wx.Frame.__init__(self, parent, title=title, size=(width, height))
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        self.cfg = config.Config()
        self.servo_list = [k for k in self.cfg.keys() if k.startswith('addr_')]
        self.controller_list = self.cfg['controllers']
        self.channel_list = map(str, range(0, 15))

        self.drivers = [PWM(int(addr.split('x')[-1], 16))
                        for addr in self.controller_list]
        for driver in self.drivers:
            driver.setPWMFreq(60)

        ################################################################
        # Joint Selector
        y_offset = 10
        self.lbl_servo_box = wx.StaticText(self, label="Joint Position",
                                           pos=(10, y_offset))
        y_offset += 25
        self.servo_box = wx.ComboBox(self, pos=(10, y_offset), size=(120, 30),
                                     choices=self.servo_list,
                                     value=self.servo_list[0],
                                     style=wx.CB_READONLY)
        y_offset += 30
        self.servo_box.SetSelection(0)
        self.Bind(wx.EVT_COMBOBOX, self.on_servo_select, self.servo_box)


        ################################################################
        # Controller & Channel Selector
        self.lbl_controller = wx.StaticText(self,
                                            label="Controller",
                                            pos=(10, y_offset))
        self.lbl_channel = wx.StaticText(self,
                                         label="Channel",
                                         pos=(130, y_offset))

        y_offset += 25
        self.ctrlr_box = wx.ComboBox(self, pos=(10, y_offset), size=(120, 30),
                                     choices=self.controller_list,
                                     value=self.controller_list[0],
                                     style=wx.CB_READONLY)
        self.chnnl_box = wx.ComboBox(self, pos=(130, y_offset), size=(120, 30),
                                     choices=self.channel_list,
                                     value=self.channel_list[0],
                                     style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.on_controller_select, self.ctrlr_box)
        self.Bind(wx.EVT_COMBOBOX, self.on_channel_select, self.chnnl_box)
        y_offset += 30

        ################################################################
        # Pulse Slider
        self.min_slider = wx.Slider(self, pos=(10, y_offset), size=(120, 40),
                                    minValue=150, maxValue=750,
                                    style=wx.SL_LABELS)
        self.max_slider = wx.Slider(self, pos=(130, y_offset), size=(120, 40),
                                    minValue=150, maxValue=750,
                                    style=wx.SL_LABELS)
        y_offset += 40
        self.lbl_min = wx.StaticText(self,
                                     label="Min Pulse",
                                     pos=(10, y_offset))
        self.lbl_max = wx.StaticText(self,
                                     label="Max Pulse",
                                     pos=(130, y_offset))
        y_offset += 40
        self.Bind(wx.EVT_SCROLL, self.on_min_change, self.min_slider)
        self.Bind(wx.EVT_SCROLL, self.on_max_change, self.max_slider)

        ################################################################
        # Test Buttons
        self.test_min = wx.Button(self, pos=(10, y_offset), size=(80, 40),
                                  label='Test Min')
        self.test_center = wx.Button(self, pos=(90, y_offset), size=(80, 40),
                                     label='Test Center')
        self.test_max = wx.Button(self, pos=(170, y_offset), size=(80, 40),
                                  label='Test Max')
        y_offset += 40
        self.Bind(wx.EVT_BUTTON, self.on_test_min, self.test_min)
        self.Bind(wx.EVT_BUTTON, self.on_test_center, self.test_center)        
        self.Bind(wx.EVT_BUTTON, self.on_test_max, self.test_max)

        ################################################################
        # Bottom Buttons
        y_offset += 20
        self.relax = wx.Button(self, pos=(10, y_offset), size=(80, 40),
                                  label='Relax')
        self.Bind(wx.EVT_BUTTON, self.on_relax, self.relax)

        self.save = wx.Button(self, pos=(100, y_offset), size=(80, 40),
                                  label='Save')
        self.Bind(wx.EVT_BUTTON, self.on_save, self.save)

        y_offset += 40


        # A multiline TextCtrl - This is here to show how the events
        # work in this program, don't pay too much attention to it
        self.logger = wx.TextCtrl(self, pos=(0,300), size=(width,300),
                                  style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Set the initial box values
        self.load_settings(self.servo_list[0])

    def load_settings(self, servo_name):
        """
        Load the servo settings from the config
        """
        controller, channel, min_pulse, max_pulse = self.cfg[servo_name]

        self.ctrlr_box.SetSelection(controller)
        self.chnnl_box.SetSelection(channel)
        self.min_slider.SetValue(min_pulse)
        self.max_slider.SetValue(max_pulse)
        self.logger.AppendText('Select servo: %s @ %s.%d\n'
                               % (servo_name,
                                  self.controller_list[controller],
                                  channel))

    def save_setting(self):
        """
        Saves the current GUI settings to the config (but not to disk)
        """
        servo_selection = self.servo_box.GetCurrentSelection()
        servo_name = self.servo_list[servo_selection]
        if len(servo_name) == 0:
            raise RuntimeError('No Servo Name')
        self.cfg[servo_name] = self.settings_from_gui()
        self.cfg.save()

    def settings_from_gui(self):
        """
        Load the settings from the GUI.
        """
        channel = self.chnnl_box.GetSelection()
        controller = self.ctrlr_box.GetSelection()
        pwm_min = self.min_slider.GetValue()
        pwm_max = self.max_slider.GetValue()
        return controller, channel, pwm_min, pwm_max

    def on_servo_select(self, event):
        self.load_settings(event.GetString())

    def on_controller_select(self, event):
        self.logger.AppendText('Controller Select: %s\n' % event.GetString())

    def on_channel_select(self, event):
        self.logger.AppendText('Channel Select: %s\n' % event.GetString())

    def on_min_change(self, event):
        pass
    
    def on_max_change(self, event):
        pass

    def on_test_min(self, event):
        controller, channel, pwm_min, pwm_max = self.settings_from_gui()
        self.logger.AppendText('Test Min: %s.%s => %s\n'
                               % (self.controller_list[controller], channel, pwm_min))
        driver = self.drivers[controller]
        driver.setPWM(channel, 0, pwm_min)

    def on_test_center(self, event):
        controller, channel, pwm_min, pwm_max = self.settings_from_gui()
        pwm_center = (pwm_min + pwm_max) / 2
        self.logger.AppendText('Test Center: %s.%s => %s\n'
                                % (self.controller_list[controller], channel, pwm_center))
        driver = self.drivers[controller]
        driver.setPWM(channel, 0, pwm_center)

    def on_test_max(self, event):
        controller, channel, pwm_min, pwm_max = self.settings_from_gui()
        self.logger.AppendText('Test Max: %s.%s => %s\n'
                               % (self.controller_list[controller], channel, pwm_max))
        driver = self.drivers[controller]
        driver.setPWM(channel, 0, pwm_max)

    def on_relax(self, event):
        controller, channel, pwm_min, pwm_max = self.settings_from_gui()
        driver = self.drivers[controller]
        driver.setPWM(channel, 0, 0)

    def on_save(self, event):
        self.save_setting()
        self.cfg.dumps()

# Gather our code in a main() function
def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)
    app = wx.App(False)
    frame = MainWindow(None, 'Servo Tester')
    frame.Show(True)
    app.MainLoop()


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  parser = argparse.ArgumentParser( 
                                    description = "Does a thing to some stuff.",
                                    epilog = "As an alternative to the commandline, params can be placed in a file, one per line, and specified on the commandline like '%(prog)s @params.conf'.",
                                    fromfile_prefix_chars = '@' )
  # TODO Specify your real parameters here.
  #parser.add_argument(
  #                    "argument",
  #                    help = "pass ARG to the program",
  #                    metavar = "ARG")
  parser.add_argument(
                      "-v",
                      "--verbose",
                      help="increase output verbosity",
                      action="store_true")
  args = parser.parse_args()
  
  # Setup logging
  if args.verbose:
    loglevel = logging.DEBUG
  else:
    loglevel = logging.INFO
  
  main(args, loglevel)
