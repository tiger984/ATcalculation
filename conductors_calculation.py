
# coding: utf-8

# In[6]:


import numpy as np
from scipy import linalg
from scipy import constants as C
from scipy import special

#导线定义

"""
1. 接触线（CW1）; 2.承力索（MW1）; 3.正馈线（PF1）; 4.钢轨1（RA1）;5.钢轨2（RA2）;6.保护线（PW1）;7.综合地线（E1）
8. 接触线（CW2）; 9.承力索（MW2）; 10.正馈线（PF2）; 11.钢轨3（RA3）;12.钢轨4（RA4）;13.保护线（PW2）;14.综合地线（E2）

"""
conductors_coordinater = 0.001*np.array([[0,6300],[0,7500],[-4400,8500],[-755,1000],[755,1000],[-3600,8000],[-4400,500],
                                 [5000,6300],[5000,7500],[4400+5000,8500],[4245,1000],[5755,1000],[3600+5000,8000],
                                 [4400+5000,500]],np.float64)  # 多导体坐标数组 (x,y),单位 m

conductors_calc_radius = 0.001*np.array([5.9,7.00,9.5,109.1,109.1,7.60,5.35,5.9,7.00,9.5,109.1,109.1,7.60,5.35])
                                    #多导体计算半径，单位 m， 计算电位系数用

conductors_equivalent_radius = 0.001*np.array([4.2,5.31,9.03,12.79,12.79,7.22,4.055,4.2,5.31,9.03,12.79,12.79,7.22,4.055])
                                    #多导体等效半径,单位m, 自电感简化计算参数

Rd = np.array([0.146,0.158,0.163,0.135,0.135,0.255,0.28,0.146,0.158,0.163,0.135,0.135,0.255,0.28])
                                    #多导体直流电阻，单位 欧/km
    
mu_r = np.array([1,1,1,40,40,1,1,1,1,1,40,40,1,1]) #导线相对磁导率
rho = np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1])*0.01777*10**-6  #导线材料电阻率

conductors_coordinater,conductors_calc_radius,conductors_equivalent_radius,Rd, mu_r, rho

def calc_potential_coefficient(c_xy,r):
    """ 计算电位系数矩阵P
    """
   
    n=np.shape(c_xy)[0]
    P=np.empty((n,n),np.float64)
    for i in range(n):  
        for j in range(n):
            if i==j:
                P[i,i]=18*10**+6*np.log(2*c_xy[i,1]/r[i])
            else:
                Dij=np.sqrt((c_xy[i,0]-c_xy[j,0])**2+(c_xy[i,1]+c_xy[j,1])**2)
                dij=np.sqrt((c_xy[i,0]-c_xy[j,0])**2+(c_xy[i,1]-c_xy[j,1])**2)
                P[i,j]=18*10**+6*np.log(Dij/dij)
    return P

def merge_potential_coefficient(P,m,k):
    n=np.shape(P)[0]
    for i in range(n):
        P[i,k]=P[i,k]-P[i,m]
         
    for i in range(n):
        for j in range(n):
            if i!=k and j!=k:
                P[i,j]=P[i,j]-P[i,k]/(P[k,k]-P[m,k])*(P[k,j]-P[m,j])
                        
          
    E=np.empty((n-1,n-1),np.float64)
    for i in range(n):
        for j in range(n):

            if i<k:
                if j<k:
                    E[i,j]=P[i,j]
                if j>k:
                    E[i,j-1]=P[i,j]
            if i>k:
                if j<k:
                    E[i-1,j]=P[i,j]
                if j>k:
                    E[i-1,j-1]=P[i,j]
    
    return E

#测试
P=calc_potential_coefficient(conductors_coordinater,conductors_calc_radius)
P=merge_potential_coefficient(P,0,1) 
P=merge_potential_coefficient(P,2,3)
P=merge_potential_coefficient(P,2,3)
P=merge_potential_coefficient(P,2,3)
P=merge_potential_coefficient(P,3,4)
P=merge_potential_coefficient(P,5,6)
P=merge_potential_coefficient(P,5,6)
P=merge_potential_coefficient(P,5,6)
np.set_printoptions(precision=3,linewidth=214,suppress=True)
print('P矩阵 e+7 : \n {}'.format(P*10**-7))

