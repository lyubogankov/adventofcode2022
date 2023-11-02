# https://pyglet.readthedocs.io/en/latest/programming_guide/quickstart.html
# https://pyglet.readthedocs.io/en/latest/programming_guide/shapes.html

import pyglet

if __name__ == '__main__':
    window = pyglet.window.Window()
    label = pyglet.text.Label(
        'Hello World',
        font_name = 'Times New Roman',
        font_size=36,
        x=window.width//2, y=window.height//2,
        anchor_x='center', anchor_y='center'
    )

    @window.event
    def on_draw():
        window.clear()
        label.draw()

    pyglet.app.run()


"""
OK so it's not running - I don't have OpenGL >2.0.

ON windows - how to check OpenGL version?
    https://www.quora.com/How-do-you-find-out-which-version-of-OpenGL-your-graphics-card-supports
    https://www.realtech-vr.com/home/glview
        Downloaded - my version is 3.1
            Hang on, that should be greater than 2.0??

    https://www.khronos.org/opengl/wiki/Getting_Started#Windows
"""