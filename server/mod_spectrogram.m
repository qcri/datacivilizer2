%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% - compute multitaper spectrogram;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_spectrogram(in_file, out_file_1, out_file_2, nw)

addpath([pwd, '/Callbacks/'])

% Step1 - read data %
tmp = load([pwd, '/Data/', in_file]);

eeg = tmp.data(1:19,:);
Fs = tmp.Fs;                % sampling rate %
eeg_bi = fcn_LBipolar(eeg); % bipolar %

% Step2 - compute multi-taper spectrogram %
params.movingwin = [2 1];      % [windowLength stepSize] %
params.tapers = [nw, 2*nw - 1];% [TW product No.tapers] %
% params.tapers    = [2 3];      % [TW product No.tapers] %
params.fpass     = [0.5 20];   % passband %
params.Fs        = Fs;         % sampling rate %

[Sdata, stimes, sfreqs] = fcn_computeSpec(eeg_bi, params);

Sdata2 = cell2mat(flipud(Sdata(:, 2)));
col = [-10 25];

close all
f = figure('units','normalized','outerposition',[0 0 1 1]);
subplot(6, 1, 1:5)
colormap jet
imagesc(stimes, sfreqs, pow2db(Sdata2), col);
axis(gca,'xy');
xlim([2500 3400])
set(gca, 'xticklabels', [], 'yticklabels', [])
box on
saveas(f, [pwd, '/Data/', out_file_2]);

save([pwd, '/Data/', out_file_1], 'Sdata', 'stimes', 'sfreqs')
end