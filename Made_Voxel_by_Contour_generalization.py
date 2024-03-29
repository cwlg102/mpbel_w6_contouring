import pydicom
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
dcm = pydicom.dcmread('RTs.dcm')
all_ctr = dcm.ROIContourSequence #ROIContourSequence로 Contour 좌표 불러올 수 있음.

ctr_volume_coord = [] #일단은 리스트로
#내분점 #좌표끼리 거리마다 weight 주는 방법

for _slice in range(200):
    try:ctr_coord_1dim = all_ctr[0].ContourSequence[_slice].ContourData #슬라이스 넘기면서 Contour좌표데이터 가져옴
    except:break

    #ctr_color = all_ctr[0].ROIDisplayColor #색깔 불러오기
    coord_arr = np.zeros((1, 3)) #미리 슬라이스의 좌표를 추가 할 array 만들어 놓고

    
    for idx in range(0, len(ctr_coord_1dim), 3): #1차원적 데이터인 ContourData를 3차원으로(데이터는 3의 배수이므로 다음과같이)

        #현재 점 추가.
        coord_arr = np.append(coord_arr, 
        [[(round((ctr_coord_1dim[idx]))), (round((ctr_coord_1dim[idx+1]))), (round((ctr_coord_1dim[idx+2])))]],
        axis = 0) #voxel화를 위한 것이므로 coord_arr에 추가할 땐 int, (그냥 int하면 내림이 되므로 round 적용시켜서.)
        #np.append를 사용할 땐, append 한 거를 다시 자신에게 초기화 해줘야하고 2차원으로 추가할 땐 [[내용]]이런식으로, 추가할 차원에 맞게 괄호를 열어줘야.
        
        #현재 인덱스 - x, y, z좌표 
        xi, yi, zi = float(ctr_coord_1dim[idx]), float(ctr_coord_1dim[idx+1]), float(ctr_coord_1dim[idx+2])
        #다음 인덱스 - 위의 인덱스에서 3씩 추가한 값
        try:xiplus, yiplus, ziplus = float(ctr_coord_1dim[idx+3]), float(ctr_coord_1dim[idx+4]), float(ctr_coord_1dim[idx+5]) 
        #####예외, xi, yi, zi가 마지막 일경우, 그냥 pass하면 안되고 첫번째 점과 연결을 시켜주어야함.#####
        except: xiplus, yiplus, ziplus = float(ctr_coord_1dim[0]), float(ctr_coord_1dim[1]), float(ctr_coord_1dim[2])
        
        #내분 계수, 70이상으로 잡을 시 채우는 점/ 걸리는 시간의 비율이 매우매우낮아진다. 5이상 70이하가 유효하게 쓸만한 범위.
        indiv_coeff = 30
        largedist = ((xi - xiplus)**2 + (yi - yiplus)**2 + (zi - ziplus)**2) ** 0.5
        if largedist < 1: #만약 길이 차이가 적게나서 1보다 작을 때 largedist를 기본 내분 갯수에 곱하면 내분 갯수가 기본보다 작아짐.
            largedist = 1 #따라서 길이 차이가 적다면 largedist를 1로.
        indiv = round(indiv_coeff * largedist) #largedist에 따라 weight가 달라짐(largedist가 크면(다음 점과의 떨어진 거리가 길다면) 내분도 많이함)
        
        #내분점을 추가. 다음 점은 다음 반복에서 추가할 것이므로 추가할 필요없음.
        for jdx in range(1, indiv):
            coord_arr = np.append(coord_arr, 
            [[(round((((indiv-1-jdx)*xi +(jdx+1)*xiplus)/indiv))), 
            (round((((indiv-1-jdx)*yi +(jdx+1)*yiplus)/indiv))), 
            (round((((indiv-1-jdx)*zi +(jdx+1)*ziplus)/indiv)))]],
            axis = 0)
    
    coord_arr = np.delete(coord_arr, 0, axis = 0) #zeros로 coord_arr의 head에 더미를 만들었으니, 맨앞은 0, 0, 0이라 삭제해주어야함.
    coord_arr = np.unique(coord_arr, axis = 0) #float 계산에 round롤 하므로 겹치는 점을 삭제.
    ctr_volume_coord.append(coord_arr) #ctr_volume_coord에 좌표 정보가 정리된 2차원 array를 추가함.



#voxelnp값에 하나하나씩 지정.
voxelnp = np.zeros((150, 512, 512)) #(z, y, x)순서, 150, 512, 512 복셀화.

zcoord = [] #contour출력을 위해 zcoord 만들어 놓기

#넘파이 array는 양의 정수로 인덱싱해야하므로 좌표 변환이 필요.
for _slice in ctr_volume_coord: #voxelnp에 -등으로 되어있는,혹은 범위밖의 좌표값 보정하여 넣어줌.
    Z = abs(_slice[0][2])
    zcoord.append(Z)
if max(zcoord) - min(zcoord) > 150: 
    print('voxelnp size 수정 필요')
    quit()

zmid = (min(zcoord)+max(zcoord))//2 #양의 값으로 변환 시킨 z값들 중 중점을 구함
trf_coeff = zmid -  75 #zcoord의 중점을, 150의 가운데로 옮겨줄수 있는 값을 구함(z의 최대 좌표-최소 좌표 < 150이어야 이런 변환 가능)
for i in range(len(zcoord)): 
    zcoord[i] -= trf_coeff #모든 값에 대해 위에서 구한 trf_coeff를 빼줌

#위에서 변환한 좌표로 voxel만들어주기
for idx, _slice in enumerate(ctr_volume_coord):
    for point_idx in range(len(_slice)):
        voxelnp[int(zcoord[idx])][int(abs(_slice[point_idx][1]))][int(_slice[point_idx][0])+256] = 255
#np.save('brain_stem_voxel', voxelnp)

#for idx in range(len(zcoord)):
#    dy = [1, -1, 0, 0]
#    dx = [0, 0, 1, -1]
#    queue = deque()
#    ctrdot = np.where(voxelnp[int(zcoord[idx])]== 255)
#    y1, x1 = ctrdot[0][0], ctrdot[1][0]
#    y2, x2 = ctrdot[0][len(ctrdot[0])-1], ctrdot[1][len(ctrdot[1])-1]
#    center_y = (y1+y2)//2
#    center_x = (x1+x2)//2
#    queue.append((center_y, center_x))
#    while queue:
#        y, x = queue.popleft()
#        for dir in range(4):
#            ny = y + dy[dir]
#            nx = x + dx[dir]
#            if ny < 0 or nx < 0 or nx >= 512 or ny >= 512:
#                continue
#            if voxelnp[int(zcoord[idx])][ny][nx] == 255:
#                continue
#            else:
#                voxelnp[int(zcoord[idx])][ny][nx] = 255
#                queue.append((ny, nx))

#만든 voxel로 슬라이스마다 contour 출력
axes = [] 
fig = plt.figure(figsize = (17, 17))
for idx, image in enumerate(zcoord):
    axes.append(fig.add_subplot(3, 7, idx+1))
    subplot_title=("slice"+str(idx+1))
    axes[-1].set_title(subplot_title)
    plt.imshow(voxelnp[int(image)], cmap = 'gray') 

plt.show()

# a = np.where(voxelnp == 255)
# print(len(a[0]))

# answer = 0
# for i in range(len(ctr_volume_coord)):
    
    # answer += len(ctr_volume_coord[i])
# print('w', answer)