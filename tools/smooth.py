# Light smoothing of the skull surface (scalp only; face and neck keep the exact mesh).
import numpy as np
from scipy.ndimage import gaussian_filter
a=np.load('R_raw.npy'); np.save('R_raw_unsmoothed.npy',a)
core=a[:,:360]; pad=np.concatenate([core[:,-6:],core,core[:,:6]],1)
sm=gaussian_filter(pad,sigma=1.1,mode='nearest')[:,6:-6]; b=np.concatenate([sm,sm[:,:1]],1)
el=np.arange(-90,91)[:,None]+0*np.arange(361)[None,:]; az=0*el+np.arange(361)[None,:]
w=np.clip((el+5)/10,0,1)
face_side=np.clip((np.minimum(np.abs(az-0),np.abs(az-360))-50)/15,0,1)
w=np.maximum(w,face_side*np.clip((el+35)/10,0,1))
np.save('R_raw.npy',a*(1-w)+b*w); print('smoothed')
