function [spect, stimes, sfreqs]=mtspecgram_jj(varargin)
%MTSPECGRAM  Computes spectrogram of EEG data using multitaper method
%
%   Usage:
%   [spect,stimes,sfreqs]=mtspecgram(data, fs)
%   [spect,stimes,sfreqs]=mtspecgram(data, params, movingwin)
%
%   Inputs
%   data: data
%   fs:  sampling frequency
%   params: structure with fields tapers, pad, Fs, fpass, err, trialave [see getparams(params)for more detail]
%
%   Outputs
%   spect: spectrogram
%   stimes:time index
%   sfreqs:freq index
 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Get time series data
data=varargin{1};

%Handle variable inputs
if ~isstruct(varargin{2})
    %Default spectral parameters
    params.pad=0;
    params.Fs=varargin{2};
    params.fpass=[0 55];
    params.err=0;
    params.trialave=0;
    params.tapers=[3 5];
    movingwin=[4 1];
    
else
    params=varargin{2};
    movingwin=varargin{3};
end

[tapers,pad,Fs,fpass,~,trialave,params]=getparams(params);

data=change_row_to_column(data);
[N,Ch]=size(data);
Nwin=round(Fs*movingwin(1));  % number of samples in window
Nstep=round(movingwin(2)*Fs); % number of samples to step through
nfft=max(2^(nextpow2(Nwin)+pad),Nwin);
[sfreqs,findx]=getfgrid(Fs,nfft,fpass);  Nf=length(sfreqs);
params.tapers=dpsschk(tapers,Nwin,Fs); % check tapers

winstart=1:Nstep:N-Nwin+1;
nw=length(winstart);

if trialave
    S = zeros(nw,Nf);
else
    S = zeros(nw,Nf,Ch);
end

% taps=dpsschk(tapers,N,Fs); % check tapers

%Deal with initial cases
for n=1:2
    indx=winstart(n):winstart(n)+Nwin-1;
    datawin=detrend(data(indx,:));
    datawin=change_row_to_column(datawin);
    N=size(datawin,1);
    taps=dpsschk(tapers,N,Fs);
    J=mtfftc(datawin,taps,nfft,Fs);
    J=J(findx,:,:);
    s=squeeze(mean(conj(J).*J,2)); 
    if trialave; s=squeeze(mean(s,2));end;
    S(n,:,:)=s;
end
%Run all subsequent in parallel
% parfor n=3:nw-1;
for n=3:nw-1;
    indx=winstart(n):winstart(n)+Nwin-1;
    datawin=detrend(data(indx,:));
    datawin=change_row_to_column(datawin);
    J=mtfftc(datawin,taps,nfft,Fs);
    J=J(findx,:,:);
    s=squeeze(mean(conj(J).*J,2));
    if trialave; s=squeeze(mean(s,2));end;
    S(n,:,:)=s;
end

spect=squeeze(S);

winmid=winstart+round(Nwin/2);
stimes=winmid/Fs;


