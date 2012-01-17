# Copyright (c) 2010 Brian Gordon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys, pygame, config, maps, sprites, item
from pygame.locals import *
from xml import sax

game = None

class Game:
    def main(self):
        def draw_layer():
            """This block of code is used twice, the first time to draw each tile of each background 
            layer, and then (after the foreground has been drawn) to draw each tile of each occluding 
            layer. Rather than have duplicate code, I put it in a local function definition and let the many 
            variables fall through. The foreground uses its own code because it deals with multi-frame 
            sprites rather static tiles and it only needs to loop through the list of items."""
            
            #The player's position determines which tiles to draw. Additionally, if the player is still 
            #moving, the trailing row/column one unit behind him should also be drawn.
            for row in range(0 - (y_tile_sliding and player.facing[1] == 1), config.tiles_visible_y + (y_tile_sliding and player.facing[1] == -1)):
                for col in range(0 - (x_tile_sliding and player.facing[0] == 1), config.tiles_visible_x + (x_tile_sliding and player.facing[0] == -1)):
                    #Blit the appropriate area from a given layer of the internal representation of the 
                    #game world onto the screen surface buffer.
                    self.screen.blit(self.tmxhandler.image[layer][row + clamped.top][col + clamped.left],
                    (col * config.tiles_size + (x_tile_sliding * player.sliding  * player.facing[0]), row * config.tiles_size + (y_tile_sliding * player.sliding  * player.facing[1]) - 16))
                    
        pygame.init()
        self.screen = pygame.display.set_mode((config.tiles_visible_x * config.tiles_size, config.tiles_visible_y * config.tiles_size - 16))
        pygame.display.set_caption("py Pokemon demo")
        
        #We use the sax library to parse tile maps, paths, and metadata out of the game world XML files.
        parser = sax.make_parser()
        self.tmxhandler = maps.TMXHandler()
        parser.setContentHandler(self.tmxhandler)
        parser.parse(config.map)
        
        #Special handling for active objects in the game world. All people must have a path property.
        for i in self.tmxhandler.items:
            if(i.type == "person"):
                #Build the path out of the parsed properties list for the map
                i.path = [int(n) for n in i.properties["path"].split(',')]

        #These parameters of regular tilesets are specified in the XML world files, but there are no XML files for 
        #player sprites so they have to be hard coded somewhere.
        player = item.Item(sprites.Sprite("sprites/boy.png", 32, 64, Color("0x00c6c6")), Rect(3, 3, 1, 1), "player")
        #Add the player to the items list so that he collides properly and is painted as part of the foreground.
        self.tmxhandler.items.append(player)

        #Everything works even with an even number of visible rows/columns. The player simply isn't centered on the screen surface.
        mid_x, mid_y = (config.tiles_visible_x - 1) / 2, (config.tiles_visible_y - 1) / 2
        self.map_edges = pygame.Rect(0, 0, self.tmxhandler.columns, self.tmxhandler.lines)

        #Calculate which tiles should be visible around the player. The clamped view makes sure that the camera doesn't 
        #go outside of the world borders.
        viewport = Rect(player.position.left - mid_x, player.position.top - mid_y, config.tiles_visible_x, config.tiles_visible_y)
        clamped = viewport.clamp(self.map_edges)

        #moving represents the direction key pressed down right now
        #If you want to know if the player is moving, player.facing and player.sliding should be 
        #used instead, because the direction key could be released or changed during movement.
        moving = (0, 0)
        player.facing = (0, 1)
        
        #Maps keyboard constants to movement vectors
        moves = {K_UP : (0, -1), K_DOWN : (0, 1), K_LEFT : (-1, 0) , K_RIGHT : (1, 0)}
        
        #Is the frame limiter currently disabled?
        turbo = 0
        
        #These take on values of 0, -1, or 1 depending on whether the tiles are currently sliding in that 
        #direction. This is different from moving because it takes into account the window clamping around the edges.
        x_tile_sliding, y_tile_sliding = 0, 0
        
        #There is a single frame for standing still. While sliding, the item alternates between the standing still 
        #frame and the current walking frame (which gets toggled every step so that the legs alternate)
        animation_cutoffs = (config.tiles_size / 2)

        clk = pygame.time.Clock()
        
        #Are we currently recording?
        recording = False 
        frame = 0
        capture_run = 0
        
        #Main game loop
        while 1:
            self.screen.fill(Color(255,0,255))
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                if event.type == KEYDOWN:
                    if event.key in moves.keys():
                        moving = moves[event.key]
                    if event.key is K_SPACE:
                        turbo = True #Hold space to disable frame limiter
                    if event.key is K_r:
                        recording = True #Hold r to record screen output to lots of PNGs

                elif event.type == KEYUP:
                    #We don't want to stop if the player presses and releases a movement key while actually 
                    #moving in a different direction, so the movement direction is checked against the pressed key.
                    if event.key in moves.keys() and moves[event.key] == moving:
                        moving = (0, 0)
                    if event.key is K_SPACE:
                        turbo = False #Restores frame limiter when space is released
                    if event.key is K_r:
                        recording = False
                        capture_run += 1

            #Note that the player's movement is being handled here rather than below with the rest of the items.
            if player.sliding == 0 and moving != (0,0):
                if(player.move(moving)): #This will return false if the player runs into an obstacle.
                    viewport.move_ip(moving) #Naively move the viewport with the player
                    clamped = viewport.clamp(self.map_edges) #Move the viewport back into the game world if it has just left it.
                    
                    #These calculations determine whether the player should move freely near the borders or be fixed in 
                    #the center of a scrolling background when distant from the borders. Note that, for example, the player 
                    #can be close to the top of the world and able to move freely vertically, but still be fixed in the 
                    #horizontal direction. 
                    x_tile_sliding, y_tile_sliding = 0, 0
                    if viewport.left == clamped.left and viewport.move(-1 * moving[0],0).left == viewport.move(-1 * moving[0],0).clamp(self.map_edges).left:
                        x_tile_sliding = 1
                    if viewport.top == clamped.top and viewport.move(0,-1 * moving[1]).top == viewport.move(0,-1 * moving[1]).clamp(self.map_edges).top:
                        y_tile_sliding = 1

            #Handles movement for all persons every frame by changing direction as necessary to match the path in the XML file.
            for i in self.tmxhandler.items:
                if(i.type == "person"): #Note that boulders are never called to go(), only bump_notify()
                    i.go()

            #First we need to pick out all layers not marked as occluding and draw them in order. This creates the 
            #background which items move on top of.
            occluding = []
            for layer in range(0, self.tmxhandler.layers):
                if "occlude" in self.tmxhandler.properties[layer+1]: #+1 because 0 is the map props
                    occluding.append(layer)
                else:
                    draw_layer() #Lots and lots of free variables fall through here
                    
            #Now draw each item (including the player) depending on whether it is visible in the camera viewport.
            for i in self.tmxhandler.items:
                #An item's sliding is set to tiles_size every time it moves, and decremented by 4 pixels per frame until 
                #it reaches 0, at which point it has reached its new position. Note that player's sliding value isn't 
                #changed until after the occluding layer has been drawn. This is necessary because if the viewport is changed 
                #before the items are drawn, they will jump back 4 pixels at the end of the sliding motion.
                if i is not player and i.sliding > 0:
                    i.sliding -= 4

                #Check if the item is visible within 3 tiles around the viewport and if so draw it. The view must be expanded 
                #by three tiles because of the worst case: while an item is sliding to the right away from the player, the player 
                #moves left. In the future I might add a check that allows inflating only by 2 tiles and a directional inflate 
                #depending on which way the player is moving.
                if clamped.inflate(3,3).contains(i.position):

                    self.screen.blit(i.sprite.facing[i.facing][0 if i.sliding < animation_cutoffs else 1 + i.toggle],
                    ((i.position.left - clamped.left) * config.tiles_size - (i.sliding * i.facing[0]) + (x_tile_sliding * player.sliding * player.facing[0]),
                    (i.position.top - clamped.top - 1) * config.tiles_size - (i.sliding * i.facing[1]) + (y_tile_sliding * player.sliding * player.facing[1]) - 16))

            #Finally, draw each occluding layer that was skipped before. This layer will draw on top of items.
            for layer in occluding:
                draw_layer()

            #And now that the drawing operations are finished, update the player's sliding value.
            if player.sliding > 0:
                player.sliding -= 4

            #Swap display buffers, and wait if it's been less than 1/30 of a second since the last frame.
            pygame.display.update()
            if not turbo:
                clk.tick(30)

            if(recording):
                #Export the screen surface to a png file for making videos. This can use a lot of disk space if you record for more 
                #than a few seconds. PNG compression kills the frame rate, but the file sizes are much more manageable. 
                pygame.image.save(self.screen, "cap/" + "run" + str(capture_run).zfill(2) + "_f" + str(frame).zfill(5) + ".png")
                frame += 1

def run():
    global game
    game = Game()
    game.main()