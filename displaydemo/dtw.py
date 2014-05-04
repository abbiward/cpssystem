import numpy as np
import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()
# from rpy2.robjects.packages import importr
# importr("proxy")

# import 'python-dtw' as pydtw
import inspect

class DTW:
    def __init__(self):
        self.r = robjects.r
        self.r('library("dtw")')
        # self.r('library("proxy")')
        # idx = r.seq(0,6.28,len=100)
        # template = r.cos(idx)
        # query = r.sin(idx)+r('runif(100)/10')
        # alignment=r.dtw(query,template,keep=r('TRUE'))
        # robjects.globalenv["alignment"] =  alignment
        # dist = r('alignment$distance')
        # print(dist)


    def get_alignment(self, query, template):

        
  

        # alignment=self.r.dtw(query,template,keep=self.r('TRUE'),open_end=self.r('TRUE'),  window_size=self.r('2'), window_type=self.r('slantedBandWindow'))
        # alignment=self.r.dtw(query,template,keep=self.r('TRUE'),open_end=self.r('TRUE'), open_begin=self.r('TRUE'))
        alignment=self.r.dtw(query,template,keep=self.r('TRUE'))
        # print "INSPECT:", inspect.getargspec(self.r.dtw.__init__)
        robjects.globalenv["alignment"] =  alignment
        dist = self.r('alignment$distance')
        # print "Cost Matrix"
        # print self.r('alignment$costMatrix')
        # print "Direction Matrix"
        # print self.r('alignment$directionMatrix')
        # print 'steps taken'
        # print self.r('alignment$stepsTaken')
        # print self.r('alignment$index1')
        # print self.r('alignment$index2')
        return dist


def main():
    dtw = DTW()
    query = np.array([[1.,0.,0.],[1.,0.,0.],[1.,0.,0.],[1.,0.,0.]])
    query = query[:,:-1]
    # query = np.array([[0,0,0],[1,0,0],[2,0,0],[3,0,0]])
    template = np.array([[0.,0.,0.],[1.,0.,0.],[2.,0.,0.],[3.,0.,0.]])
    template = template[:,:-1]
    x = dtw.get_alignment(query,template)
    print "dist", x[0]

if __name__ == '__main__':
    main()