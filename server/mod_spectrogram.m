%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% - compute multitaper spectrogram; 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_spectrogram(in_file, out_file, nw)

addpath([pwd, '/Callbacks/'])

% Step1 - read data %
tmp = load([pwd, '/Data/', in_file]);

eeg = tmp.eeg;
Fs = tmp.Fs;                % sampling rate %             
eeg_bi = fcn_LBipolar(eeg); % bipolar %

% Step2 - compute multi-taper spectrogram %
params.movingwin = [2 1];      % [windowLength stepSize] %
params.tapers = [nw, 2*nw - 1];% [TW product No.tapers] %
% params.tapers    = [2 3];      % [TW product No.tapers] %
params.fpass     = [0.5 20];   % passband %
params.Fs        = Fs;         % sampling rate %

[Sdata, stimes, sfreqs] = fcn_computeSpec(eeg_bi, params);
save([pwd, '/Data/', out_file], 'Sdata', 'stimes', 'sfreqs')
end