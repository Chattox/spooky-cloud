"""
    Spooky Cloud
    
    Light controls for a 50 LED WS2812 strip, powered by a Pimoroni Plasma 2350
    
    Lets see how quickly Pimoroni's proprietary hardware goes south this time
"""

from pimoroni import Button
from Spooky import Spooky

button_a = Button("BUTTON_A")
button_boot = Button("USER_SW")
cloud = Spooky(50)

cloud.startup()