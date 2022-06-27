import numpy as np
import matplotlib.pyplot as plt
voxelnp = np.load('brain_stem_contour_voxel.npy')
#voxelnp = np.transpose(voxelnp, (2, 1, 0))

zc = np.where(voxelnp == 255) #Data 형이 뭔지 고려해주고
zcoord = []
for i in range(len(zc[0])):
    zcoord.append(int(zc[0][i]))
zcoord = list(set(zcoord))


axes = [] 
fig = plt.figure(figsize = (17, 17))
for idx, image in enumerate(zcoord):
    axes.append(fig.add_subplot(3, 7, idx+1)) #바깥루프의 축길이가 얼마나 되는지 고려해서
    subplot_title=("slice"+str(idx+1))
    axes[-1].set_title(subplot_title)
    plt.imshow(voxelnp[int(image)], cmap = 'gray') 

plt.show()