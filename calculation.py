

import numpy as np
import topology as tp
import conductors_calc as cc


class ChainNetwork:
    def __init__(self,
                 name="",
                 =1,
                 N=25,
                 =14,
                 topology=tp.Topology(name="AT_System"),
                 ):
        self.name = name
        self.topology = topology
        self.h = h
        self.N = N
        self.m = m
        self.z = np.empty((M, M, N), np.complex128)

    def set_parameter(self):
        c_xy = []
        c_resistance = []
        c_mu_r = []
        c_radius = []
        c_equivalent_radius = []
        for line in self.topology.lines:
            c_xy.append([line.coordinater_x, line.coordinater_y])
            c_resistance.append(line.resistance)
            c_mu_r.append(line.mu_r)
            c_radius.append(line.radius)
            c_equivalent_radius.append(line.equivalent_radius)
        return c_xy, c_resistance, c_mu_r, c_radius, c_equivalent_radius

    def calc_unit_z(self):
        c_xy, c_resistance, c_mu_r, c_radius, c_equivalent_radius = self.set_parameter()
        L = cc.calc_L(c_xy, c_equivalent_radius)


    def calc_unit_yc(self):
        unit_yc = np.empty((self.m, self.m), np.complex128)
        c_xy, c_resistance, c_mu_r, c_radius, c_equivalent_radius = self.set_parameter()


k = 3
chen = ChainNetwork(n=k, h=6)
chen.setY()
print(chen.h, chen.n, chen.topo.name, chen.Y)