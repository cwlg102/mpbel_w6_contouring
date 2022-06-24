import pydicom
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

dcm = pydicom.dcmread('RTs.dcm')
all_ctr = dcm.ROIContourSequence #ROIContourSequence로 Contour 좌표 불러올 수 있음.

sdx = 0
ctr_volume_coord = [] #일단은 리스트로
#내분점 #좌표끼리 거리마다 weight 주는 방법

for sdx in range(200):
    try:ctr_coord_1dim = all_ctr[0].ContourSequence[sdx].ContourData #슬라이스 넘기면서 Contour좌표데이터 가져옴
    except:break

    #ctr_color = all_ctr[0].ROIDisplayColor #색깔 불러오기
    coord_arr = np.zeros((1, 3)) #미리 좌표 array 만들어 놓고
    adx = 0
    joke = 0;jflag = 0
    for idx in range(0, len(ctr_coord_1dim), 3): #1차원적 데이터인 ContourData를 3차원으로(데이터는 3의 배수이므로 다음과같이)

        #if jflag:joke -= 1
        #else:joke += 1 
        #print('*'*joke)
        #if joke > 20:
        #    jflag = 1
        #elif joke == 1:
        #    jflag = 0
        
        coord_arr = np.append(coord_arr, 
        [[(round((ctr_coord_1dim[idx]))), (round((ctr_coord_1dim[idx+1]))), (round((ctr_coord_1dim[idx+2])))]],
        axis = 0) #voxel화를 위한 것이므로 coord_arr에 추가할 땐 int, (그냥 int하면 내림이 되므로 round 적용시켜서.)
        #np.append를 사용할 땐, append 한 거를 다시 자신에게 초기화 해줘야하고 2차원으로 추가할 땐 [[내용]]이런식으로, 추가할 차원에 맞게 괄호를 열어줘야.

        xi, yi, zi = float(ctr_coord_1dim[idx]), float(ctr_coord_1dim[idx+1]), float(ctr_coord_1dim[idx+2])
        try:xiplus, yiplus, ziplus = float(ctr_coord_1dim[idx+3]), float(ctr_coord_1dim[idx+4]), float(ctr_coord_1dim[idx+5])
        except: xiplus, yiplus, ziplus = float(ctr_coord_1dim[0]), float(ctr_coord_1dim[1]), float(ctr_coord_1dim[2])
        #####예외, xi, yi, zi가 마지막 일경우, 그냥 pass하면 안되고 첫번째 점과 연결을 시켜주어야함.#####

        indiv_coeff = 70
        largedist = ((xi - xiplus)**2 + (yi - yiplus)**2 + (zi - ziplus)**2) ** 0.5
        if largedist < 1: #만약 길이 차이가 적게나서 1보다 작을 때 largedist를 기본 내분 갯수에 곱하면 내분 갯수가 기본보다 작아짐.
            largedist = 1
        indiv = round(indiv_coeff * largedist) #distance에 따라 weight 가 달라짐
        
        for jdx in range(1, indiv):
            #내분점 공식
            coord_arr = np.append(coord_arr, 
            [[(round((((indiv-1-jdx)*xi +(jdx+1)*xiplus)/indiv))), 
            (round((((indiv-1-jdx)*yi +(jdx+1)*yiplus)/indiv))), 
            (round((((indiv-1-jdx)*zi +(jdx+1)*ziplus)/indiv)))]],
            axis = 0)
            
        adx += 1

    sdx += 1 #다음 슬라이스로
    coord_arr = np.delete(coord_arr, 0, axis = 0) #zeros로 만들었으니, 맨앞은 0, 0, 0이라 삭제해주어야함.
    coord_arr = np.unique(coord_arr, axis=0) #중복된 것을 제거해주는 함수.
    ctr_volume_coord.append(coord_arr)
   
#voxelnp값에 하나하나씩 지정.
voxelnp = np.zeros((150, 512, 512)) #(z, y, x)순서.

zcoord = [] #contour출력을 위해 zcoord 만들어 놓기
for _slice in ctr_volume_coord: #voxelnp에 -등으로 되어있는,혹은 범위밖의 좌표값 보정하여 넣어줌.
    Z = abs(_slice[0][2])-150
    zcoord.append(Z)
    for point_idx in range(len(_slice)):
        voxelnp[int(Z)][int(abs(_slice[point_idx][1]))][int(_slice[point_idx][0])+256] = 255

#bfs를 활용하여 안에 채우기.
#갇힌 그림이므로 중점을 구해서 queue에 넣어주기.
for idx in range(len(zcoord)):
    dy = [1, -1, 0, 0]
    dx = [0, 0, 1, -1]
    queue = deque()
    ctrdot = np.where(voxelnp[int(zcoord[idx])]== 255)
    y1, x1 = ctrdot[0][0], ctrdot[1][0]
    y2, x2 = ctrdot[0][len(ctrdot[0])-1], ctrdot[1][len(ctrdot[1])-1]
    center_y = (y1+y2)//2
    center_x = (x1+x2)//2
    queue.append((center_y, center_x))
    while queue:
        y, x = queue.popleft()
        for dir in range(4):
            ny = y + dy[dir]
            nx = x + dx[dir]
            if voxelnp[int(zcoord[idx])][ny][nx] == 255:
                continue
            else:
                voxelnp[int(zcoord[idx])][ny][nx] = 255
                queue.append((ny, nx))
    
    

axes = [] 
fig = plt.figure(figsize = (17, 17))
for idx, image in enumerate(zcoord):
    axes.append(fig.add_subplot(3, 7, idx+1))
    subplot_title=("slice"+str(idx+1))
    axes[-1].set_title(subplot_title)
    plt.imshow(voxelnp[int(image)], cmap = 'gray') #정확히 있는 좌표로 해야함! (idx가 0부터 20까지라 아무것도 못보여준다...)

plt.show()


a = np.where(voxelnp == 255)
print(len(a[0]))

answer = 0
for i in range(len(ctr_volume_coord)):
    
    answer += len(ctr_volume_coord[i])
print('w', answer)