def calc_B(P):
    """ 计算电容系数矩阵"""
    
    B=linalg.inv(P)
    return B



B=calc_B(P)
np.set_printoptions(precision=3,linewidth=214,suppress=True)              
          
print('B矩阵(×e-9) : \n {}'.format(B*10**9))

def calc_L(c_xy,r):
    n=np.shape(c_xy)[0]
    L=np.empty((n,n),np.float64)
    for i in range(n):           #计算导线外自感和互电感
        for j in range(n):
            if i==j:
                L[i,i]=2*10**-4*np.log(2*c_xy[i,1]/r[i])
            else:
                Dij=np.sqrt((c_xy[i,0]-c_xy[j,0])**2+(c_xy[i,1]+c_xy[j,1])**2) 
                dij=np.sqrt((c_xy[i,0]-c_xy[j,0])**2+(c_xy[i,1]-c_xy[j,1])**2)
                L[i,j]=2*10**-4*np.log(Dij/dij) 
    return L

# 函数测试
f=50
c_xy=conductors_coordinater
r= conductors_calc_radius
L=calc_L(c_xy,r)
np.set_printoptions(precision=4,linewidth=214,suppress=True) 

print('L矩阵(×e-3) : \n {}'.format(L*10**3))


def calc_Zc1(f,Rd,r,mu_r,rho):
    
    n = np.shape(Rd)[0]
    Zc = np.empty((n),np.complex128)
    for i in range(n):
        m = np.sqrt(2*np.pi*f*mu_r[i]*4*np.pi*10**-7/rho[i])
        mr = m*r[i]
    #    print(mr)
        a = special.ber(mr)+1j*special.bei(mr)
        b = special.berp(mr)+1j*special.beip(mr)
        c = 1j*a/b
    #    print('a=',a)
    #    print('b=',b)
    #    print('c=',c)      
       
        alphaR = (mr/2)*np.real(c)
        alphaL = (4/mr)*np.imag(c)
    #    print('alphaL = ',alphaL)
        Rc = Rd[i]*alphaR;
        Xc = np.pi*f*10**-4*mu_r[i]*alphaL
        Zc[i] = Rc+1j*Xc
        print(Zc[i])
        
    return Zc



def calc_Zc(f,Rd,r,mu_r,rho):
    
    n = np.shape(Rd)[0]
    Zc = np.empty((n),np.complex128)
    
    for i in range(n):
        m = np.sqrt(2*np.pi*f*mu_r[i]*4*np.pi*10**-7/rho[i])
        mr = m*r[i]
   #     print(mr)
        A = special.ber(mr)*special.beip(mr)-special.bei(mr)*special.berp(mr)
        B = special.bei(mr)*special.beip(mr)+special.ber(mr)*special.berp(mr)
        C = special.berp(mr)**2+special.beip(mr)**2
       # print('B/C=',B/C,'A/C=',A/C)
       # print('A/C=',A/C)
        
        alphaR = (mr/2)*(A/C)
        alphaL = (4/mr)*(B/C)
   #     print('alphaL = ',alphaL)
        Rc = Rd[i]*alphaR
        Xc = np.pi*f*10**-4*mu_r[i]*alphaL
        Zc[i] = Rc+1j*Xc
        print(Zc[i])
        
    return Zc



#测试
##dd = np.empty((5),np.float64)
# print(dd)
f = 5000
re = conductors_calc_radius
#np.set_printoptions(precision=8,linewidth=120,suppress=True)
print('Zc=')
Zc = calc_Zc(f,Rd,re,mu_r,rho)

#print('Zc矩阵 : \n {}'.format(Zc))
print('Zc1=')
Zc1 = calc_Zc1(f,Rd,re,mu_r,rho)
#print('Zc1矩阵 : \n {}'.format(Zc1))
#print(Zc1)

