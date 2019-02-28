import pygame
import sys
from pygame.locals import *
import time
import numpy as np
import h5py

'''Test the BitScope Library by connecting with the first available device
and performing a capture and dump. Requires BitLib 2.0 and Python Bindings'''

import matplotlib.pyplot as plt
import numpy as np
import concurrent.futures

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

# set up pygame
pygame.init()

# set up the window
window_width = 512
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

    w = window_width
    h = window_height - 20

    y_scale = float(h)/max_content
    x_scale = w/float(n+1)
    x_scale = 1

    points = [(0.,h)]
    for i, c in enumerate(bin_contents):
        if logscale:
            c = max(0, np.log(c))
        points.append((i, h))
        points.append((i, h - y_scale*c))
        points.append((i, h))
        #points.append((x_scale*i, h - y_scale*c))
        #points.append((x_scale*(i+1), h - y_scale*c))
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

# initialize amplitudes  storage
amplitudes = []
data = []

is_running = False
logscale = False
show_prompt = True
prompt_mode = False

prompt_text = ""

about_to_clear = False
about_to_clear_time = 0

# the value for saturation is 9.1640625
#bins = np.linspace(0, 9.165, 2**11+1)
bins = np.linspace(0, 9.165, 2**8+1)
#bins = np.linspace(0, 2**8, 2**8+1)

acquisitor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

quitting = False

def acquire():
    print("started acquisition")
    while True:
        if is_running:
            #print(line)
            line = input().strip()
            line = line.split(" ")
            line = [float(x) for x in line[1:]]
            amp = np.max(line) - np.min(line)
            #print(amp)
            amplitudes.append(amp)
            data.append(line)
        else:
            dump = input()
        if quitting:
            return

acquisitor.submit(acquire)

refresh_rate = 1./60

# run the game loop
while True:

    if about_to_clear and time.time() - about_to_clear_time >= 0.5:
        about_to_clear = False

    time.sleep(refresh_rate)

    if is_running:
        window_surface.fill(WHITE)

        draw_hist(np.histogram(amplitudes, bins)[0], logscale=logscale)

    # draw the window onto the screen
    if show_prompt:
        draw_prompt(prompt_text)
    pygame.display.update()

    for event in pygame.event.get():

        if event.type == QUIT:
            quitting = True
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
                        file_name = file_name.replace(".h5", "").replace(".hdf", "")
                        np.savetxt(file_name, np.array(data), header="data")
                        with h5py.File(file_name+".h5", 'w') as hf:
                            hf.create_dataset("data",  data=np.array(data))
                            hf.create_dataset("amplitudes",  data=np.array(amplitudes))
                        prompt_text = "\""+file_name+"\".h5 written"
                        prompt_mode = False
                    elif prompt_text.strip() == ":set logscale":
                        logscale = not logscale
                        prompt_mode = False
                    elif prompt_text.strip() == ":q":
                        quitting = True
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
                            amplitudes = []
                            data = []
                            window_surface.fill(WHITE)
                            if show_prompt:
                                draw_prompt(prompt_text)
                            pygame.display.update()
                        about_to_clear = True
                        about_to_clear_time = time.time()
