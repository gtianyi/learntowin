'''
Created on Sep 2, 2016

@author: lenovo
'''
import unittest
from kmeans import *

class Test(unittest.TestCase):


    def test_new_centroids(self):
        clusters=[[[0,0],[1,1]],[[10,10],[9,9]]]
        point_length=2
        centroids = new_centroids(clusters, point_length)
        self.assertEquals(centroids,[[0.5,0.5],[9.5,9.5]], centroids)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSearch']
    unittest.main()