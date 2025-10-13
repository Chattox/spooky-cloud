import random
import time
import plasma
from pimoroni import RGBLED
import colours

class Spooky:
    """
        Controller for 50 LED WS2812 light strip
    """
    
    def __init__(self, num_leds):
        self.plasma_led = RGBLED()
        self.NUM_LEDS = num_leds
        self.strip = plasma.WS2812(self.NUM_LEDS, color_order=plasma.COLOR_ORDER_RGB)
        self.bg_colours = [colours.BLANK, colours.RED, colours.GREEN, colours.BLUE, colours.ORANGE, colours.TEAL]
        # Index of self.bg_colours of the currently selected background colour
        self.current_bg_i = 0
        self.led_grid = [
            [0, 5, 6, 11, 12, 17, 18, 23, 24, 29, 30, 35, 36, 41, 42, 47, 48],
            [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49],
            [2, 3, 8, 9, 14, 15, 20, 21, 26, 27, 32, 33, 38, 39, 44, 45],
            ]
        # Lightning flash count range
        self.flash_count_min = 5
        self.flash_count_max = 15
        # Lightning brightness range
        self.flash_brightness_min = 10
        self.flash_brightness_max = 255
        # Lightning duration range in ms
        self.flash_duration_min = 5
        self.flash_duration_max = 75
        # Delay between lightning flashes range in ms
        self.next_flash_delay_min = 0
        self.next_flash_delay_max = 75
        # Range for brightness variance of background lighting
        self.b_variance_min = 0
        self.b_variance_max = 50
             
    def startup(self):
        """
            Start process for lights
        """
        
        self.strip.start()
        self.clear()
        self.plasma_led.set_rgb(0, 255, 0)
        
    def convert_hsv(self, hsv):
        """
            The plasma library requires HSV values to be weird because pimoroni are
            weird little guys. Decided I'd rather keep the constants to real HSV
            values and just convert them as needed
            
            Args:
                hsv: tuple of real HSV value
                
            Returns:
                tuple of HSV value converted to pimoroni requirements
        """
        
        h, s, v = hsv
        new_h = h / 360
        new_s = s / 100
        new_v = v / 100
        
        return (new_h, new_s, new_v)
        
    def get_cur_bg(self):
        """
            Returns current background colour
            
            Returns:
                Tuple of current bg colour as HSV
        """
        return self.bg_colours[self.current_bg_i]
            
    def set_all(self, colour):
        """
            Set all LEDs in the strip to the same colour at once
            
            Args:
                colour: Tuple containing HSV value
        """
        h, s, v = self.convert_hsv(colour)
        for i in range(self.NUM_LEDS):
            self.strip.set_hsv(i, h, s, v)
            
    def clear(self):
        """
            Set all lights to 0, 0, 0, effectively turning them off
        """
        self.set_all(colours.BLANK)
            
    def cycle_background(self):
        """
            Cycles all LEDs through a selection of colours
        """
        if self.current_bg_i >= len(self.bg_colours) - 1:
            self.current_bg_i = 0
        else:
            self.current_bg_i += 1
            
        colour = self.get_cur_bg()
        
        # Vary the brightness on each LED a little to make it look more natural
        for i in range(self.NUM_LEDS):
            v_col = self.convert_hsv(self.vary_brightness(colour))
            self.strip.set_hsv(i, *v_col)
            
    def vary_brightness(self, col):
        """
            Varies the brightness of an HSV value by a random amount within the
            specified min and max
            
            Args:
                col: Tuple of HSV value
                
            Returns:
                Tuple of new HSV value
        """
        # If colour is blank, skip
        if col == (0.0, 0.0, 0.0):
            return col
        
        # Get variance
        v = random.randint(self.b_variance_min, self.b_variance_max)
        # Decide if positive or negative variance
        i = random.randint(0,1)
        if i == 0:
            # We don't want the decrease in brightness to be
            # as severe as the increase
            v = v * 0.75
            v = -v
            
        varied_col = list(col)
        
        brightness = varied_col[2] + v
        if brightness > 100.0:
            brightness = 100.0
        elif brightness < 0.0:
            brightness = 0.0
        
        varied_col[2] = brightness
            
        return tuple(varied_col)
            
            
    def toggle_lightning(self, button_a):
        """
            Toggles lightning effects, button_a is required to break out of the while loop
            since I'm not touching threading on a 2350
            
            Args:
                button_a: button_a instance of Button
        """
        self.do_lightning()
        
    def do_lightning(self):
        """
            Flashes LEDs in a lightning effect
        """
        flash_count = random.randint(self.flash_count_min, self.flash_count_max)
        
        for i in range(flash_count):
            # get flash brightness
            f_b = random.randint(self.flash_brightness_min, self.flash_brightness_max)
            flash_colour = (f_b, f_b, f_b)
            self.set_all(flash_colour)
            time.sleep_ms(random.randint(self.flash_duration_min, self.flash_duration_max))
            self.set_all(self.get_cur_bg())
            time.sleep_ms(random.randint(self.next_flash_delay_min, self.next_flash_delay_max))
        