def calc_Zgm(f,c_xy,rou):
    n=np.shape(c_xy)[0]
    Rgm=np.empty((n,n),np.float64)
    Xgm=np.empty((n,n),np.float64)
    for i in range(n):          
        for j in range(n):
            Dij=np.sqrt((c_xy[i,0]-c_xy[j,0])**2+(c_xy[i,1]+c_xy[j,1])**2)
            xij=np.abs(c_xy[i,0]-c_xy[j,0])
            theta=np.arcsin(xij/Dij)
            k=4*np.pi*np.sqrt(5)*10**-4*Dij*np.sqrt(f/rou) 
            Rgm[i,j]=calc_Rg(f,k,theta)
            Xgm[i,j]=calc_Xg(f,k,theta)
                
    return Rgm + 1j*Xgm



def calc_Rg(f,k,theta):
       
    b1=np.sqrt(2)/6
    b2=1/16
    b3=b1/(3*5)
    b4=b2/(4*6)
    b5=-b3/(5*7)
    b6=-b4/(6*8)
    b7=-b5/(7*9)
    b8=-b6/(8*10)
    
    c2=1.3659315
    c4=c2+1/4+1/6
    c6=c4+1/6+1/8
    
    d4=np.pi/4*b4
    d6=np.pi/4*b6
    d8=np.pi/4*b8
    
    if k<5.1:
        Rg=np.pi/8
        -b1*k*np.cos(theta)
        +b1*k*np.cos(theta)
        +b2*((c2-np.log(k))*k**2*np.cos(2*theta)+theta*k**2*np.sin(2*theta))
        +b3*k**3*np.cos(3*theta)
        -d4*k**4*np.cos(4*theta)
        -b5*k**5*np.cos(5*theta)
        +b6*((c6-np.log(k))*k**2*np.cos(6*theta)+theta*k**6*np.sin(6*theta))
        +b7*np.cos(7*theta)
        -d8*k**8*np.cos(8*theta)
    else:
        Rg=np.cos(theta)/k
        -np.sqrt(2)*np.cos(2*theta)/k**2
        +np.cos(3*theta)/k**3
        +3*np.cos(5*theta)/k**5
        -45*np.cos(7*theta)
        Rg=Rg/sqrt(2)
      
    Rg=4*2*np.pi*f*10**-4*Rg
    return Rg
    
def calc_Xg(f,k,theta):
                
    b1=np.sqrt(2)/6
    b2=1/16
    b3=b1/(3*5)
    b4=b2/(4*6)
    b5=-b3/(5*7)
    b6=-b4/(6*8)  
    b7=-b5/(7*9)
    b8=-b6/(8*10)
    
    c2=1.3659315
    c4=c2+1/4+1/6
    c6=c4+1/6+1/8
    c8=c4+1/8+1/10
    
    d2=np.pi/4*b2
    d4=np.pi/4*b4
    d6=np.pi/4*b6
    d8=np.pi/4*b8
    
    if k<5.1:
        Xg=0.5*(0.6159315-np.log(k))
        +b1*k*np.cos(theta)
        -d2*k*k*np.cos(2*theta)
        +b3*k**3*np.cos(3*theta)
        -b4*((c4-np.log(k))*k**4*np.cos(4*theta)+theta*k**4*rou=10**6np.sin(4*theta))
        +b5*k**5*np.cos(5*theta)
        -d6*k**6*np.cos(6*theta)
        +b7*k**7*np.cos(7*theta)
        -b8*((c8-np.log(k))*k**8*np.cos(8*theta)+theta*k**8*np.sin(8*theta))
    else:
        Xg=np.cos(theta)/k
        -np.cos(3*theta)/k**3
        +3*np.cos(5*theta)-45*np.cos(7*theta)
        Xg=Xg/sqrt(2)
    
    Xg=4*2*np.pi*f*10**-4*Xg
    return Xg

# 测试
f=50
rou=10**6
c_xy=conductors_coordinater
Zgm=calc_Zgm(f,c_xy,rou)
np.set_printoptions(precision=4,linewidth=214,suppress=True)
print('Zgm 矩阵 : \n {}'.format(Zgm))



