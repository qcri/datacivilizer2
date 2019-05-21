%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EEG Preprocessing Pipeline %
% - resample; 
% - apply filters (notch filter, band/high/low-pass filters);
% - generate different montages (bipolar, common average); 
% - clip;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_clip(arg1, arg2)


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

% Step4 - do montages %
eeg_mon = eeg;                                          % monopolar montage %
eeg_bi = fcn_LBipolar(eeg);                             % L-bipolar montage %
eeg_car = eeg - repmat(mean(eeg, 1), size(eeg, 1), 1);  % common average ref. montage %

% Step5 - round up if too much by clips at +/-500mV %
eeg_mon(eeg_mon>500)  = 500;
eeg_mon(eeg_mon<-500) = -500;

eeg_bi(eeg_bi>500)  = 500;
eeg_bi(eeg_bi<-500) = -500;

eeg_car(eeg_car>500)  = 500;
eeg_car(eeg_car<-500) = -500;

save([pwd, '/Data/', arg2], 'data', 'startTime', 'Fs');
end