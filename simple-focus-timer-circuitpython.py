import time, os, board
import neopixel, touchio
from rainbowio import colorwheel

OFF = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

# Settings
pixels_count = 8
# How many LEDs on a strip to glow on each touch
pixels_increment = 1
# Brightness, max is 1, go nuts if you like
pixels_brightness = 0.1
# Each LED is a 5 minutes timer
timer_seconds = (60 * 5)
# See the color constants above, define a new color if you like
color = WHITE

# Initialise lights
pixel_pin = board.GP16
pixels = neopixel.NeoPixel(pixel_pin, pixels_count, brightness=pixels_brightness, auto_write=True)

# Initialise touch pin
touch_pin = touchio.TouchIn(board.GP15)

on_count = 0
prev_count = 0

# Helper to get rounded time monotonic
def time_monotonic():
    return round(time.monotonic())

# A cool rainbow effect, we will use this on startup and when the timer ends
def rainbow_cycle(wait, count):
    for color in range(count):
        for pixel in range(len(pixels)):  # pylint: disable=consider-using-enumerate
            pixel_index = (pixel * 256 // len(pixels)) + color * 5
            pixels[pixel] = colorwheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)
    pixels.fill(OFF)

# Glows or switches off the LEDs
def update_pixels():
    pixels.fill(OFF)
    if on_count:
        for p in range(on_count):
            pixels[p] = color
        
rainbow_cycle(0.01, 80)
start_time = time_monotonic()

while True:
    prev_count = on_count
    now_time = time_monotonic()
    if touch_pin.value:
        # Detected a touch
        if on_count >= pixels_count:
            # Still less than 'pixels_count', increase the timer count
            on_count = 0
            update_pixels()
        else:
            # Cant go above 'pixels_count', reset to 0
            on_count += pixels_increment
            update_pixels()
        # Touch will always reset the start time
        start_time = time_monotonic()

    elapsed_min = now_time - start_time
    if elapsed_min >= timer_seconds and on_count:
        # Each tick (timer_seconds) will trigger this
        # Reduce 'pixels_increment' which will switch off 'pixels_increment' number of LEDs
        start_time = time_monotonic()
        on_count -= pixels_increment
        update_pixels()
        if on_count is 0:
            # A little show for you
            time.sleep(1)
            rainbow_cycle(0.01, 80)

    time.sleep(0.2)
