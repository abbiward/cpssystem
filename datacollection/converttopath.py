'''
# rundemo.py
# You can change the files that we use for each part by changing the import
# statements
'''
import sys
# sys.path.append("/Users/aaward/Dropbox/IW/displaydemo")
import os
import time

# import configurations as config     # custom configuration parameters

def convert_file(alllines):
    origin = map(float, alllines[0][1:-2].split(', '))
    newwindow = []
    for line in alllines[1:]:
        newpt = map(float, line[1:-2].split(', '))
        newwindow.append([val-oval for (val,oval) in zip(newpt,origin)])
    return newwindow

def main(argv):

    [olddir, newdir] = argv

    for filename in os.listdir(olddir):
        # print filename
        # print olddir + filename
        # print newdir + filename
        f = open(olddir+filename,'r')
        alllines = f.readlines()
        f_out = open(newdir+filename, 'w')
        newlines = convert_file(alllines)
        for item in newlines:
            f_out.write(str(item) + "\n")    

if __name__ == '__main__':
    t1 = time.time()
    if len(sys.argv) != 3:
        print 'python collectsample.py olddir newdir'
    else:
        main(sys.argv[1:])
        print "TOTAL TIME: ", time.time()-t1
