import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from numpy.fft import fft,ifft,fft2,ifft2,ifftshift,fftshift
from scipy.fftpack import ifft2
f=1.5*1E9
from numpy import power
from scipy import interpolate

from numpy import  array
def interp2(x, y, img, xi, yi):
    """
    按照matlab interp2写的加速2d插值
    当矩阵规模很大的时候,numba就快,矩阵规模小,则启动numba有开销
    原图是规整矩阵才能这么做
    """

    # @nb.jit
    def _interpolation(x, y, m, n, mm, nn, zxi, zyi, alpha, beta, img, return_img):
        qsx = int(m / 2)
        qsy = int(n / 2)
        for i in range(mm):  # 行号
            for j in range(nn):
                zsx, zsy = int(zxi[i, j] + qsx), int(zyi[i, j] + qsy)  # 左上的列坐标和行坐标
                zxx, zxy = int(zxi[i, j] + qsx), int(zyi[i, j] + qsy + 1)  # 左下的列坐标和行坐标
                ysx, ysy = int(zxi[i, j] + qsx + 1), int(zyi[i, j] + qsy)  # 右上的列坐标和行坐标
                yxx, yxy = int(zxi[i, j] + qsx + 1), int(zyi[i, j] + qsy + 1)  # 右下的列坐标和行坐标
                fu0v = img[zsy, zsx] + alpha[i, j] * (img[ysy, ysx] - img[zsy, zsx])
                fu0v1 = img[zxy, zxx] + alpha[i, j] * (img[yxy, yxx] - img[zxy, zxx])
                fu0v0 = fu0v + beta[i, j] * (fu0v1 - fu0v)
                return_img[i, j] = fu0v0
        return return_img

    m, n = img.shape  # 原始大矩阵大小
    mm, nn = xi.shape  # 小矩阵大小,mm为行,nn为列
    zxi = np.floor(xi)  # 用[u0]表示不超过S的最大整数
    zyi = np.floor(yi)
    alpha = xi - zxi  # u0-[u0]
    beta = yi - zyi
    return_img = np.zeros((mm, nn))
    return_img = _interpolation(x, y, m, n, mm, nn, zxi, zyi, alpha, beta, img, return_img)
    return return_img


filename='待测近场无干扰_63.txt'

a=np.loadtxt(filename,delimiter=',')


B=np.array(a)
B=np.transpose(a)
#我的数据除以1000
B1=B[0]
B2=B[1]
B3=np.zeros_like(B[1])
Ex=B[3]+B[4]*1j
Ey=B[5]+B[6]*1j
Ez=np.zeros_like(B[1])
Eabs=abs(Ex)+abs(Ey)+abs(Ez)
c=pd.DataFrame(np.transpose(np.array([B1,B2,B3,Ex,Ey,Ez,Eabs])),columns=['x','y','z','Ex','Ey','Ez','Eabs'])
c.x=np.real(c.x)
c.y=np.real(c.y)
c.Eabs=np.real(c.Eabs)
delta_x=set(c.x)
length_of_x=len(delta_x)
delta_y=set(c.y)
length_of_y=len(delta_y)


X_THETA_DIRECTION=(np.linspace(1,length_of_x,length_of_x))
Y_PHI_DIRECTION=(np.linspace(1,length_of_y,length_of_y))

#np.square(abs(Ex))+np.square(abs(Ey))+np.square(abs(Ez))

Planar_Sampling=np.sqrt (np.power(abs(Ex),2)+np.power(abs(Ey),2)+np.power(abs(Ez),2))
Planar_Sampling_RESULT=Planar_Sampling.reshape((length_of_y,length_of_x))
Planar_Sampling_RESULT=np.flipud(Planar_Sampling_RESULT)
Planar_Sampling_RESULT=Planar_Sampling_RESULT /np.max(Planar_Sampling_RESULT)



ax = sns.heatmap(Planar_Sampling_RESULT)


#phi+theta 2-D Matrix——生成phi和theta角度的二维矩阵

delta_theta2=1
delta_phi2=1
theta_range2=np.linspace(-90,90,181)*np.pi/180
phi_range2=np.linspace(0,180,181)*np.pi/180
fft_padding=31
padding=fft_padding
#Calculate Sampling interval in X and Y directions——计算X和Y方向的采样间隔

