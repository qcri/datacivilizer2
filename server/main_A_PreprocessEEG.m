%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EEG Preprocessing Pipeline %
% - resample; 
% - apply filters (notch filter, band/high/low-pass filters);
% - generate different montages (bipolar, common average); 
% - clip;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%function [] = main_A_PreprocessEEG(arg1)

%disp(arg1);

%clc
%close all
%clear




addpath([pwd, '/Callbacks/']);

fileName = 'SampleData1.mat';

% Step1 - read data %
tmp = load([pwd, '/Data/', fileName]);
eeg = tmp.data(1:19, :);               % EEG %
ekg = tmp.data(21, :)-tmp.data(20, :); % EKG %
To = datetime(tmp.startTime, 'Inputformat', 'MM-dd-yyyy hh:mm:ss'); % strating timestamp of EEG %
Fs = tmp.Fs; % sampling rate %

% Step2 - resample %
if Fs~=200
    eeg = resample(eeg', 200, Fs)';  
    ekg = resample(ekg', 200, Fs)';
    Fs = 200;
end

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
 
save([pwd, '/Data/clean_', fileName], 'eeg', 'Fs', 'To');
%end