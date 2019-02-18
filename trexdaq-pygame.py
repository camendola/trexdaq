import pygame
import sys
from pygame.locals import *
from concurrent.futures import ThreadPoolExecutor
import time
import numpy as np

# executor for acquisition
acquisitor = ThreadPoolExecutor(max_workers=1)

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

def acquire(timeout):
    start_time = time.time()
    data = []
    while True:
        t = np.linspace(0, 10, 101)
        a = 0.5 + np.random.exponential(scale=5.)
        y = pulse_shape(t, a=a)
        y = digitize(y)
        line = "{0:.4f} ".format(a) + " ".join(["{0}".format(yi) for yi in y])
        time.sleep(1./rate)
        line = line.strip().split(" ")
        debug_amplitudes = float(line[0])
        measurements = [int(s) for s in line[1:]]
        amplitude = max(measurements) - min(measurements)
        data.append(amplitude)
        if time.time() - start_time > timeout:

            return data
    return data

# set up pygame
pygame.init()

# set up the window
window_width = 500
window_height = 400
window_surface = pygame.display.set_mode((window_width, window_height), 0, 32)
pygame.display.set_caption('Hello world!')

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
amplitudes = np.array([], dtype=np.int)

is_running = False
logscale = False
show_prompt = True
prompt_mode = False

bins = np.linspace(0, 2**8, 2**8+1)

prompt_text = ""

about_to_clear = False
about_to_clear_time = 0

# run the game loop
while True:

    time.sleep(refresh_rate)

    if about_to_clear and time.time() - about_to_clear_time >= 0.5:
        about_to_clear = False

    if is_running:
        window_surface.fill(WHITE)
        amplitudes_new = acquisitor.submit(acquire, refresh_rate).result()
        amplitudes = np.array(np.append(amplitudes, amplitudes_new), dtype=np.int)

        draw_hist(np.bincount(amplitudes, minlength=2**8),
                  logscale=logscale)

        # pygame.draw.rect(window_surface, WHITE, (0, 0, 500, 400))
        # pygame.draw.rect(window_surface, BLACK, (0, 0, 500, 400), 1)

        # draw the window onto the screen
        if show_prompt:
            draw_prompt(prompt_text)
        pygame.display.update()

    for event in pygame.event.get():

        if event.type == QUIT:
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
                        file_name = prompt_text[3:].strip()
                        print(amplitudes)
                        np.savetxt(file_name, amplitudes, header="# amplitudes")
                        prompt_text = "\""+file_name+"\" written"
                        prompt_mode = False
                    elif prompt_text.strip() == ":set logscale":
                        logscale = not logscale
                        prompt_mode = False
                    elif prompt_text.strip() == ":q":
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
                    draw_hist(np.bincount(amplitudes, minlength=2**8),
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
