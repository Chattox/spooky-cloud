import plasma

class Spooky:
    """
        Controller for 50 LED WS2812 light strip
    """
    
    def __init__(self, num_leds):
        self.NUM_LEDS = num_leds
        self.strip = plasma.WS2812(self.NUM_LEDS)
        
    def startup(self):
        """
            Start process for lights
        """
        
        self.strip.start()
        for i in range(self.NUM_LEDS):
            self.strip.set_rgb(i, 0, 0, 0)