import numpy as np, json
from field import *
exec(open('sec.py').read())
S=np.load('sites.npy',allow_pickle=True).item()
Nz,Iz,LPA,RPA=S['Nz'],S['Iz'],S['LPA'],S['RPA']
A={}
sag,Ls=section(Nz,Iz,np.array([0,200.0,0]),start=Nz,via=np.array([0,200.0,0]),end=Iz)
for f,n in zip(np.arange(1,10)/10,['Fpz','AFz','Fz','FCz','Cz','CPz','Pz','POz','Oz']): A[n]=at(sag,Ls,f)
cor,Lc=section(LPA,RPA,A['Cz'],start=LPA,via=A['Cz'],end=RPA)
A['T7']=at(cor,Lc,.1); A['T8']=at(cor,Lc,.9)
ringL,Lr=section(A['Fpz'],A['Oz'],A['T7'],start=A['Fpz'],via=A['T7'],end=A['Oz'])
ringR,Lr2=section(A['Fpz'],A['Oz'],A['T8'],start=A['Fpz'],via=A['T8'],end=A['Oz'])
for f,l,r in zip(np.arange(1,10)/10,['Fp1','AF7','F7','FT7',None,'TP7','P7','PO7','O1'],['Fp2','AF8','F8','FT8',None,'TP8','P8','PO8','O2']):
    if l: A[l]=at(ringL,Lr,f); A[r]=at(ringR,Lr2,f)
# lateral rows: arc from the left circumference point through the midline point to the right one, equal steps
rows={'F':('F7','Fz','F8',['F7','F5','F3','F1','Fz','F2','F4','F6','F8']),
      'FC':('FT7','FCz','FT8',['FT7','FC5','FC3','FC1','FCz','FC2','FC4','FC6','FT8']),
      'C':('T7','Cz','T8',['T7','C5','C3','C1','Cz','C2','C4','C6','T8']),
      'CP':('TP7','CPz','TP8',['TP7','CP5','CP3','CP1','CPz','CP2','CP4','CP6','TP8']),
      'P':('P7','Pz','P8',['P7','P5','P3','P1','Pz','P2','P4','P6','P8']),
      'AF':('AF7','AFz','AF8',['AF7',None,'AF3',None,'AFz',None,'AF4',None,'AF8']),
      'PO':('PO7','POz','PO8',['PO7',None,'PO3',None,'POz',None,'PO4',None,'PO8'])}
for k,(l,m,r,names) in rows.items():
    pts,L=section(A[l],A[r],A[m],start=A[l],via=A[m],end=A[r])
    for i,n in enumerate(names):
        if n and n not in (l,m,r): A[n]=at(pts,L,i/8)
infL,Li=section(Nz,Iz,LPA,start=Nz,via=LPA,end=Iz); infR,Li2=section(Nz,Iz,RPA,start=Nz,via=RPA,end=Iz)
for f,l,r in zip([.3,.4,.6,.7,.8],['F9','FT9','TP9','P9','PO9'],['F10','FT10','TP10','P10','PO10']): A[l]=at(infL,Li,f); A[r]=at(infR,Li2,f)
A['T9']=LPA; A['T10']=RPA; A['Nz']=Nz; A['Iz']=Iz; A['LPA']=LPA; A['RPA']=RPA
extra={'TP9_clear':S['TP9'],'TP10_clear':S['TP10'],'EOG_L':S['EOG']}
le=np.array(json.load(open('meas.json'))['eyeL']); re_=le*np.array([-1,1,1])
extra['EOG_R']=surf(*angles(np.array([re_[0],re_[1]-20,re_[2]+4])-C))
np.save('all1010.npy',{'sites':A,'extra':extra},allow_pickle=True)
print(len(A),'sites'); print(sorted(A))
