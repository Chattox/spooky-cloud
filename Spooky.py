import plasma
import colours

class Spooky:
    """
        Controller for 50 LED WS2812 light strip
    """
    
    def __init__(self, num_leds):
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
        
    def startup(self):
        """
            Start process for lights
        """
        
        self.strip.start()
        for i in range(self.NUM_LEDS):
            self.strip.set_rgb(i, 0, 0, 0)
            
    def cycle_background(self):
        """
            Cycles all LEDs through a selection of colours
        """
        if self.current_bg_i >= len(self.bg_colours) - 1:
            self.current_bg_i = 0
        else:
            self.current_bg_i += 1
            
        print(self.bg_colours[self.current_bg_i])
        r, g, b = self.bg_colours[self.current_bg_i]
        print(r)
        print(g)
        print(b)
        
        for i in range(self.NUM_LEDS):
            self.strip.set_rgb(i, r, g, b)