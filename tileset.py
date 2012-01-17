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

class Tileset:
    """A tileset is a large raster image divided into rectangles that can be tiled onto the screen to build custom 
    game worlds without having to be an artist capable of new graphics work. This class cuts out each tile from the given 
    tileset file and makes it available in a 2D list (same positions as in the tileset image) of surfaces to be referenced 
    as needed. Tiles are used for decoration and cannot be interacted with."""
    def __init__(self, tile_width, tile_height):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tiles = [] #A flat list containing each tile_size square cut out from the tileset
                
    def addSet(self, file, transp):
    	image = pygame.image.load(file)
        if not image:
            print "Could not find tileset file ", file
            
        image.set_alpha(None)
        image.set_colorkey(transp)
        image.convert()
            
        #Populate tiles from the tileset file
        for row in xrange(image.get_height()/self.tile_height):
            for column in xrange(image.get_width()/self.tile_width):
                self.tiles.append(image.subsurface(Rect(column*self.tile_width, row*self.tile_height, self.tile_width, self.tile_height)))