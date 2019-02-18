import pygame
import sys
from pygame.locals import *
import time
import numpy as np

'''Test the BitScope Library by connecting with the first available device
and performing a capture and dump. Requires BitLib 2.0 and Python Bindings'''

from bitlib import *
import matplotlib.pyplot as plt
import numpy as np

MY_DEVICE = 0 # one open device only
MY_CHANNEL = 0 # channel to capture and display
MY_TRIGGER_CHANNEL = 1 # channel to capture and display
MY_PROBE_FILE = "" # default probe file if unspecified 
MY_MODE = BL_MODE_DUAL # preferred capture mode
MY_RATE = 1000000 # default sample rate we'll use for capture.
MY_SIZE = 5000 # number of samples we'll capture (simply a connectivity test)
TRUE = 1

MODES = ("FAST","DUAL","MIXED","LOGIC","STREAM")
SOURCES = ("POD","BNC","X10","X20","X50","ALT","GND")

# Open the first device found
BL_Open(MY_PROBE_FILE,1)
#
# Open succeeded (report versions).
#
print " Library: %s (%s)" % (
    BL_Version(BL_VERSION_LIBRARY),
    BL_Version(BL_VERSION_BINDING))
#
# Select this device (optional, it's already selected).
#
BL_Select(BL_SELECT_DEVICE,MY_DEVICE)
#
# Report the link, device and channel information.
#
print "    Link: %s" % BL_Name(0)
print "BitScope: %s (%s)" % (BL_Version(BL_VERSION_DEVICE),BL_ID())
print "Channels: %d (%d analog + %d logic)" % (
    BL_Count(BL_COUNT_ANALOG)+BL_Count(BL_COUNT_LOGIC),
    BL_Count(BL_COUNT_ANALOG),BL_Count(BL_COUNT_LOGIC))
#
# Determine which modes the device supports.
#
print "   Modes:" + "".join(["%s" % (
    (" " + MODES[i]) if i == BL_Mode(i) else "") for i in range(len(MODES))])
#
# Report canonic capture specification in LOGIC (if supported) or FAST mode (otherwise.
#
BL_Mode(BL_MODE_LOGIC) == BL_MODE_LOGIC or BL_Mode(BL_MODE_FAST)
print " Capture: %d @ %.0fHz = %fs (%s)" % (
    BL_Size(),BL_Rate(),
    BL_Time(),MODES[BL_Mode()])
#
# Report the maximum offset range (if the device supports offsets).
#
BL_Range(BL_Count(BL_COUNT_RANGE));
if BL_Offset(-1000) != BL_Offset(1000):
    print "  Offset: %+.4gV to %+.4gV" % (
        BL_Offset(1000), BL_Offset(-1000))
#
# Report the input source provided by the device and their respective ranges.
#
for i in range(len(SOURCES)):
    if i == BL_Select(2,i):
        print "     %s: " % SOURCES[i] + " ".join(["%5.2fV" % BL_Range(n) for n in range(BL_Count(3)-1,-1,-1)])
#
# Set up to capture MY_SIZE samples at MY_RATE from CH-A via the POD input using the highest range.
#
BL_Mode(MY_MODE) # prefered capture mode

# For the trigger channel
#BL_Select(BL_SELECT_CHANNEL,MY_TRIGGER_CHANNEL); # Select trigger channel
#print BL_Trigger(1.0,BL_TRIG_RISE); # optional when untriggered */

# For the pulse channel
BL_Select(BL_SELECT_CHANNEL,MY_CHANNEL); # choose the channel
#BL_Size(100); # optional default BL_MAX_SIZE
#print BL_Rate(BL_MAX_RATE); # optional, default BL_MAX_RATE
#print BL_Intro(0.000005); # optional, default BL_ZERO
BL_Select(BL_SELECT_SOURCE,BL_SOURCE_POD); # use the POD input */
#print BL_Offset(-6.21); # optional, default 0
print BL_Offset(-4.6); # optional, default 0
print BL_Range(BL_Count(BL_COUNT_RANGE)); # maximum range
#print BL_Trigger(0.1-4.6,BL_TRIG_RISE); # optional when untriggered */
#print BL_Trigger(0.2,BL_TRIG_RISE); # optional when untriggered */
print BL_Trigger(-4.5,BL_TRIG_RISE); # optional when untriggered */
BL_Enable(TRUE); # at least one channel must be initialised 

np.random.seed(10)

rate = 200

# Define the pulse shape: a simple gaussian
def pulse_shape(t, t0=5., a=12., sigma=1.):
    return np.exp(-((t - t0)/(2.*sigma))**2) * a

# Digitize to 8 bit plus saturation
resolution = 2**8
digitization_bins = np.linspace(0, 12, resolution+1)
digitization_step = digitization_bins[1] - digitization_bins[0]
def digitize(y):
    y = np.digitize(y, digitization_bins)
    y = np.clip(y, a_min=1, a_max=resolution)
    return y - 1

def acquire():
    BL_Trace(BL_TRACE_FOREVER)
    data = np.array(BL_Acquire())[:100]
    amp = np.max(data) - np.min(data)
    plt.plot(data, "o-")
    plt.show()
    return amp

# set up pygame
pygame.init()

# set up the window
window_width = 500
window_height = 400
window_surface = pygame.display.set_mode((window_width, window_height), 0, 32)
pygame.display.set_caption('Trex DAQ')

