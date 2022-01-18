from pytictoc import TicToc
import numpy as np
import matplotlib.image as img
import pyglet
import pyautogui

class PyGLet_APP ():
    def __init__ (self):
        self.display = pyglet.canvas.Display()
        self.screens = self.display.get_screens()
        self.window = pyglet.window.Window(fullscreen=True, screen=self.screens[1])
        self.window.on_draw = self.on_draw
        self.window.on_mouse_press = self.on_mouse_press
        self.image = pyglet.image.load("TestingPattern.bmp")
        self.count = 0
        self.Sprite = pyglet.sprite.Sprite(self.image)
        self.clock = TicToc()
    
    def on_draw (self):
        self.window.clear()
        self.Sprite.draw()
    
    def on_mouse_press (self, x, y, button, modifiers):
        #print(f"({x}, {y}, {button}, {modifiers})")
        #self.clock.tic()
        #
        #self.count = (self.count + 1) % 3
        #imgtmp = np.zeros((2436, 752, 3), dtype=np.uint8)
        #if (self.count == 0):
        #    imgtmp[:, :, 0] = 255
        #    img.imsave("TestingPattern.bmp", imgtmp)
        #    self.image = pyglet.image.load("TestingPattern.bmp")
        #    self.Sprite.image = self.image
        #elif (self.count == 1):
        #    imgtmp[:, :, 1] = 255
        #    img.imsave("TestingPattern.bmp", imgtmp)
        #    self.image = pyglet.image.load("TestingPattern.bmp")
        #    self.Sprite.image = self.image
        #elif (self.count == 2):
        #    imgtmp[:, :, 2] = 255
        #    img.imsave("TestingPattern.bmp", imgtmp)
        #    self.image = pyglet.image.load("TestingPattern.bmp")
        #    self.Sprite.image = self.image
        #
        #self.clock.toc()

        #self.image = pyglet.image.load("TestingPattern.bmp")
        self.image = pyglet.image.load_animation("TestingPattern.gif")
        self.Sprite.image = self.image

        #if ((self.count % 2) == 0):
        #    self.image = pyglet.image.load("TestingPatternAfter.bmp")
        #if ((self.count % 2) == 1):
        #    self.image = pyglet.image.load("TestingPatternBefore.bmp")
        #
        #self.Sprite.image = self.image
        #self.count += 1
    
    def run (self):
        pyglet.app.run()

if (__name__ == "__main__"):
    app = PyGLet_APP()
    app.run()