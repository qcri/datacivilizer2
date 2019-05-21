%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% - compute multitaper spectrogram; 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clc
close all
clear

addpath([pwd, '/Callbacks/'])

fileName = 'SampleData1.mat';

% Step1 - read data %
tmp = load([pwd, '/Data/', fileName]);
eeg = tmp.data(1:19, :);    
Fs = tmp.Fs;               
eeg_bi = fcn_LBipolar(eeg); % bipolar %

% Step2 - compute multi-taper spectrogram %
params.movingwin = [2 1];      % [windowLength stepSize] %
params.tapers    = [2 3];      % [TW product No.tapers] %
params.fpass     = [0.5 20];   % passband %
params.Fs        = Fs;         % sampling rate %

[Sdata, stimes, sfreqs] = fcn_computeSpec(eeg_bi, params);
save([pwd, '/Data/spec_', fileName], 'Sdata', 'stimes', 'sfreqs')
