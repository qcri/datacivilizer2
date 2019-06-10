%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EEG Preprocessing Pipeline %
% - resample; 
% - apply filters (notch filter, band/high/low-pass filters);
% - generate different montages (bipolar, common average); 
% - clip;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_resample(arg1, arg2)

%disp(arg1);

%clc
%close all
%clear




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

% Step2 - resample %
if Fs~=200
    eeg = resample(eeg', 200, Fs)';  
    ekg = resample(ekg', 200, Fs)';
    Fs = 200;
end

%dlmwrite([pwd, '/Data/resample.txt'], data);
dlmwrite([pwd, '/Data/', arg2, '.txt'], data);
save([pwd, '/Data/', arg2], 'data', 'startTime', 'Fs');

end