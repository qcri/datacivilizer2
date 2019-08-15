%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EEG Preprocessing Pipeline %
% - resample; 
% - apply filters (notch filter, band/high/low-pass filters);
% - generate different montages (bipolar, common average); 
% - clip;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_clip(in_file, out_file)

tic;

addpath([pwd, '/Callbacks/']);

% Step1 - read data %
tmp = load([pwd, '/Data/', in_file]);

num_channels = size(tmp.data, 1);
eeg = tmp.data(1:num_channels-1,:);
ekg = tmp.data(num_channels,:);
channels = tmp.channels;
startTime = tmp.startTime;
Fs = tmp.Fs;                % sampling rate %

% Step5 - round up if too much by clips at +/-500mV %
eeg(eeg>500)  = 500;
eeg(eeg<-500) = -500;

data = cat(1,eeg,ekg);
dlmwrite([pwd, '/Data/', out_file, '.txt'], data);
save([pwd, '/Data/', out_file], 'data', 'channels', 'startTime', 'Fs');

toc;

end