f=2000
rou=10**6
c_xy=conductors_coordinater
n=np.shape(c_xy)[0]
for i in range(n):           #计算导线与大地回路电阻和电感rou=10**6
        for j in range(n):
            Dij=np.sqrt((c_xy[i,0]-c_xy[j,0])**2+(c_xy[i,1]+c_xy[j,1])**2)
            xij=np.abs(c_xy[i,0]-c_xy[j,0])
            theta=np.arcsin(xij/Dij)
            k=4*np.pi*np.sqrt(5)*10**-4*Dij*np.sqrt(f/rou)
           # print(k)
            
            
 
            
            

def calc_Zf(f,c_xy,r,Rd,rho,mu_r,rou):
    Zgm = calc_Zgm(f,c_xy,rou)  #计算线路大地回路阻抗
    L = calc_L(c_xy,r)          # 计算线路自感与外感
    Zc = calc_Zc(f,Rd,r,mu_r,rho)      # 计算线路内阻抗
    Zf = Zgm +1j*2*np.pi*f*L
    n = np.shape(c_xy)[0]
    for i in range(n):
        Zf[i,i] = Zf[i,i] + Zc[i]
    return Zf
    
  #测试
f = 50
rou=10**6
r = conductors_calc_radius
c_xy = conductors_coordinater
Zf = calc_Zf(f,c_xy,r,Rd,rho,mu_r,rou)
print('Zf = ',Zf)

def calc_z(f,c_xy,re,Rd,rou):
    n = np.shape(c_xy)[0]
    R = np.empty((n,n),np.float64)
    X = np.empty((n,n),np.float64)
    z = np.empty((n,n),np.complex128)
    Rg = np.pi**2*f*10**-4
    Dg = 660*np.sqrt(rou/f)
    for i in range(n):           #
        for j in range(n):
            if i==j:
                R[i,j] = Rg+Rd[i]
                X[i,j] = 2*2*np.pi*f*10**-4*np.log(Dg/re[i])
            else:
                dij = np.sqrt((c_xy[i,0]-c_xy[j,0])**2+(c_xy[i,1]-c_xy[j,1])**2)
                R[i,j] = Rg
                X[i,j] = 2*2*np.pi*f*10**-4*np.log(Dg/dij)
    z = R+1j*X        
    return R,X,z
# 测试该函数
f = 50
c_xy = conductors_coordinater
re = conductors_equivalent_radius

rou=10**6
R,X,z=calc_z(f,c_xy,re,Rd,rou)
np.set_printoptions(precision=4,linewidth=214,suppress=True)
# print('R 矩阵 : \n {}'.format(R))
# print('X 矩阵 : \n {}'.format(X))
print('z 矩阵 : \n {}'.format(z))

def merge_z(z,m,k):
    
    n=np.shape(z)[0]
    for i in range(n):
        z[i,k]=z[i,k]-z[i,m]
         
    for i in range(n):
        for j in range(n):
            if i!=k and j!=k:
                z[i,j]=z[i,j]-z[i,k]/(z[k,k]-z[m,k])*(z[k,j]-z[m,j])
                               
            
    E=np.empty((n-1,n-1),np.complex128)
    for i in range(n):
        for j in range(n):
            if i<k:
                if j<k:
                    E[i,j]=z[i,j]
                if j>k:
                    E[i,j-1]=z[i,j]
            if i>k:
                if j<k:
                    E[i-1,j]=z[i,j] 
                if j>k:
                    E[i-1,j-1]=z[i,j]
    
    return E

# 测试
f=50
c_xy=conductors_coordinater
re=conductors_equivalent_radius

rou=10**6
R,X,z=calc_z(f,c_xy,re,Rd,rou)
np.set_printoptions(precision=3,linewidth=214,suppress=True) 
print('阻抗矩阵z （Ω/km）: \n {}'.format(z))
z=merge_z(z,0,1) 
z=merge_z(z,2,3)
z=merge_z(z,2,3)
z=merge_z(z,2,3)
z=merge_z(z,3,4)
z=merge_z(z,5,6)
z=merge_z(z,5,6)
z=merge_z(z,5,6)
Z=np.abs(z) 

np.set_printoptions(precision=4,linewidth=214,suppress=True)              
print('阻抗矩阵z （Ω/km）: \n {}'.format(z))
print('阻抗矩阵Z （Ω/km）: \n {}'.format(Z))

