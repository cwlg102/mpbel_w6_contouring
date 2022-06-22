import pydicom
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
dcm = pydicom.dcmread('RTs.dcm')
all_ctr = dcm.ROIContourSequence #ROIContourSequence로 Contour 좌표 불러올 수 있음.

#ContourSequence 0부터 20까지(21개) - 각 slice
#print(all_ctr[0].ContourSequence[0].ContourData)
sdx = 0
ctr_volume = [] #일단은 리스트로
indiv = 150 #내분점으로 해버림 # 좌표끼리 거리마다 weight 주는 방법도 있을것 같으나 어려울듯

while sdx < 21: #len이 안먹혀서
    ctr_coord_1dim = all_ctr[0].ContourSequence[sdx].ContourData #슬라이스 넘기면서 Contour좌표데이터 가져옴
    ctr_color = all_ctr[0].ROIDisplayColor #색깔 불러오기
    coord_arr = np.zeros((indiv*len(ctr_coord_1dim)//3, 3)) #미리 좌표 array 만들어 놓고
    adx = 0
    for idx in range(0, len(ctr_coord_1dim), 3): #1차원적 데이터인 ContourData를 3차원으로(데이터는 3의 배수이므로 다음과같이)
        coord_arr[adx][0], coord_arr[adx][1], coord_arr[adx][2] = \
        float(ctr_coord_1dim[idx]), float(ctr_coord_1dim[idx+1]), float(ctr_coord_1dim[idx+2])
        adx += indiv #ContourData는 3씩 건너고 있으므로 좌표 array에 대해선 1씩 올리게 해줘야
    
    idx = -indiv
    while idx < indiv *len(coord_arr):
        idx += indiv
        try:xiplus, yiplus, ziplus = coord_arr[idx+indiv][0], coord_arr[idx+indiv][1], coord_arr[idx+indiv][2]
        except:break
        xi, yi, zi = coord_arr[idx][0], coord_arr[idx][1], coord_arr[idx][2]
        for jdx in range(1, indiv):
            #내분점 공식
            coord_arr[idx+jdx][0] = float(((indiv-1-jdx)*xi +(jdx+1)*xiplus)/indiv)
            coord_arr[idx+jdx][1] = float(((indiv-1-jdx)*yi +(jdx+1)*yiplus)/indiv)
            coord_arr[idx+jdx][2] = float(((indiv-1-jdx)*zi +(jdx+1)*ziplus)/indiv)

    sdx += 1 #다음 슬라이스로
    ctr_volume.append(coord_arr)

x = []
y = []   
z = []  
for i in ctr_volume[3]:
   x.append(i[0])
   y.append(i[1])

print(all_ctr[0].ROIDisplayColor)
plt.axis((-255, 256, -511, 0))
plt.scatter(x, y, c = 'magenta', s = 1)

plt.imshow()
