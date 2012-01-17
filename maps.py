#This file is modified from Silveira Neto's blog post at http://silveiraneto.net/2009/12/19/tiled-tmx-map-loader-for-pygame/ which is GPLv3-licensed
#Accordingly, this file is made available under the GPLv3. See http://www.gnu.org/licenses/gpl.txt
#Copyright Brian Gordon 2010.

import os, sys, pygame, config, item, sprites, game, tileset
from pygame.locals import *
from xml import sax
from tileset import Tileset


class TMXHandler(sax.ContentHandler):
    """Adapted from http://silveiraneto.net/2009/12/19/tiled-tmx-map-loader-for-pygame/"""
    def __init__(self):
        #Inform
        self.tile_width = 0
        self.tile_height = 0
        self.columns = 0
        self.lines  = 0
        self.layers = 0 #How many <layer>s have been processed (will contain total number of layers when the ContentHandler is finished)
        self.properties = [{}] #List of dictionaries (one per layer) of name/value pairs. Specified by <property> tags.
        self.tileset = None #The Tileset object built from <tileset> tags
        self.image = [] #A list of layers, each containing a 2D list of references to Tileset cells
        self.cur_row = []
        self.cur_layer = []
        self.blocking = [] #List of blocking areas which items cannot go into (painted over impassable terrain)
        self.items = [] #List of all items
        self.in_item = False; #whether I'm putting properties into an item or into a layer

    def startElement(self, name, attrs):
        if name == 'map':
            self.columns = int(attrs.get('width', None))
            self.lines  = int(attrs.get('height', None))
            self.tile_width = int(attrs.get('tilewidth', None))
            self.tile_height = int(attrs.get('tileheight', None))
        # create a tileset
        elif name=="image":
            #It's possible to use more than one tileset, but they must have identical tile sizes and identical 
            #transparent color keys.
            source = attrs.get('source', None)
            transp = attrs.get('trans', None)

            if(self.tileset == None):
                self.tileset = Tileset(self.tile_width, self.tile_height)
            
            self.tileset.addSet(source, pygame.Color("0x" + str(transp)))
        # store additional properties.
        elif name == 'property':
            #add to item or layer properties depending on which parent tag we're in
            if self.in_item:
                self.items[-1].properties[attrs.get('name', None)] = attrs.get('value', None)
            else:
                self.properties[self.layers][attrs.get('name', None)] = attrs.get('value', None)
        # starting counting
        elif name == 'layer':
            self.line = 0
            self.column = 0
            self.layers += 1
            self.properties.append({});
            self.in_item = False
        # get information of each tile and put on the map
        elif name == 'tile':
            #tile ID for referencing the tile set
            gid = int(attrs.get('gid', None)) - 1
            if gid <0: gid = 0

            self.cur_row.append(self.tileset.tiles[gid])

            self.column += 1
            if(self.column>=self.columns):
                self.line += 1
                self.column = 0
                self.cur_layer.append(self.cur_row)
                self.cur_row = []

            if(self.line>=self.lines):
                self.image.append(self.cur_layer)
                self.cur_layer = []
        elif name == "object":
            #object areas can be painted in tiled, or specified by hand like in the sample map
            
            self.in_item = True

            x = int(attrs.get('x', None)) / self.tile_width
            y = int(attrs.get('y', None)) / self.tile_height

            if(attrs.get('type', None) == "block"): #blocks items from entering contained squares
                width = int(attrs.get('width', None)) / self.tile_width
                height = int(attrs.get('height', None)) / self.tile_height

                self.blocking.append(Rect(x, y, width, height))

            if(attrs.get('type', None) == "boulder"): #pushable
                self.items.append(item.Item(sprites.Sprite("sprites/rock.png", 32, 64, Color("0x00c6c6")), Rect(x, y, 1, 1), "boulder"))

            if(attrs.get('type', None) == "girl"):
                self.items.append(item.Item(sprites.Sprite("sprites/girl.png", 32, 64, Color("0x00c6c6")), Rect(x, y, 1, 1), "person"))

            if(attrs.get('type', None) == "boy"):
                self.items.append(item.Item(sprites.Sprite("sprites/boy.png", 32, 64, Color("0x00c6c6")), Rect(x, y, 1, 1), "person"))
