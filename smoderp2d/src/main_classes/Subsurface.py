import numpy as np
import math
import sys
import os


from smoderp2d.src.main_classes.General           import Globals as Gl
from smoderp2d.src.main_classes.General           import Size
from smoderp2d.src.main_classes.KinematicDiffuse  import *


import smoderp2d.src.processes.subsurface           as darcy
import smoderp2d.src.io_functions.prt               as prt

class SubArrs:

  def __init__(self, L_sub, Ks, vg_n, vg_l, z, ele):
    self.L_sub =     L_sub
    self.h =         float(0)
    self.H =         ele
    self.z =         z
    self.slope =      float(0)
    self.exfiltration = float(0)
    self.V_runoff =     float(0)
    self.V_runoff_pre = float(0)
    self.V_rest =       float(0)
    self.Ks =           Ks
    self.cum_percolation =   float(0)
    self.percolation  =   float(0)
    self.vg_n =   vg_n
    self.vg_m =   1.0-1.0/vg_n
    self.vg_l =   vg_l


## Documentation for a class.
#  More details.
#
class SubsurfaceC(Diffuse if Gl.diffuse == True else Kinematic, Size):
  def __init__(self,L_sub, Ks, vg_n, vg_l):

    if (Globals.r == None or Globals.r == None):
      exit("Global variables are not assigned")
    super(SubsurfaceC, self).__init__()

    r = Gl.r
    c = Gl.c

    self.arr = np.empty((self.r,self.c), dtype=object)

    for i in range(self.r):
      for j in range(self.c):
        self.arr[i][j] = SubArrs(L_sub, Ks, vg_n, vg_l,mat_dmt[i][j]-L_sub, mat_dmt[i][j])
    #raw_input()

    for i in self.rr:
      for j in self.rc[i]:
        self.arr[i][j].slope = mat_slope[i][j]
        #self.slope_(i,j)
        
        #print mat_slope[i][j], self.arr[i][j].slope
        #raw_input()
    self.Kr    = darcy.relative_unsat_conductivity
    self.darcy = darcy.darcy

  def slope_(self,i,j):
    a = self.arr[i-1][j-1].H
    b = self.arr[i-1][j].H
    c = self.arr[i-1][j+1].H
    d = self.arr[i][j-1].H
    f = self.arr[i][j+1].H
    g = self.arr[i+1][j-1].H
    h = self.arr[i+1][j].H
    k = self.arr[i+1][j+1].H
    dzdx = ((c + 2.0*f + k) - (a + 2.0*d + g))/(8.0 * self.pixel_area)
    dzdy = ((g + 2.0*h + k) - (a + 2.0*b + c))/(8.0 * self.pixel_area)
    nasobek = math.sqrt(pow(dzdx,2) + pow(dzdy,2))
    diffslope = math.atan(nasobek) * math.pi/180
    
    return diffslope

  def fill_slope(self):
    self.update_H()

  def get_exfiltration(self,i,j):

    return self.arr[i][j].exfiltration
  def bilance(self,i,j,infilt,inflow,dt):

    arr = self.arr[i][j]
    bil = infilt + arr.V_rest/self.pixel_area + inflow
    
    #print bil, infilt , arr.V_rest/self.pixel_area , inflow
    percolation  = self.calc_percolation(i,j,bil,dt)
    arr.cum_percolation += percolation
    bil -= percolation
    #print bil,
    arr.percolation = percolation
    arr.h, arr.exfiltration = self.calc_exfiltration(i,j,bil)
    #print arr.h
    #print arr.h, infilt, arr.V_rest/self.pixel_area, inflow
     

  def calc_percolation(self,i,j,bil,dt):

    arr = self.arr[i][j]

    
    if (bil > arr.L_sub):
      S = 1.0
    else:
      S = bil/arr.L_sub

    perc = arr.Ks*self.Kr(S,arr.vg_l,arr.vg_m)*dt
    #jj bacha
    #perc = 0
    if (perc > bil):
      perc = bil
    return perc

  def calc_exfiltration(self,i,j,bil):

    arr = self.arr[i][j]
    if (bil > arr.L_sub):
      #print bil
      exfilt  = bil-arr.L_sub
      bil = arr.L_sub
      #print exfilt
    else:
      exfilt = 0
      
    return bil,exfilt

  def runoff(self,i,j,delta_t,efect_vrst):

    arr = self.arr[i][j]
    #print arr .Ks
    self.q_subsurface = self.darcy(arr,efect_vrst)
    #print arr.h
    arr.V_runoff = delta_t * self.q_subsurface
    arr.V_rest = arr.h * self.pixel_area - delta_t * self.q_subsurface

  def runoff_stream_cell(self,i,j):
    self.arr[i][j].V_runoff = 0.0
    self.arr[i][j].V_rest   = 0.0
    return self.arr[i][j].h

  def curr_to_pre(self):
    for i in self.rr:
      for j in self.rc[i]:
        self.arr[i][j].V_runoff_pre = self.arr[i][j].V_runoff

  def return_str_vals(self,i,j,sep,dt):
    arr = self.arr[i][j]
     #';Sub_Water_level_[m];Sub_Flow_[m3/s];Sub_V_runoff[m3];Sub_V_rest[m3];Percolation[],exfiltration[];'
    line = str(arr.h) + sep + str(arr.V_runoff/dt) + sep + str(arr.V_runoff) + sep + str(arr.V_rest) + sep + str(arr.percolation) + sep + str(arr.exfiltration)
    return line




## Class
#  empty class if no subsurface flow is considered
class SubsurfacePass(object,Size):
  def __init__(self,L_sub, Ks, vg_n, vg_l):
    #jj
    self.n = 0
    self.arr = np.empty((Gl.r,Gl.c), dtype=object)
    self.q_subsurface = None
    #self.arr = np.zeros([0],float)
    prt.message("\tOFF")
  def new_inflows(self):
    pass
  def cell_runoff(self,i,j,sur):
    return 0
  def fill_slope(self):
    pass
  def get_exfiltration(self,i,j):
    return 0.0
  def bilance(self,i,j,infilt,inflow,dt):
    pass
  def runoff(self,i,j,delta_t,efect_vrst):
    pass
  def runoff_stream_cell(self,i,j):
    return 0.0
  def return_str_vals(self,i,j,sep,dt):
    return ''
  def curr_to_pre(self):
    pass



class Subsurface(SubsurfaceC if Gl.subflow == True else SubsurfacePass):
  def __init__(self,L_sub = 0.010, Ks = 0.001, vg_n = 1.5, vg_l =  0.5):
    prt.message("Subsurface:")
    super(Subsurface, self).__init__(L_sub = L_sub, Ks = Ks, vg_n = vg_n, vg_l =  vg_l)

