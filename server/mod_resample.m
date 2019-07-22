%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EEG Preprocessing Pipeline %
% - resample; 
% - apply filters (notch filter, band/high/low-pass filters);
% - generate different montages (bipolar, common average); 
% - clip;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_resample(in_file, out_file, resample_freq)

addpath([pwd, '/Callbacks/']);

% Step1 - read data %
tmp = load([pwd, '/Data/', in_file]);

eeg = tmp.eeg;
ekg = tmp.ekg;
channels = tmp.channels;
startTime = tmp.startTime;
Fs = tmp.Fs;                % sampling rate %

% Step2 - resample %
if Fs~=resample_freq
    eeg = resample(eeg', resample_freq, Fs)';  
    ekg = resample(ekg', resample_freq, Fs)';
    Fs = resample_freq;
end

data = cat(1,eeg,ekg);
dlmwrite([pwd, '/Data/', out_file, '.txt'], data);
save([pwd, '/Data/', out_file], 'eeg', 'ekg', 'channels', 'startTime', 'Fs');
end