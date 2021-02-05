from cocos import *
from cocos.layer import *
from cocos.director import *
from cocos.actions import *
from cocos.sprite import *

import Wall
from Resources import *

class Cursor(Sprite):
    def __init__(self, image):
        super(Cursor, self).__init__(image)
        self.position = (windowWidth/2, gameAreaHeight/2)
        self.do(Repeat(Rotate(360,2)))
        self.colr = 1
        self.radius = self.width/2
        window.push_handlers(self)

    def on_mouse_motion (self, x, y, dx, dy):
        x,y = director.get_virtual_coordinates(x,y)
        x = min(x, windowWidth)
        x = max(x, 0)
        y = min(y, gameAreaHeight)
        y = max(y, 0)
        self.position = x,y
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(x, y, dx, dy)
        
    def speedUp(self):
        self.image = cursor_green
        self.colr = 2
        self.do(Repeat(Rotate(360,2)))
        
    def slowDown(self):
        self.image = cursor_blue
        self.colr = 1
        self.do(Repeat(Rotate(360,4)))

    def reverse(self):
        self.image = cursor_blue
        self.colr = 3
        self.do(Repeat(Rotate(-360,2)))

class GameLayer(Layer):
    def __init__(self):
        super(GameLayer, self).__init__()
        self.speed = 500
        self.speedMult = 1
        self.cursor = Cursor(cursor_blue)
        self.walls = [Wall.Wall(4, self.speed, 0),Wall.Wall(4, self.speed, 1),Wall.Wall(4, self.speed, 2),Wall.Wall(4, self.speed, 3)]
        for wall in self.walls:
            wall.addTo(self)
        self.add(self.cursor)
        self.score = Score(self.cursor)
        self.score.do(Repeat(Delay(.1) + CallFunc(self.score.update)))
        window.push_handlers(self)

    def level(self, level):
        if level == 1:
            self.walls[0].activate()
            self.speed = 500
        if level == 2:
            self.walls[2].canActivate = True
        if level == 3:
            self.walls[1].canActivate = True
            self.walls[3].canActivate = True
        if level == 4 or level == 5:
            self.speed += 100
        for wall in self.walls:
            wall.changeSpeed(self.speed*self.speedMult)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == pyglet.window.mouse.RIGHT:
            self.rightMouse()
            return
        self.score.modifier = 2
        self.cursor.speedUp()
        self.speedMult = 1.2
        for wall in self.walls:
            wall.changeSpeed(self.speed*self.speedMult)
        
    def rightMouse(self):
        self.cursor.reverse()
        self.score.modifier = -5
        self.speedMult = 1.2
        for wall in self.walls:
            wall.changeSpeed(-self.speed*self.speedMult)

    def on_mouse_release(self, x, y, buttons, modifiers):
        self.cursor.slowDown()
        self.score.modifier = 1
        self.speedMult = 1
        for wall in self.walls:
            wall.changeSpeed(self.speed)

class Score(text.Label):
    def __init__(self, cursor):
        super(Score, self).__init__("0")
        self.font_name="sans-serif",
        self.font_size=32
        self.position = (25, windowHeight-25)
        self.modifier = 1
        self.value = 0
        self.cursor = cursor
        self.level = 1
        
    def update(self):
        if self.cursor.x >= windowWidth/2 and self.modifier > 0:
            bonus = 2
        else:
            bonus = 1
        # print(self.modifier * self.level * bonus)
        self.value += self.modifier * self.level * bonus
        self.element.text = str(self.value)

class MainScene(scene.Scene):
    def __init__(self):
        super(MainScene, self).__init__()
        self.gameLayer = GameLayer()
        self.add(self.gameLayer)
        self.levelSprite = Sprite(levels[0], position=(windowWidth/2, windowHeight/2))
        self.add(Sprite(top, position=(windowWidth/2, windowHeight-20)), z=2)
        self.add(self.levelSprite, z=1)
        self.add(Sprite(bg, position=(windowWidth/2, windowHeight/2)), z=-1)
        self.add(self.gameLayer.score, z=3)
        self.level = 1
        self.gameLayer.level(self.level)
        self.do((Delay(15)+CallFunc(self.increaseLevel))*4)
        self.do(Repeat(CallFunc(self.update)))

    def update(self):
        for wall in self.gameLayer.walls:
            wall.checkCollision(self.gameLayer.cursor)

    def increaseLevel(self):
        if self.level < 5:
            self.level += 1
        print("LEVEL UP ", self.level)
        self.gameLayer.level(self.level)
        self.gameLayer.score.level = self.level
        self.levelSprite.image = levels[self.level-1]

window = director.init(
   windowWidth,
   windowHeight,
   caption="test")

main = MainScene()
director.run(main)
