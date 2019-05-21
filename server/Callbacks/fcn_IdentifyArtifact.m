function [z,a,e,s]=fcn_IdentifyArtifact(data,Fs);
 
%% find artifacts and suppressions
% z = 1 --> suppression, z=0 --> not suppression
% a = 1 --> artifact,    a=0 --> not artifact
 
%*********************************************************
% filters: bandpass filter [0.5 - 35], also apply notch filter
[bh,ah] = butter(4, 0.5/(Fs/2),'high'); %
[bl,al] = butter(4, 35/(Fs/2),'low'); %
[bn, an] = butter(6, [55 65]./(Fs/2), 'stop'); % notch filter
 
% also filter between 30-50hz to remove emg
[be, ae] = butter(6, [30 50]./(Fs/2)); % bandpass filter
 
%% filter the data 
for i=1:5
    d=data(i,:); 
    d=filtfilt(bn,an,d); % notch filter
    demg(i,:)=filtfilt(be,ae,d); % bandpass -- for emg    
    d=filtfilt(bl,al,d); % lowpass           
    d=filtfilt(bh,ah,d); % highpass
    s(i,:)=d;
    %% calculate the envelope
    e(i,:)=abs(hilbert(d)); 
end
 
%% calculate mean envelope (over active channels)
ME=mean(e([1 2 4 5],:)); ME=smooth(ME, Fs/2); % apply 1/2 second smoothing
e=ME; 
 
%% detect suppressions
% apply threshold -- 5uv
z=(ME<5); 
% remove too-short suppression segments
z=fcnRemoveShortEvents(z,Fs/2); 
% remove too-short burst segments
b=fcnRemoveShortEvents(1-z,Fs/2);
z=1-b; 
z=z';
%% detect artifacts
a=fcnDetectArtifacts(Fs,s,demg);
s=s([1 2 4 5],:);