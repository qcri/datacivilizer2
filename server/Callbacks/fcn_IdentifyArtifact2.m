function a=fcn_IdentifyArtifact2(data,Fs, D, thr1, thr2)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Input: data [1xN] - channel-wise EEG
%        Fs - sampiing rate
%        labels - channel labels
%        D - duration of the sliding window 
%        thr1 - energy term upper bound  
%        thr2 - energy term lower bound  
  
 
% Output: a = 1 --> artifact,    a=0 --> not artifact
 
% default - a=fcn_IdentifyArtifact2(data, Fs, 5, 500, 1E-6)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 
e_avg = abs(data); % energy term %
 
i0=1; i1=1; ct=0; dn=0; 
Nt=size(data,2); 
chunkSize=D; 
a=zeros(1,Nt); 
 
while ~dn  
    i0=i1; 
    if i1==Nt; dn=1; end
    i1=i0+round(Fs*chunkSize); i1=min(i1,Nt); i01=i0:i1; ct=ct+1; % get next data chunk
    A(ct)=0; % set to 1 if artifact is detected
      
    s = e_avg(i01); % current data chunk %
    % check for saturation or flats %
    if max(s>thr1) || max(s<thr2)
        A(ct)=1;
    end
     
    a(i01)=A(ct); 
end
  
if sum(a)<5; ind=find(a==1); a(ind)=0; end