delta_x = list(delta_x)
delta_x=sorted(delta_x)
number_of_samples_x = len(delta_x)
delta_x = abs(delta_x[1]-delta_x[2])

delta_y = list(delta_y)
delta_y=sorted(delta_y)
number_of_samples_y = len(delta_y)
delta_y = abs(delta_y[1]-delta_y[2])
#% Scanner Plane Dimensions
length_x = delta_x * (number_of_samples_x-1)
length_y = delta_y * (number_of_samples_y-1)

lambda0=299792458/f
k0=2*np.pi/lambda0

number_of_samples_x_padded = padding*number_of_samples_x
number_of_samples_y_padded = padding*number_of_samples_y


m=np.linspace(-1*number_of_samples_x_padded/2,number_of_samples_x_padded/2-1,number_of_samples_x_padded)
n=np.linspace(-1*number_of_samples_y_padded/2,number_of_samples_y_padded/2-1,number_of_samples_y_padded)

kx=2*np.pi*m/(number_of_samples_x_padded*delta_x);
ky=2*np.pi*n/(number_of_samples_y_padded*delta_y);



kx_grid,ky_grid = np.meshgrid(kx,ky);

ky_grid=np.flipud(ky_grid)


ky_grid1=np.flipud(ky_grid)
d=np.power(ky_grid1,2)
c=k0*k0-np.power(kx_grid,2)-np.power(ky_grid1,2)
c=np.array(c,dtype=np.complex)
kz_grid = np.sqrt(c)

# herical Far-Field Wavenumber Vector——球面远场波数向量kx_grid_spherical+ky_grid_spherical+kz_grid_spherical


(theta_grid,phi_grid)=np.meshgrid(theta_range2,phi_range2)

#(theta_grid,phi_grid)=theta_range2,phi_range2
kx_grid_spherical = k0*np.sin(theta_grid)*np.cos(phi_grid)
ky_grid_spherical = k0*np.sin(theta_grid)*np.sin(phi_grid)
kz_grid_spherical = k0*np.cos(theta_grid)


#Reshape E field to fit grid——变换得到远场Ax,Ay,Az分量

Ex_nf = Ex.reshape(number_of_samples_y,number_of_samples_x).transpose()
Ey_nf = Ey.reshape(number_of_samples_y,number_of_samples_x).transpose()
Ez_nf = Ez.reshape(number_of_samples_y,number_of_samples_x).transpose()

number_of_samples_x2=number_of_samples_x
number_of_samples_y2=number_of_samples_y

Ex_nf=Ex_nf.transpose()
Ey_nf=Ey_nf.transpose()
Ez_nf=Ez_nf.transpose()

Ex_nf=np.flipud(Ex_nf)
Ex_nf_Interpolation=Ex_nf

Ey_nf=np.flipud(Ey_nf)
Ey_nf_Interpolation=Ey_nf

Ez_nf=np.flipud(Ez_nf)
Ez_nf_Interpolation=Ez_nf
#% 对29*12的平面时域信号Ex_nf和Ey_nf进行补零，形成841*348的矩阵

fx=(ifft2(Ex_nf,(number_of_samples_y_padded,number_of_samples_x_padded)))
fy=(ifft2(Ey_nf,(number_of_samples_y_padded,number_of_samples_x_padded)))
ky_grid=np.flipud(ky_grid)
fz=-(fx*kx_grid+fy*ky_grid)/kz_grid



fx=ifftshift(fx)
fy=ifftshift(fy)

fz1=ifftshift(fz)


fz2=-(fx*kx_grid+fy*ky_grid)/kz_grid
fz=fz1*0.65+fz2*0.35

#;%采样平面距离天线口面的距离为5*lambda
r=5*lambda0

print("here")


fx=fx*np.exp(1j*kz_grid*r)/(4*np.pi*np.pi)
fy=fy*np.exp(1j*kz_grid*r)/(4*np.pi*np.pi)
fz=fz*np.exp(1j*kz_grid*r)/(4*np.pi*np.pi)

