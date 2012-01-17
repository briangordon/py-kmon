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

import pygame, game, sprites, config, maps
from pygame.locals import *

class Item:
    #what about standing still
    def __init__(self, sprite, position, type, facing=(0,1), toggle=0):
        self.sprite = sprite #The sprite associated with this item
        self.position = position #A rect used to hold the x,y position (from the upper left corner) of the object
        self.facing = facing #The direction vector of the item
        self.sliding = 0 #The number of pixels away from rest an item is when moving
        self.toggle = toggle #Is the first or the second walking frame being used right now?
        self.type = type #Specially-handled item types are "boulder", "person", "player", "block", "girl", "boy"
        self.properties = {} #Dictionary for storing name/value pairs of information about the item. Currently used properties are "path", .
        self.path = [] #Movement path list with x,y alternating. Example: [2,-1,0,2] will loop through down 2, left 1, right 2.
        self.step = 0 #which index of the path list that the item is currently working on
        self.gone = 0 #number of steps taken already toward path[step]

    def move(self, direction):
        """Move the item one tile in the desired direction given by a direction vector (2-tuple). It will 
        return true if the item is able to move in that direction. It will return false if it runs into an 
        unmovable obstacle, a movable obstacle, or if the item is already moving somewhere."""
        
        #When moved, an item immediately takes on its new coordinates so that collision calculations are always 
        #up to date. However, it also gets a tile_width display offset so that it doesn't appear to have moved at all. 
        #That offset is slowly reduced (4 pixels per frame) until the item is in position. During this time, another item 
        #can move into its old place, but since all items move at the same speed their graphics cannot overlap.
        
        if(direction == (0,0)):
            return True #Can't fail to stand still

        if(self.sliding == 0):
            self.facing = direction
            self.toggle = not self.toggle #Use the other walking frame

            new_x, new_y = self.position.left + direction[0], self.position.top + direction[1]
            
            hit = Rect(new_x, new_y, 1, 1).collidelist([i.position for i in game.game.tmxhandler.items])
            
            #Is the item going to be inside another item if it takes on the new_x and new_y?
            if hit > -1: 
                game.game.tmxhandler.items[hit].bump_notify(self.type, self.facing) #Let it know it's being bumped into
                return False
            #Is the item going to be inside a blocking area (out of bounds, fences, buildings, etc) if it takes on the new_x and new_y?
            elif(not game.game.map_edges.collidepoint(new_x, new_y-1) or Rect(new_x, new_y, 1, 1).collidelist(game.game.tmxhandler.blocking) > -1):
                return False
            else:
                #Looking clear, start the move.
                self.position.move_ip(direction[0], direction[1])
                self.sliding = config.tiles_size
                return True

    def go(self):
        #If the item is doing nothing at this step, immediately proceed to the next path instruction or wrap around.
        #You might want to do that if your desired path doubles back on itself (like "Up 5, Left 0, Down 5" will go up and then down)
        if(self.path[self.step] == 0):
            self.step = ( self.step + 1 ) % len(self.path)
        
        #Get the sign of the current instruction
        unit = (self.path[self.step] > 0) * 2 - 1
        #Get the vector with that sign, with the direction depending on whether step is odd or even
        unit_v = (0, unit) if self.step%2 else (unit, 0)

        if(self.move(unit_v)):
            self.gone += unit
            
            #If the item has finished its current instruction, go to the next step or wrap around.
            if(self.gone == self.path[self.step]):
                self.step = ( self.step + 1 ) % len(self.path)
                self.gone = 0

    def bump_notify(self, type, facing):
        #Move a boulder forward but only if it's being directly pushed by a person or player
        #This means no pushing long stacks of boulders
        if(self.type == "boulder" and (type == "player" or type == "person")):
            self.move(facing)
