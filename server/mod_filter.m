%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EEG Preprocessing Pipeline %
% - resample; 
% - apply filters (notch filter, band/high/low-pass filters);
% - generate different montages (bipolar, common average); 
% - clip;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_filter(in_file, out_file, notch_freq, high_pass_freq, low_pass_freq)

addpath([pwd, '/Callbacks/']);

% Step1 - read data %
tmp = load([pwd, '/Data/', in_file]);

eeg = tmp.eeg;
ekg = tmp.ekg;
channels = tmp.channels;
startTime = tmp.startTime;
Fs = tmp.Fs;                % sampling rate %

% To = datetime(tmp.startTime, 'Inputformat', 'MM-dd-yyyy hh:mm:ss'); % strating timestamp of EEG %

% Step3 - filters %
[B1, A1] = iirnotch(notch_freq/(Fs/2), notch_freq/(35*Fs/2));               % notch (60Hz by default)     %
[B2, A2] = butter(3, [high_pass_freq, low_pass_freq]/(Fs/2));               % [high-pass to low-pass] band-pass      %
% [B3, A3] = butter(3, high_pass_freq/(Fs/2), 'high');                      % high-pass (.5Hz by default) %
% [B4, A4] = butter(3, low_pass_freq/(Fs/2), 'low');                        % low-pass (40Hz by default)  %
for i = 1:size(eeg, 1)
    tmp = eeg(i, :);
    tmp = filter(B1, A1, tmp);
    eeg(i, :) = filter(B2, A2, tmp);
end
ekg = filter(B1, A1, ekg);
ekg = filter(B2, A2, ekg);

data = cat(1,eeg,ekg);
dlmwrite([pwd, '/Data/', out_file, '.txt'], data);
save([pwd, '/Data/', out_file], 'eeg', 'ekg', 'channels', 'startTime', 'Fs');
end