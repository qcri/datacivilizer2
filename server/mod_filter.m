%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EEG Preprocessing Pipeline %
% - resample; 
% - apply filters (notch filter, band/high/low-pass filters);
% - generate different montages (bipolar, common average); 
% - clip;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_filter(arg1, arg2)


addpath([pwd, '/Callbacks/']);

fileName = arg1;

% Step1 - read data %
tmp = load([pwd, '/Data/', fileName]);
eeg = tmp.data(1:19, :);               % EEG %
ekg = tmp.data(21, :)-tmp.data(20, :); % EKG %
To = datetime(tmp.startTime, 'Inputformat', 'MM-dd-yyyy hh:mm:ss'); % strating timestamp of EEG %
Fs = tmp.Fs; % sampling rate %
data = tmp.data;
startTime = tmp.startTime;


% Step3 - filters %
[B1, A1] = iirnotch(60/(Fs/2), 60/(35*Fs/2));    % 60Hz notch %
[B2, A2] = butter(3, [.5, 40]/(Fs/2));           % [.5 to 40Hz] band-pass %
% [B3, A3] = butter(3, .5/(Fs/2), 'high');       %  .5Hz high-pass %
% [B4, A4] = butter(3, 40/(Fs/2), 'low');        %  40Hz low-pass %
for i = 1:size(eeg, 1)
    tmp = eeg(i, :);
    tmp = filter(B1, A1, tmp);
    eeg(i, :) = filter(B2, A2, tmp);
end
ekg = filter(B1, A1, ekg);
ekg = filter(B2, A2, ekg);

save([pwd, '/Data/', arg2], 'data', 'startTime', 'Fs');
end