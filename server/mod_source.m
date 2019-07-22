%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EEG Preprocessing Pipeline %
% - resample; 
% - apply filters (notch filter, band/high/low-pass filters);
% - generate different montages (bipolar, common average); 
% - clip;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_source(in_file, out_file)

addpath([pwd, '/Callbacks/']);

% Step1 - read data %
tmp = load([pwd, '/Data/', in_file]);

if isfield(tmp,'channels')
    data = tmp.data;            % data          %
    channels = tmp.channels;    % channel names %
    startTime = tmp.startTime;  % timestamp     %
    Fs = tmp.Fs;                % sampling rate %
    eeg = data(1:19, :);             % EEG %
    ekg = data(21, :) - data(20, :); % EKG %
    
    data = cat(1,eeg,ekg);
    dlmwrite([pwd, '/Data/', out_file, '.txt'], data);
    save([pwd, '/Data/', out_file], 'eeg', 'ekg', 'channels', 'startTime', 'Fs');
else
    data = tmp.data;            % data               %
    t = tmp.t;                  % time number vector %
    Fs = tmp.Fs;                % sampling rate      %
    dlmwrite([pwd, '/Data/', out_file, '.txt'], data);
    save([pwd, '/Data/', out_file], 'data', 't', 'Fs');
end