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
        self.flash_brightness_max = 100
        # Lightning duration range in ms
        self.flash_duration_min = 5
        self.flash_duration_max = 75
        # Delay between lightning flashes range in ms
        self.next_flash_delay_min = 0
        self.next_flash_delay_max = 75
        # Range for brightness variance of background lighting
        self.b_variance_min = 0
        self.b_variance_max = 50
        # Whether lightning routine is active
        self.lightning_active = False
        # Delay range for lightning strikes in seconds
        self.lightning_delay_min = 0
        self.lightning_delay_max = 5
        # Whether lightning is localised or fills the whole grid
        self.localised = True
        # Range of localised lightning radius
        self.flash_radius_min = 0
        self.flash_radius_max = 2
        # Range for number of extra strike on a local strike
        self.extra_strikes_min = 0
        self.extra_strikes_max = 3
        # Max distance away from previous strike extra strikes can be
        self.max_extra_distance = 1
        # Range for delay between extra strikes in ms
        self.extra_strike_delay_min = 0
        self.extra_strike_delay_max = 50
             
    def startup(self):
        """
            Start process for lights
        """
        
        self.strip.start()
        self.clear()
        self.plasma_led.set_rgb(0, 255, 0)
        for i in range(len(self.bg_colours)):
            self.bg_colours[i] = self.convert_hsv(self.bg_colours[i])
        
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
        for i in range(self.NUM_LEDS):
            self.strip.set_hsv(i, *colour)
            
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
            v_col = self.vary_brightness(colour)
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
        v = random.randint(self.b_variance_min, self.b_variance_max) / 100
        # Decide if positive or negative variance
        i = random.randint(0,1)
        if i == 0:
            # We don't want the decrease in brightness to be
            # as severe as the increase
            v = v * 0.75
            v = -v
            
        varied_col = list(col)
        
        brightness = varied_col[2] + v
        if brightness > 1.0:
            brightness = 1.0
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
        # If not active, start lightning loop
        if self.lightning_active is False:
            self.lightning_active = True
            self.plasma_led.set_rgb(0, 0, 255)
            print("Starting lightning loop")
            while self.lightning_active is True:
                print("Lightning!")
                self.do_lightning()
                # Delay until next lightning strike in seconds
                delay = random.randint(self.lightning_delay_min, self.lightning_delay_max)
                print(f"Delay until next strike: {delay} seconds")
                # Very rough count of time passed
                elapsed = 0.0
                while elapsed < delay:
                    if button_a.read():
                        self.lightning_active = False
                        self.plasma_led.set_rgb(0, 255, 0)
                        print("Stopping lightning loop")
                        break
                    elapsed += 0.1
                    time.sleep(0.1)
        
    def do_lightning(self):
        """
            Decides whether lightning will be localised or full grid, then does a lightning strike
        """
        
        if self.localised:
            # Still have a 1 in 20 chance of full lightning
            i = random.randint(1, 20)
            if i == 10:
                self.full_lightning()
            else:
                self.localised_lightning()
        else:
            self.full_lightning()
            
    def get_area_coords(self, origin_yx):
        """
            Return corner coords of a square area on the led grid based
            on given origin coordinates and a randomly generated radius
            
            Args:
                origin_xy: tuple of centre point y x coordinates
                
            Returns:
                tuple containing 2 tuples of bottom left and top right coordinates
        """
        
        o_y, o_x = origin_yx
        
        radius = random.randint(self.flash_radius_min, self.flash_radius_max)
        rad_min_x = o_x - radius
        rad_max_x = o_x + radius
        rad_min_y = o_y - radius
        rad_max_y = o_y + radius
        # Cap points within grid bounds
        rad_min_x = 0 if rad_min_x < 0 else rad_min_x
        rad_max_x = len(self.led_grid[0]) - 1 if rad_max_x > len(self.led_grid[0]) - 1 else rad_max_x
        rad_min_y = 0 if rad_min_y < 0 else rad_min_y
        rad_max_y = len(self.led_grid) - 1 if rad_max_y > len(self.led_grid) - 1 else rad_max_y
        
        return ((rad_min_x, rad_min_y), (rad_max_x, rad_max_y))
    
    def get_area_leds(self, coords):
        """
            Get a list of LED addresses within a set of coordinates
            
            Args:
                coords: a tuple containing 2 tuples of bottom left and top right coordinates
                
            Returns:
                a list of ints corresponding to LEDs on the grid
        """
        
        b_l, t_r = coords
        
        # Get LEDs within flash grid bounds
        flash_leds = []
        if b_l == t_r:
            flash_leds.append(self.led_grid[b_l[1]][b_l[0]])
        else:
            min_x, min_y = b_l
            max_x, max_y = t_r
            # + 1 to ranges to get full square since range() isn't inclusive of max arg
            for i in range((max_y - min_y) + 1):
                for j in range((max_x - min_x) + 1):
                    target_y = min_y + i
                    target_x = min_x + j
                    # skip the end of the top row since there's no led there
                    if target_y == 2 and target_x == 16:
                        continue
                    else:
                        # 1 third of the time, move a target LED around to randomise the flash shape
                        # a little bit
                        chance = random.random()
                        if chance > 0.33:
                            flash_leds.append(self.led_grid[target_y][target_x])
                        else:
                            k = random.random()
                            move = 1 if k >= 0.5 else -1
                            move_x = target_x + move
                            if move_x < 0:
                                move_x = 0
                            elif move_x > len(self.led_grid[target_y]) - 1:
                                move_x = len(self.led_grid[target_y]) - 1
                                
                            # Keep shifting the LED if the target is already present, but
                            # after 20 failed attempts just drop the LED so the loop doesn't
                            # get stuck
                            count = 0
                            while move_x in flash_leds:
                                print("led already present")
                                move_x = move_x + move
                                if move_x < 0:
                                    move_x = 0
                                elif move_x > len(self.led_grid[target_y]) - 1:
                                    move_x = len(self.led_grid[target_y]) - 1
                                if count >= 20:
                                    print("giving up on this led")
                                    break
                                else:
                                    count += 1
                                    
                            flash_leds.append(self.led_grid[target_y][move_x])
                        
        return flash_leds
        
    def localised_lightning(self):
        """
            Flashes clusters of LEDs around the grid to simulate
            localised lighting strikes within the cloud
        """
        
        origin_points = []
        # First pick an origin point for the initial strike and add that to the list
        origin_y = random.randint(0, len(self.led_grid) - 1)
        origin_x = random.randint(0, len(self.led_grid[origin_y]) - 1)
        origin_points.append((origin_y, origin_x))
        
        # Then add the additional origin points, not too far from the previous
        num_extras = random.randint(self.extra_strikes_min, self.extra_strikes_max)
        for i in range(num_extras):
            y_dist = random.randint(-self.max_extra_distance, self.max_extra_distance)
            x_dist = random.randint(-self.max_extra_distance, self.max_extra_distance)
            # Make sure they actually move somewhere
            while y_dist == 0 and x_dist == 0:
                y_dist = random.randint(-self.max_extra_distance, self.max_extra_distance)
                x_dist = random.randint(-self.max_extra_distance, self.max_extra_distance)
            
            y = origin_points[-1][0] + y_dist
            x = origin_points[-1][1] + x_dist
            
            # Make sure they're not out of bounds
            y = 0 if y < 0 else y
            y = len(self.led_grid) - 1 if y > len(self.led_grid) - 1 else y
            x = 0 if x < 0 else x
            x = len(self.led_grid[y]) - 1 if x > len(self.led_grid[y]) - 1 else x
            
            # Finally, add to the list
            origin_points.append((y, x))
            
        print(origin_points)
        # Then start going through the strikes
        for i in range(len(origin_points)):
            # Get area corner coords
            corners = self.get_area_coords(origin_points[i])
            # Get area LEDs
            flash_leds = self.get_area_leds(corners)
            
            # Do the lightning
            flash_count = random.randint(self.flash_count_min, self.flash_count_max)
            bg_c = self.get_cur_bg()
        
            for i in range(flash_count):
                # get flash brightness
                f_b = random.randint(self.flash_brightness_min, self.flash_brightness_max)
                f_c = (0.0, 0.0, f_b)
                for i in range(len(flash_leds)):
                    self.strip.set_hsv(flash_leds[i], *f_c)
                time.sleep_ms(random.randint(self.flash_duration_min, self.flash_duration_max))
                for i in range(len(flash_leds)):
                    self.strip.set_hsv(flash_leds[i], *bg_c)
                time.sleep_ms(random.randint(self.next_flash_delay_min, self.next_flash_delay_max))
            # Reset flashed LEDs to varied bg
            for i in range(len(flash_leds)):
                    varied_bg = self.vary_brightness(bg_c)
                    self.strip.set_hsv(flash_leds[i], *varied_bg)
            
            # Wait out delay until next strike
            time.sleep_ms(random.randint(self.extra_strike_delay_min, self.extra_strike_delay_max))
                 
    def full_lightning(self):
        """
            Flashes all LEDs on the strip in a lightning strike
        """
        
        flash_count = random.randint(self.flash_count_min, self.flash_count_max)
        bg_c = self.get_cur_bg()
        
        for i in range(flash_count):
            # get flash brightness
            f_b = random.randint(self.flash_brightness_min, self.flash_brightness_max)
            flash_colour = (0.0, 0.0, f_b)
            self.set_all(flash_colour)
            time.sleep_ms(random.randint(self.flash_duration_min, self.flash_duration_max))
            self.set_all(bg_c)
            time.sleep_ms(random.randint(self.next_flash_delay_min, self.next_flash_delay_max))
        # Reset LEDs to varied background
        for i in range(self.NUM_LEDS):
                varied_bg = self.vary_brightness(bg_c)
                self.strip.set_hsv(i, *varied_bg)
        