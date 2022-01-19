from pytictoc import TicToc
import numpy as np
import matplotlib.image as img
import pyglet
import pyautogui

class PyGLet_APP ():
    def __init__ (self):
        #self.display = pyglet.canvas.Display()
        #self.screens = self.display.get_screens()
        #self.window = pyglet.window.Window(fullscreen=True, screen=self.screens[1])
        self.window = pyglet.window.Window(500, 500)
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
        if ((self.count % 2) == 0):
            self.image = pyglet.image.load(r"./../Image/TestingPattern001_500x500.bmp")
        else:
            self.image = pyglet.image.load(r"./../Image/TestingPattern002_500x500.bmp")
        #self.image = pyglet.image.load_animation("TestingPattern.gif")
        self.Sprite.image = self.image
        self.count += 1
    
    def run (self):
        pyglet.app.run()

if (__name__ == "__main__"):
    app = PyGLet_APP()
    app.run()