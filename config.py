tiles_visible_x = 13
tiles_visible_y = 11

#This is included more to avoid magic constants than to provide a way 
#to set custom sizes. This must always match the dimensions given in the 
#map file (which are the real values for the tilesets used). The reason 
#we can't just use those values is that the display has to be initialized 
#to its correct size before we parse the XML because the parser uses 
#image processing calls on the linked tilesets to build the tile list.
tiles_size = 32

#Set this to the map file you want to load. Valid map files included in 
#the demo are "map.tmx" and "map2.tmx"
map = "map2.tmx"