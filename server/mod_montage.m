%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EEG Preprocessing Pipeline %
% - resample; 
% - apply filters (notch filter, band/high/low-pass filters);
% - generate different montages (bipolar, common average); 
% - clip;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_montage(in_file, out_file, montage_type)

addpath([pwd, '/Callbacks/']);

% Step1 - read data %
tmp = load([pwd, '/Data/', in_file]);

eeg = tmp.eeg;
ekg = tmp.ekg;
channels = tmp.channels;
startTime = tmp.startTime;
Fs = tmp.Fs;                % sampling rate %

% Step4 - filters %
if montage_type == "L-bipolar"  % L-bipolar montage %
    eeg = fcn_LBipolar(eeg); 
elseif montage_type == "common_avg_ref" || montage_type == "car"    % common average ref. montage %
    eeg = eeg - repmat(mean(eeg, 1), size(eeg, 1), 1);
% else
%     eeg = eeg; % monopolar montage %
end

data = cat(1,eeg,ekg);
dlmwrite([pwd, '/Data/', out_file, '.txt'], data);
save([pwd, '/Data/', out_file], 'eeg', 'ekg', 'channels', 'startTime', 'Fs');
end