# set up the colors
# WHITE = (220, 220, 204)
text_color = (220, 220, 204)
WHITE = (63, 63, 63)
BLACK = (63, 63, 63)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
# BLUE = (0, 0, 255)
# BLUE = (73, 114, 189)
BLUE = (220, 220, 204)

# set up fonts
monospace_font = pygame.font.SysFont("DejaVu Sans Mono", 14)


# draw the white background onto the surface
window_surface.fill(WHITE)

def draw_prompt(text=": Hello World!"):

    # set up the text
    text = monospace_font.render(text, True, text_color, BLACK)
    textRect = text.get_rect()
    textRect.top = window_height - 18
    textRect.left = 2

    # draw the text's background rectangle onto the surface
    pygame.draw.rect(window_surface, BLACK, (0, textRect.top - 2, window_width, textRect.height + 4))
    # draw the text onto the surface
    window_surface.blit(text, textRect)

# draw a green polygon onto the surface
pygame.draw.polygon(window_surface, GREEN, ((146, 0), (291, 106), (236, 277), (56, 277), (0, 106)))

def draw_hist(bin_contents, logscale=False):
    n = len(bin_contents)
    max_content = max(max(bin_contents), 1)
    max_content = 10**(int(np.log10(max_content))+1)

    if logscale:
        max_content = np.log(max_content)

    w = 500
    h = 400 - 20

    y_scale = float(h)/max_content
    x_scale = w/float(n+1)

    points = [(0.,h)]
    for i, c in enumerate(bin_contents):
        if logscale:
            c = max(0, np.log(c))
        points.append((x_scale*i, h - y_scale*c))
        points.append((x_scale*(i+1), h - y_scale*c))
    points.append((w,h))

    pygame.draw.polygon(window_surface, BLUE, points)

# draw some blue lines onto the surface
pygame.draw.line(window_surface, BLUE, (60, 60), (120, 60), 4)
pygame.draw.line(window_surface, BLUE, (120, 60), (60, 120))
pygame.draw.line(window_surface, BLUE, (60, 120), (120, 120), 4)

# draw a blue circle onto the surface
pygame.draw.circle(window_surface, BLUE, (300, 50), 20, 0)

# draw a red ellipse onto the surface
pygame.draw.ellipse(window_surface, RED, (300, 250, 40, 80), 1)


# get a pixel array of the surface
pixArray = pygame.PixelArray(window_surface)
pixArray[480][380] = BLACK
del pixArray

# draw the window onto the screen
pygame.display.update()

refresh_rate = 1./60

# initialize amplitudes  storage
amplitudes = np.array([], dtype=np.float)

is_running = False
logscale = False
show_prompt = True
prompt_mode = False

prompt_text = ""

about_to_clear = False
about_to_clear_time = 0

# the value for saturation is 9.1640625
bins = np.linspace(0, 9.165, 2**11+1)

# run the game loop
while True:

    if about_to_clear and time.time() - about_to_clear_time >= 0.5:
        about_to_clear = False

    if is_running:
        window_surface.fill(WHITE)
        amplitudes_new = [acquire()]
        amplitudes = np.array(np.append(amplitudes, amplitudes_new), dtype=np.float)

        draw_hist(np.histogram(amplitudes, bins)[0],
                  logscale=logscale)
    else:
        time.sleep(refresh_rate)

    # draw the window onto the screen
    if show_prompt:
        draw_prompt(prompt_text)
    pygame.display.update()

    for event in pygame.event.get():

        if event.type == QUIT:
            BL_Close()
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                prompt_text = ""
                prompt_mode = False

                if show_prompt:
                    draw_prompt(prompt_text)
                pygame.display.update()

            if prompt_mode:
                if event.key == pygame.K_BACKSPACE:
                    prompt_text = prompt_text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    prompt_text = prompt_text[:-1]
                elif event.key == pygame.K_RETURN:
                    if prompt_text[:3] == ":w ":
                        file_name = str(prompt_text[3:].strip())
                        print(list(amplitudes))
                        #np.savetxt(file_name, amplitudes, header="# amplitudes")
                        prompt_text = "\""+file_name+"\" written"
                        prompt_mode = False
                    elif prompt_text.strip() == ":set logscale":
                        logscale = not logscale
                        prompt_mode = False
                    elif prompt_text.strip() == ":q":
                        BL_Close()
                        pygame.quit()
                        sys.exit()
                    else:
                        prompt_text = "Not a command: " + prompt_text[1:]
                        prompt_mode = False
                else:
                    prompt_text = prompt_text + event.unicode

                if show_prompt:
                    draw_prompt(prompt_text)
                pygame.display.update()

            else:
                if event.key == pygame.K_l:
                    logscale = not logscale
                    window_surface.fill(WHITE)
                    draw_hist(np.histogram(amplitudes, bins)[0],
                              logscale=logscale)
                    if show_prompt:
                        draw_prompt(prompt_text)
                    pygame.display.update()

                if event.key == pygame.K_SPACE:
                    is_running = not is_running

                if event.key == 59: # colon
                    if not prompt_mode:
                        prompt_mode = True
                        prompt_text = ":"
                    if show_prompt:
                        draw_prompt(prompt_text)
                    pygame.display.update()

                if event.key == pygame.K_d:
                    if not is_running:
                        if about_to_clear and time.time() - about_to_clear_time < 0.5:
                            about_to_clear = False
                            amplitudes = np.array([], dtype=np.int)
                            window_surface.fill(WHITE)
                            if show_prompt:
                                draw_prompt(prompt_text)
                            pygame.display.update()
                        about_to_clear = True
                        about_to_clear_time = time.time()