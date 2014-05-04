# Original code: http://www.daniweb.com/software-development/python/threads/140384/pygame-cursor
import pygame as pg
import time

import sys
sys.path.append("/Users/aaward/Dropbox/IW")
import configurations as config

class CursorDemo:
    def __init__(self):       
        # bgcolor = 255, 255, 255  # white
        # bgcolor = 155, 155, 255  # purplish
        # bgcolor = 89, 255, 186  # blue/green/aquaish? 
        # bgcolor = 117, 255, 197  # blue/green/aquaish? 
        #bgcolor = 142, 255, 208 # blue/green/aquaish? 
        bgcolor = 184, 65, 18

        # possible_screens = [(800,400), (1440,900), (1920,1080)]
        (self.screen_width, self.screen_height) = config.screen_size

        # self.screen_width = 400 #400 #1920 #1440 #400 #1440
        # self.screen_height = 400 #400 #1080 #900 #400 #990
        #screen = pg.display.set_mode((self.screen_width, self.screen_height),pg.FULLSCREEN,0)
        screen = pg.display.set_mode((self.screen_width, self.screen_height))
        screen.fill(bgcolor)

        self.cursor_parameters = []
        self.square_size = 512
        for i in range(2,self.square_size-1):
            mycursor = self.make_square_cursor(self.square_size,i)
            self.cursor_parameters.append(mycursor)

        print len(self.cursor_parameters)

        self.z_pos_limit = config.z_pos_limit # .08

        # set the mouse cursor
        pg.mouse.set_cursor(*pg.cursors.diamond)

        pg.display.flip()

    
    def make_square_cursor(self, size_bmp, size_square):
        # size_bmp: one side size of bitmap: must be multiple of 8
        # 3 types of rows: empty, top/bottom edge, side edge 
        # ctr = size_bmp/2
        vals_per_row = size_bmp/8
        # location is going to be size_square away from ctr
        row_top_edge = 1 # ctr-size_square
        row_bottom_edge = size_square # ctr+size_square
        index_left_edge = 1 # ctr-size_square
        index_right_edge = size_square # ctr+size_square

        # initialize data
        data = [0]*(size_bmp*vals_per_row)
      
        # get row indicies 
        # row_top_edge_ind = vals_per_row*row_top_edge
        num_vals_255 = size_square/8
        num_bits_remaining = size_square % 8 

        # set top and bottom rows 
        bit_values = [0,128,192,224,240,248,252,254,255]
        hor_edge = [255]*num_vals_255 + [bit_values[num_bits_remaining]] + [0]*(abs(vals_per_row-num_vals_255-1))
        hor_edge = hor_edge[:vals_per_row+1]
        data[0:vals_per_row] = hor_edge
        row_bottom_edge_ind = vals_per_row*row_bottom_edge
        data[row_bottom_edge_ind:row_bottom_edge_ind+vals_per_row] = hor_edge
        
        # set edges
        bit_values_vert = [1,2,4,8,16,32,64,128]
        bit_values_vert.reverse()
        vert_edge_row = [0]*vals_per_row
        vert_edge_row[0] = 128
        index_right_edge = size_square/8
        if (index_right_edge == 0):
            vert_edge_row[0] = 128+bit_values_vert[size_square % 8] 
            if (vert_edge_row[0] > 255):
                vert_edge_row[0] = 128
        else:
            vert_edge_row[index_right_edge] = bit_values_vert[size_square % 8]
        
        for i in range(vals_per_row,(size_square)*vals_per_row,vals_per_row):
            data[i:i+vals_per_row] = vert_edge_row

        # initialize mask
        mask = [0]*len(data)
        data_first_row = data[0:vals_per_row]
        for i in range(0,size_square*vals_per_row,vals_per_row):
            mask[i:i+vals_per_row] = data_first_row
        # mask = data

        # flip white/black
        # data,mask = mask,data

        return ((size_bmp,size_bmp),(8,1),data,mask)



    def bound_readings(self,to_bound,bounding_limits):
        # to_bound is list of values to bound
        # bounding_limits is 2d list of bounding_limits
        #   each entry is a list of length 2: [lower_limit, upper_limit]
        bounded = [0]*len(to_bound)
        # print "bound_readings:  ", to_bound, bounding_limits
        for i in range(len(to_bound)):
            if (to_bound[i] < bounding_limits[i][0]):
                # print "sm"
                bounded[i] = bounding_limits[i][0]
            elif (to_bound[i] > bounding_limits[i][1]):
                # print "lg"
                bounded[i] = bounding_limits[i][1]
            else:
                bounded[i] = to_bound[i]
        return bounded


    # def bound_readings(self, pos, screen_width, screen_height):
    #     x = pos[0]
    #     y = pos[1]
    #     if (pos[0] < 0):
    #         x = 0
    #     elif (pos[0] >= screen_width):
    #         x = screen_width
    #     if (pos[1] < 0):
    #         y = 0
    #     elif (pos[1] >= screen_height):
    #         y = screen_height
    #     return (x,y)


    def scale_readings(self,pos, screen_width, screen_height):
        if (pos[0] == -1) or (pos[1] == -1):
            return (-1,-1)

        pos[0] = int(pos[0]*screen_width)
        pos[1] = int(pos[1]*screen_height)
        # bound them appropariately to the screen
        (hor_position,vert_position) = self.bound_readings(pos, [[0,screen_width], [0,screen_height]])
        return (hor_position, vert_position)

    def set_new_cursor_position(self, newpos):
        oldpos = pg.mouse.get_pos()
        if (newpos[0] - oldpos[0]) == 0:
            pg.mouse.set_pos(newpos)
            return
        slope = 1.*(newpos[1] - oldpos[1])/(newpos[0] - oldpos[0])
        steps = 5

        dx = slope/steps
        dy = slope/steps

        print "cursordemo.py: trying to set", oldpos, newpos

        currpos = oldpos
        for i in range(0,steps):
            currpos = (int(currpos[0]+dx), int(currpos[1]+dy))
            pg.mouse.set_pos(currpos)
            # time.sleep(.003)


    def update_display(self,xyposition,zpos,message=None):
        #xyposition: (x,y) pixel position from top left corner
        #zpos is some value between 0 and 1 where 1 is very close to the display
        #   and 0 is max distance

        print xyposition
        # take normalized stuff and put it in dimensions you want
        newxy = xyposition
        oldposition = pg.mouse.get_pos()
        # print "oldpos: ", oldposition
        if (-1 == xyposition[0]):
            newxy[0] = 1.*oldposition[0]/self.screen_width
            # print "cursordemo.py: no x position detected; ", newxy[0]
        if (-1 == xyposition[1]):
            newxy[1] = 1.*oldposition[1]/self.screen_height
            # print "cursordemo.py: no y position detected; ", newxy[1]

        xypos_final = self.scale_readings(newxy, self.screen_width, self.screen_height)
        pg.mouse.set_pos(xypos_final)
        print "cursordemo.py:final pos:", xypos_final
            #self.set_new_cursor_position(xypos_final)
        # size = zpos/10000
        # print "size: ", zpos,
        size = int(zpos*len(self.cursor_parameters))
        # print size,
        size = self.bound_readings([size],[[0,len(self.cursor_parameters)-1]])[0]

        if (zpos < self.z_pos_limit):
            size = 0
        elif (zpos > 2):
            return
        # print size
        # size = zpos



        pg.mouse.set_cursor(*self.cursor_parameters[size])
        


def main():
    CD = CursorDemo()
    num_parameters = CD.square_size-3
    cursor_positions = [[.2,.1], [.4,.2], [.6,.5]]

    # set up the event loop ...
    currsize = 0
    currpos = 0
    start_time = time.clock()
    while time.clock() < start_time + 5:
        event = pg.event.poll()
        CD.update_display(cursor_positions[currpos],currsize)

        # update/reset counters
        currsize = currsize+1
        if currsize >= num_parameters:
    	    currsize = 0 
            currpos = currpos + 1
            if currpos >= len(cursor_positions):
                 currpos = 0
        #pg.display.flip()
        #time.sleep(.1)

        # quit on mouse click
        if event.type == pg.MOUSEBUTTONDOWN:
            break

if __name__ == '__main__':
    main()
