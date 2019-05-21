%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EEG Preprocessing Pipeline %
% - resample; 
% - apply filters (notch filter, band/high/low-pass filters);
% - generate different montages (bipolar, common average); 
% - clip;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_montage(arg1, arg2)


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
eeg_mon = eeg;                                          % monopolar montage %
eeg_bi = fcn_LBipolar(eeg);                             % L-bipolar montage %
eeg_car = eeg - repmat(mean(eeg, 1), size(eeg, 1), 1);  % common average ref. montage %

save([pwd, '/Data/', arg2], 'data', 'startTime', 'Fs');
end