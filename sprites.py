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

import pygame
from pygame.locals import *

class Sprite:
    def __init__(self, file, tile_width, tile_height, transp):
        image = pygame.image.load(file)
        if not image:
            print "Could not find sprite sheet ", file
            
        #Disable alpha channels so that the old keyed transparency color mechanism works
        image.set_alpha(None)
        image.set_colorkey(transp)

        #A dictionary of lists, indexed by facing direction, each of which contains the 3 frames 
        #associated with that direction. The frames are taken from the given sprite sheet file. 
        #Sprite sheets must be 12 tile_widths wide. Tiles congruent to x (mod 3) are:
        #       x=0: The item standing still
        #       x=1: The first walking frame
        #       x=2: The second walking frame
        
        self.facing = {}

        #south
        self.facing[(0,1)] = []
        self.facing[(0,1)].append(image.subsurface(Rect(0*tile_width, 0, tile_width, tile_height)))
        self.facing[(0,1)].append(image.subsurface(Rect(1*tile_width, 0, tile_width, tile_height)))
        self.facing[(0,1)].append(image.subsurface(Rect(2*tile_width, 0, tile_width, tile_height)))

        #north
        self.facing[(0,-1)] = []
        self.facing[(0,-1)].append(image.subsurface(Rect(3*tile_width, 0, tile_width, tile_height)))
        self.facing[(0,-1)].append(image.subsurface(Rect(4*tile_width, 0, tile_width, tile_height)))
        self.facing[(0,-1)].append(image.subsurface(Rect(5*tile_width, 0, tile_width, tile_height)))

        #east
        self.facing[(1,0)] = []
        self.facing[(1,0)].append(image.subsurface(Rect(6*tile_width, 0, tile_width, tile_height)))
        self.facing[(1,0)].append(image.subsurface(Rect(7*tile_width, 0, tile_width, tile_height)))
        self.facing[(1,0)].append(image.subsurface(Rect(8*tile_width, 0, tile_width, tile_height)))

        #west
        self.facing[(-1,0)] = []
        self.facing[(-1,0)].append(image.subsurface(Rect(9*tile_width, 0, tile_width, tile_height)))
        self.facing[(-1,0)].append(image.subsurface(Rect(10*tile_width, 0, tile_width, tile_height)))
        self.facing[(-1,0)].append(image.subsurface(Rect(11*tile_width, 0, tile_width, tile_height)))

        self.facing[(0,0)] = self.facing[(0,1)]
