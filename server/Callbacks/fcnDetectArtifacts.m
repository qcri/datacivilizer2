function a=fcnDetectArtifacts(Fs,data,dataEMG);
 
%% check for artifacts in 5 second blocks-- each block is counted all-or-none as artifact
 
% returns vector a, with 1=artifact, 0=no artifact
 
% checks: 
% 1. amptlitude in any channel > 500uv 
% 2. loose channel (gotman criteria)
% 3. emg artifact >50%
 
i0=1; i1=1;
ct=0; 
dn=0; 
Nt=size(data,2); 
chunkSize=5; % 5 second chunks
a=zeros(1,Nt); 
while ~dn  
    %% get next data chunk
    i0=i1; 
    if i1==Nt; dn=1; end
    i1=i0+round(Fs*chunkSize); i1=min(i1,Nt); i01=i0:i1; ct=ct+1; % get next data chunk
    A(ct)=0; % set to 1 if artifact is detected
     
    s=data(:,i01); % 5 second data chunk
    de=dataEMG(:,i01);
     
    %% check for saturation
    for i=[1 2 4 5]; if max(s(i,:)>500); A(ct)=1; end; end % max amplitude >500uv
     
     
    %% check for emg artifact
    for i=[1 2 4 5]; v=std(de(i,:)); if v>5; A(ct)=1; end; end % max amplitude >500uv
    
    %% check for implausibly low variance
    %
    for i=[1 2 4 5]; v=std(s(i,:)); if v<0.0001; A(ct)=1; end; end % max amplitude >500uv
 
    
 
%     if v<0.1; 
%         disp(v); 
%         figure(1); clf; plot(s(1,:)); 
%         keyboard
%     end
 
    %% check for loose channels
    c1=s(2,:)-s(1,:); c2=s(1,:)-s(4,:); c3=s(1,:)-s(2,:); c4=s(2,:)-s(5,:);
    m12=mean(abs(c1+c2)); m1=mean(abs(c2)); c=(m12< 1/2*m1); if c==1; A(ct)=1; end % fp1-f7
    m12=mean(abs(c3+c4)); m1=mean(abs(c4)); c=(m12< 1/2*m1); if c==1; A(ct)=1; end % fp2-f8
     
    a(i01)=A(ct); 
end
 
if sum(a)<5; ind=find(a==1); a(ind)=0; end