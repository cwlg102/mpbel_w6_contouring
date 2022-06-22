import pydicom
import numpy as np
import matplotlib.pyplot as plt

dcm = pydicom.dcmread('RTs.dcm')
all_ctr = dcm.ROIContourSequence #ROIContourSequence로 Contour 좌표 불러올 수 있음.

sdx = 0
ctr_volume = [] #일단은 리스트로

#내분점 #좌표끼리 거리마다 weight 주는 방법
while sdx < 21: #len이 안먹혀서
    ctr_coord_1dim = all_ctr[0].ContourSequence[sdx].ContourData #슬라이스 넘기면서 Contour좌표데이터 가져옴
    #ctr_color = all_ctr[0].ROIDisplayColor #색깔 불러오기
    coord_arr = np.zeros((1, 3)) #미리 좌표 array 만들어 놓고
    adx = 0
    for idx in range(0, len(ctr_coord_1dim), 3): #1차원적 데이터인 ContourData를 3차원으로(데이터는 3의 배수이므로 다음과같이)
        coord_arr = np.append(coord_arr, 
        [[float(ctr_coord_1dim[idx]), float(ctr_coord_1dim[idx+1]), float(ctr_coord_1dim[idx+2])]],
        axis = 0)

        xi, yi, zi = float(ctr_coord_1dim[idx]), float(ctr_coord_1dim[idx+1]), float(ctr_coord_1dim[idx+2])
        try:xiplus, yiplus, ziplus = float(ctr_coord_1dim[idx+3]), float(ctr_coord_1dim[idx+4]), float(ctr_coord_1dim[idx+5])
        except: xiplus, yiplus, ziplus = float(ctr_coord_1dim[0]), float(ctr_coord_1dim[1]), float(ctr_coord_1dim[2])
        #####예외, xi, yi, zi가 마지막 일경우, 그냥 pass하면 안되고 첫번째 점과 연결을 시켜주어야함.#####

        #largediff = max([abs(xi-xiplus), abs(yi-yiplus), abs(zi-ziplus)])
        largedist = ((xi - xiplus)**2 + (yi - yiplus)**2 + (zi - ziplus)**2) ** 0.5
        if largedist < 1: #만약 길이 차이가 적게나서 1보다 작을 때 largedist를 기본 내분 갯수에 곱하면 내분 갯수가 기본보다 작아짐.
            largedist = 1
        indiv = int(20 * largedist) #distance에 따라 weight 가 달라짐
        
        for jdx in range(1, indiv):
            #내분점 공식
            coord_arr = np.append(coord_arr, 
            [[float(((indiv-1-jdx)*xi +(jdx+1)*xiplus)/indiv), 
            float(((indiv-1-jdx)*yi +(jdx+1)*yiplus)/indiv), 
            float(((indiv-1-jdx)*zi +(jdx+1)*ziplus)/indiv)]],
            axis = 0)
            
        adx += 1

    sdx += 1 #다음 슬라이스로
    ctr_volume.append(coord_arr)

x = []
y = []   
z = []  
print('1 : 3D로, 0 : 2D로: ', end ='')
button = int(input())
if button == 1:
    iwant3d = 1
else:iwant3d = 0


if iwant3d == 0:
    ctrx = []
    ctry = []
    
    for k in range(len(ctr_volume)):
        x = []
        y = []
        for _slice in ctr_volume[k]:
            if _slice[0] == 0 and _slice[1] == 0:
                continue
            x.append(_slice[0])
            y.append(_slice[1])
        ctrx.append(x)
        ctry.append(y)
    
    for _slice in range(len(ctrx)):
        plt.figure()
        plt.axis((-255, 256, -511, 0))
        plt.scatter(ctrx[_slice], ctry[_slice], s = 1)
    plt.show()

elif iwant3d == 1:
    fig = plt.figure(figsize = (6, 6))
    ax = fig.add_subplot(projection = '3d')
    for k in range(len(ctr_volume)):
        for i in ctr_volume[k]:
            if i[0] == 0 and i[1] == 0 and i[2] == 0:
                continue
            x.append(i[0])
            y.append(i[1])
            z.append(i[2])
    ax.axis((-50, 50, -300, -200))
    ax.scatter(x, y, z, c = 'magenta', s = 1)
    ax.set_zlim(-300, -150)
    plt.show()
