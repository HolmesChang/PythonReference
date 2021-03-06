import pyglet
from pyglet.window import mouse

# ================================================== #
#   Displaying Static Image
# ================================================== #
#fpath = r"HorizontalWhiteGLGradientL2R_720x1280.bmp"
#image = pyglet.resource.image(fpath)

# ================================================== #
#   Displaying Dynamic Image
# ================================================== #
fpath = r"WhiteGL000ToGL255_2436x752.gif"
fpath2 = r"SPR_RedGL000ToGL255_2436x752.gif"
animation = pyglet.image.load_animation(fpath)
animation2 = pyglet.image.load_animation(fpath2)
animSprite = pyglet.sprite.Sprite(animation)
w = animSprite.width
h = animSprite.height

count = 0

display = pyglet.canvas.Display()
screens = display.get_screens()

window = pyglet.window.Window(fullscreen=True, screen=screens[1])

#(r, g, b, alpha) = (0.5, 0.5, 0.8, 0.5)
#pyglet.gl.glClearColor(r,g,b,alpha)

@window.event
def on_draw ():
    window.clear()
    # ================================================== #
    #   Displaying Static Image
    # ================================================== #
    #image.blit(0, 0)

    # ================================================== #
    #   Displaying Dynamic Image
    # ================================================== #
    animSprite.draw()

@window.event
def on_mouse_press (x, y, button, modifiers):
    global count

    print(f"({x}, {y}, {button}, {modifiers})")
    
    if ((count % 2) == 0):
        animSprite.image = animation2
    else:
        animSprite.image = animation
    
    #window.clear()
    #animSprite.draw()

    count += 1

pyglet.app.run()