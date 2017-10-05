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
        width = 600
        height = 630
        self.auto_test = False;
        
        # A "-1" in the size parameter instructs wxWidgets to use the default size.
        # In this case, we select 200px width and the default height.
        wx.Frame.__init__(self, parent, title=title, size=(width, height))
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        self.cfg = config.Config()
        self.servo_list = [k for k in self.cfg.keys() if k.startswith('addr_')]
        self.controller_list = self.cfg['controllers']
        self.channel_list = map(str, range(0, 15))
        self.Center()

        #ID CONSTANTS 
        #.:RADIO BUTTONS
        self.RBR_ADDR = 1;
        self.RBL_ADDR = 2;
        self.RBH_ADDR = 3;

        #.:PULSE SLIDER
        self.SR_MAX = 4;
        self.SR_MIN = 5;

        self.SL_MAX = 6;
        self.SL_MIN = 7;

        self.SH_MAX = 8;
        self.SH_MIN = 9;

        #.:TESTS BUTTONS HEAD
        self.BTH_MIN = 12;
        self.BTH_MAX = 13;
        self.BTH_CENTER = 14;

        #.:TESTS BUTTONS LEFT
        self.BTL_MIN = 15;
        self.BTL_MAX = 16;
        self.BTL_CENTER = 17;

        #.:TESTS BUTTONS RIGHT
        self.BTR_MIN = 18;
        self.BTR_MAX = 19;
        self.BTR_CENTER = 20;

        #.:RELAX BUTTONS
        self.BTR_RELAX = 21;
        self.BTL_RELAX = 22;
        self.BTH_RELAX = 23;

        #.:COMBOBOX CHANNEL/CONTROLS
        self.CBR_CTRL = 10;
        self.CBR_CNNL = 11;
        
        self.CBL_CTRL = 24;
        self.CBL_CNNL = 25;

        self.CBH_CTRL = 26;
        self.CBH_CNNL = 27;

        self.RIGHT_SIDE_LIST = [
                self.RBR_ADDR,self.BTR_RELAX,self.BTR_MAX,
                self.BTR_MIN,self.BTR_CENTER,self.CBR_CTRL,
                self.CBR_CNNL,self.SR_MIN,self.SR_MAX
        ]

        self.LEFT_SIDE_LIST = [
                self.RBL_ADDR,self.BTL_RELAX,self.BTL_MAX,
                self.BTL_MIN,self.BTL_CENTER,self.CBL_CTRL,
                self.CBL_CNNL,self.SL_MIN,self.SL_MAX
        ]


        self.drivers = [PWM(int(addr.split('x')[-1], 16))
                        for addr in self.controller_list]
        for driver in self.drivers:
                driver.setPWMFreq(60)

        ################################################################
        # Joint Selector
        y_offset = 10
        self.lbl_servo_box = wx.StaticText(self, label="Joint Position",
                                           pos=(10, y_offset))
        y_offset += 20
        x_col1_offset = 10
        x_col2_offset = 120
        x_col3_offset = 10

        self.checkbox_r = [];
        self.checkbox_l = [];
        self.checkbox_h = [];

        for channelStr in self.servo_list:
                if(channelStr.startswith('addr_r')):
                        self.checkbox_r.append(channelStr)
                elif(channelStr.startswith('addr_l')):          
                        self.checkbox_l.append(channelStr)
                else:
                        self.checkbox_h.append(channelStr)
        
        self.servo_right_box = wx.RadioBox(self,pos = (x_col1_offset,y_offset),label="RIGHT",choices = self.checkbox_r ,
        majorDimension = 1, style = wx.RB_GROUP,id=self.RBR_ADDR)
        self.Bind(wx.EVT_RADIOBOX, self.on_servo_select, self.servo_right_box)
        
        self.servo_left_box = wx.RadioBox(self, pos = (x_col2_offset,y_offset),label="LEFT", choices = self.checkbox_l ,
        majorDimension = 1,id=self.RBL_ADDR)
        self.Bind(wx.EVT_RADIOBOX, self.on_servo_select, self.servo_left_box)
        y_offset+= 270
        
        self.servo_head_box = wx.RadioBox(self, pos = (x_col3_offset,y_offset),label="HEAD", choices = self.checkbox_h ,
        majorDimension = 1,size=(210,50),id=self.RBH_ADDR)
        self.Bind(wx.EVT_RADIOBOX, self.on_servo_select, self.servo_head_box)
        ################################################################
        # Controller & Channel Selector - RIGHT
        y_offset=50
        x_offset= 240

        wx.StaticBox(self, label="Controller/Channel Right", pos=(x_offset - 5, y_offset - 20),
          size=(350, 205))
        
        self.lbl_controller = wx.StaticText(self,
                                            label="Controller",
                                            pos=(x_offset, y_offset))

        self.lbl_channel = wx.StaticText(self,
                                         label="Channel",
                                         pos=(380, y_offset))

        y_offset += 25
        self.ctrlr_right_box = wx.ComboBox(self, pos=(x_offset, y_offset), size=(120, 30),
                                     choices=self.controller_list,id=self.CBR_CTRL,
                                     value=self.controller_list[0],
                                     style=wx.CB_READONLY)
        self.chnnl_right_box = wx.ComboBox(self, pos=(380, y_offset), size=(120, 30),
                                     choices=self.channel_list,id=self.CBR_CNNL,
                                     value=self.channel_list[0],
                                     style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.on_controller_select, self.ctrlr_right_box)
        self.Bind(wx.EVT_COMBOBOX, self.on_channel_select, self.chnnl_right_box)
        y_offset += 40

        ################################################################
        # Pulse Slider - RIGHT
        self.min_right_slider = wx.Slider(self, pos=(x_offset, y_offset), size=(120, 50),
                                    minValue=150, maxValue=750,id=self.SR_MIN,
                                    style=wx.SL_LABELS)
        self.max_right_slider = wx.Slider(self, pos=(x_offset+140, y_offset), size=(120, 50),
                                    minValue=150, maxValue=750,id=self.SR_MAX,
                                    style=wx.SL_LABELS)
        y_offset += 60
        self.lbl_min = wx.StaticText(self,
                                     label="Min Pulse",
                                     pos=(x_offset, y_offset))
        self.lbl_max = wx.StaticText(self,
                                     label="Max Pulse",
                                     pos=(x_offset+140, y_offset))

        self.Bind(wx.EVT_SCROLL, self.on_min_change, self.min_right_slider)
        self.Bind(wx.EVT_SCROLL, self.on_max_change, self.max_right_slider)
        y_offset += 30
        # Test Buttons RIGHT
        self.test_min = wx.Button(self, pos=(x_offset, y_offset), size=(60, 25), id=self.BTR_MIN,
                                  label='Min')
        self.test_center = wx.Button(self, pos=(x_offset+70, y_offset), size=(70, 25),id=self.BTR_CENTER,
                                     label='Center')
        self.test_max = wx.Button(self, pos=(x_offset+150, y_offset), size=(60, 25), id=self.BTR_MAX,
                                  label='Max')
        self.test_relax = wx.Button(self, pos=(x_offset+223, y_offset), size=(60, 25), id=self.BTR_RELAX,
                                  label='Relax')
        y_offset += 70
        self.Bind(wx.EVT_BUTTON,self.on_test_min, self.test_min)
        self.Bind(wx.EVT_BUTTON,self.on_test_center, self.test_center)        
        self.Bind(wx.EVT_BUTTON,self.on_test_max, self.test_max)
        self.Bind(wx.EVT_BUTTON,self.on_relax, self.test_relax)
        ################################################################
        # Controller & Channel Selector - LEFT
        y_offset=260

        wx.StaticBox(self, label="Controller/Channel Left", pos=(x_offset - 5, y_offset - 20),
          size=(350, 205))
        
        self.lbl_controller = wx.StaticText(self,
                                            label="Controller",
                                            pos=(x_offset, y_offset))

        self.lbl_channel = wx.StaticText(self,
                                         label="Channel",
                                         pos=(380, y_offset))

        y_offset += 25
        self.ctrlr_left_box = wx.ComboBox(self, pos=(x_offset, y_offset), size=(120, 30),
                                     choices=self.controller_list,id=self.CBL_CTRL,
                                     value=self.controller_list[0],
                                     style=wx.CB_READONLY)
        self.chnnl_left_box = wx.ComboBox(self, pos=(380, y_offset), size=(120, 30),
                                     choices=self.channel_list,id=self.CBL_CNNL,
                                     value=self.channel_list[0],
                                     style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.on_controller_select, self.ctrlr_left_box)
        self.Bind(wx.EVT_COMBOBOX, self.on_channel_select, self.chnnl_left_box)
        y_offset += 40

        ################################################################
        # Pulse Slider - LEFT

        self.min_left_slider = wx.Slider(self, pos=(x_offset, y_offset), size=(120, 50),
                                    minValue=150, maxValue=750,id=self.SL_MAX,
                                    style=wx.SL_LABELS)
        self.max_left_slider = wx.Slider(self, pos=(x_offset+140, y_offset), size=(120, 50),
                                    minValue=150, maxValue=750,
                                    style=wx.SL_LABELS,id=self.SL_MIN)
        y_offset += 60
        self.lbl_min = wx.StaticText(self,
                                     label="Min Pulse",
                                     pos=(x_offset, y_offset))
        self.lbl_max = wx.StaticText(self,
                                     label="Max Pulse",
                                     pos=(x_offset+140, y_offset))
        y_offset += 30
        self.Bind(wx.EVT_SCROLL, self.on_min_change, self.min_left_slider)
        self.Bind(wx.EVT_SCROLL, self.on_max_change, self.max_left_slider)

       # Test Buttons LEFT
        self.test_min = wx.Button(self, pos=(x_offset, y_offset), size=(60, 25), id=self.BTL_MIN,
                                  label='Min')
        self.test_center = wx.Button(self, pos=(x_offset+70, y_offset), size=(70, 25),id=self.BTL_CENTER,
                                     label='Center')
        self.test_max = wx.Button(self, pos=(x_offset+150, y_offset), size=(60, 25), id=self.BTL_MAX,
                                  label='Max')
        self.test_relax = wx.Button(self, pos=(x_offset+223, y_offset), size=(60, 25), id=self.BTL_RELAX,
                                  label='Relax')
        y_offset += 70
        self.Bind(wx.EVT_BUTTON,self.on_test_min, self.test_min)
        self.Bind(wx.EVT_BUTTON,self.on_test_center, self.test_center)        
        self.Bind(wx.EVT_BUTTON,self.on_test_max, self.test_max)
        self.Bind(wx.EVT_BUTTON,self.on_relax, self.test_relax)

        ################################################################
        # Controller & Channel Selector - HEAD
        y_offset=385
        wx.StaticBox(self, label="Controller/Channel Head", pos=(5, y_offset - 20),
          size=(220, 212))
        self.lbl_controller = wx.StaticText(self,
                                            label="Controller",
                                            pos=(10, y_offset))

        self.lbl_channel = wx.StaticText(self,
                                         label="Channel",
                                         pos=(120, y_offset))

        y_offset += 25
        self.ctrlr_head_box = wx.ComboBox(self, pos=(10, y_offset), size=(90, 30),
                                     choices=self.controller_list,id=self.CBH_CTRL,
                                     value=self.controller_list[0],
                                     style=wx.CB_READONLY)
        self.chnnl_head_box = wx.ComboBox(self, pos=(120, y_offset), size=(100, 30),
                                     choices=self.channel_list,id=self.CBH_CNNL,
                                     value=self.channel_list[0],
                                     style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.on_controller_select, self.ctrlr_head_box)
        self.Bind(wx.EVT_COMBOBOX, self.on_channel_select, self.chnnl_head_box)

        y_offset += 40

        ################################################################
        # Pulse Slider - HEAD
        self.min_head_slider = wx.Slider(self, pos=(10, y_offset), size=(100, 50),
                                    minValue=150, maxValue=750,id=self.SH_MIN,
                                    style=wx.SL_LABELS)
        self.max_head_slider = wx.Slider(self, pos=(120, y_offset), size=(100, 50),
                                    minValue=150, maxValue=750, id=self.SH_MAX,
                                    style=wx.SL_LABELS)
        y_offset += 60
        self.lbl_min = wx.StaticText(self,
                                     label="Min Pulse",
                                     pos=(10, y_offset))
        self.lbl_max = wx.StaticText(self,
                                     label="Max Pulse",
                                     pos=(10+130, y_offset))
        self.Bind(wx.EVT_SCROLL, self.on_min_change, self.min_head_slider)
        self.Bind(wx.EVT_SCROLL, self.on_max_change, self.max_head_slider)
        y_offset += 30

        # Test Buttons HEAD
        self.test_min = wx.Button(self, pos=(10, y_offset), size=(50, 25), id=self.BTH_MIN,
                                  label='Min')
        self.test_min.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.test_center = wx.Button(self, pos=(65, y_offset), size=(50, 25),id=self.BTH_CENTER,
                                     label='Center')
        self.test_center.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.test_max = wx.Button(self, pos=(59*2, y_offset), size=(50, 25), id=self.BTH_MAX,
                                  label='Max')
        self.test_max.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.test_relax = wx.Button(self, pos=(57*3, y_offset), size=(50, 25), id=self.BTH_RELAX,
                                  label='Relax')
        self.test_relax.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        
        self.Bind(wx.EVT_BUTTON, self.on_test_min, self.test_min)
        self.Bind(wx.EVT_BUTTON, self.on_test_center, self.test_center)        
        self.Bind(wx.EVT_BUTTON, self.on_test_max, self.test_max)
        self.Bind(wx.EVT_BUTTON,self.on_relax, self.test_relax)

        ################################################################
        # Bottom Buttons
        y_offset -= 80
        self.relax_all = wx.Button(self, pos=(235, y_offset), size=(72, 25),
                                  label='Relax All')
        self.relax_all.SetBackgroundColour((0,191,255)) 
        self.relax_all.SetForegroundColour(wx.Colour(34,35,38)) 
        self.Bind(wx.EVT_BUTTON, self.on_relax_all, self.relax_all)

        self.auto_mode = wx.Button(self, pos=(320, y_offset), size=(90, 25),
                                  label='Auto Mode')
        self.auto_mode.SetBackgroundColour((255,165,0)) 
        self.auto_mode.SetForegroundColour(wx.Colour(34,35,38)) 

        self.Bind(wx.EVT_BUTTON, self.on_auto_mode, self.auto_mode)

        self.save = wx.Button(self, pos=(420, y_offset), size=(70, 25),
                                  label='Save')
        self.save.SetBackgroundColour((70,160,73))
        self.save.SetForegroundColour(wx.Colour(34, 35, 38))
        
        self.Bind(wx.EVT_BUTTON, self.on_save, self.save)

        # A multiline TextCtrl - This is here to show how the events
        # work in this program, don't pay too much attention to it
        self.logger = wx.TextCtrl(self, pos=(235,495), size=(350,80),
                                  style=wx.TE_MULTILINE | wx.TE_READONLY)


        # Set the initial box values
        self.load_settings(self.checkbox_r[0],self.RBR_ADDR)
        self.load_settings(self.checkbox_l[0],self.RBL_ADDR)
        self.load_settings(self.checkbox_h[0],self.RBH_ADDR)

    def load_settings(self, servo_name,fromId = -1):
        """
        Load the servo settings from the config
        """
        controller, channel, min_pulse, max_pulse = self.cfg[servo_name]
        if(fromId == self.RBR_ADDR):
                self.ctrlr_right_box.SetSelection(controller)
                self.chnnl_right_box.SetSelection(channel)
                self.min_right_slider.SetValue(min_pulse)
                self.max_right_slider.SetValue(max_pulse)
        elif(fromId == self.RBL_ADDR):
                self.ctrlr_left_box.SetSelection(controller)
                self.chnnl_left_box.SetSelection(channel)
                self.min_left_slider.SetValue(min_pulse)
                self.max_left_slider.SetValue(max_pulse)
        else:
                self.ctrlr_head_box.SetSelection(controller)
                self.chnnl_head_box.SetSelection(channel)
                self.min_head_slider.SetValue(min_pulse)
                self.max_head_slider.SetValue(max_pulse)

        self.logger.AppendText('Select servo: %s @ %s.%d\n'
                               % (servo_name,
                                  self.controller_list[controller],
                                  channel))

    def save_setting(self):
        """
        Saves the current GUI settings to the config (but not to disk)
        after detect what side of hex is going to save
        """
        servo_name = self.servo_right_box.GetStringSelection()
        if len(servo_name) == 0:
            raise + oRuntimeError('No Servo Right Name')
        self.save_by_location(self.RBR_ADDR,servo_name);
            
        servo_name = self.servo_left_box.GetStringSelection()
        if len(servo_name) == 0:
            raise + oRuntimeError('No Servo Left Name')
        self.save_by_location(self.RBL_ADDR,servo_name);
        
        servo_name = self.servo_head_box.GetStringSelection()
        if len(servo_name) == 0:
            raise + oRuntimeError('No Servo Head Name')
        self.save_by_location(self.RBH_ADDR,servo_name);        

    def save_by_location(self,fromID,servo_name):
        """
        Saves the current GUI 
        """
        self.cfg[servo_name] = self.settings_from_gui(fromID)
        self.cfg.save()

    def settings_from_gui(self,fromID):
        """
        Load the settings from the GUI.
        """
        if(fromID == self.RBR_ADDR or fromID in self.RIGHT_SIDE_LIST):
            channel = self.chnnl_right_box.GetSelection()
            controller = self.ctrlr_right_box.GetSelection()
            pwm_min = self.min_right_slider.GetValue()
            pwm_max = self.max_right_slider.GetValue()
        elif(fromID == self.RBL_ADDR or fromID in self.LEFT_SIDE_LIST):
            channel = self.chnnl_left_box.GetSelection()
            controller = self.ctrlr_left_box.GetSelection()
            pwm_min = self.min_left_slider.GetValue()
            pwm_max = self.max_left_slider.GetValue()
        else:
            channel = self.chnnl_head_box.GetSelection()
            controller = self.ctrlr_head_box.GetSelection()
            pwm_min = self.min_head_slider.GetValue()
            pwm_max = self.max_head_slider.GetValue()                   
        return controller, channel, pwm_min, pwm_max

    def on_servo_select(self, event):
        self.load_settings(event.GetString(),event.GetEventObject().GetId())

    def on_controller_select(self, event):
        self.logger.AppendText('Controller Select: %s\n' % event.GetString())

    def on_channel_select(self, event):
        self.logger.AppendText('Channel Select: %s\n' % event.GetString())

    def on_auto_mode(self, event):
        self.auto_test = not self.auto_test
        self.logger.AppendText('Auto Test Mode is ' + ("Enabled" if self.auto_test else "Disabled") + '\n')

    def on_min_change(self, event):
        if self.auto_test:
                self.on_test_min(event) 
        pass
    
    def on_max_change(self, event):
        if self.auto_test:
                self.on_test_max(event)
        pass

    def on_test_min(self, event):
        controller, channel, pwm_min, pwm_max = self.settings_from_gui(event.GetEventObject().GetId())
        self.logger.AppendText('Test Min: %s.%s => %s\n'
                               % (self.controller_list[controller], channel, pwm_min))
        driver = self.drivers[controller]
        driver.setPWM(channel, 0, pwm_min)

    def on_test_center(self, event):
        controller, channel, pwm_min, pwm_max = self.settings_from_gui(event.GetEventObject().GetId())
        pwm_center = (pwm_min + pwm_max) / 2
        self.logger.AppendText('Test Center: %s.%s => %s\n'
                                % (self.controller_list[controller], channel, pwm_center))
        driver = self.drivers[controller]
        driver.setPWM(channel, 0, pwm_center)

    def on_test_max(self, event):
        controller, channel, pwm_min, pwm_max = self.settings_from_gui(event.GetEventObject().GetId())
        self.logger.AppendText('Test Max: %s.%s => %s\n'
                               % (self.controller_list[controller], channel, pwm_max))
        driver = self.drivers[controller]
        driver.setPWM(channel, 0, pwm_max)

    def on_relax(self, event):
        controller, channel, pwm_min, pwm_max = self.settings_from_gui(event.GetEventObject().GetId())
        driver = self.drivers[controller]
        driver.setPWM(channel, 0, 0)
        self.logger.AppendText('Relax: %s.%s => %s\n'
                               % (self.controller_list[controller], channel, 0))

    def on_relax_all(self, event):
        for j in range(0,len(self.servo_list)):
            driver = self.drivers[self.cfg[self.servo_list[j]][0]]
            driver.setPWM(self.cfg[self.servo_list[j]][1], 0, 0)
        self.logger.AppendText('All servos relaxed\n')

    def on_save(self, event):
        self.save_setting()
        self.cfg.dumps()
        self.logger.AppendText("Current seting(s) of screen saved\n")

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