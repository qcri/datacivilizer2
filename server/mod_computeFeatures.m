%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% - compute EEG featrues;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_computeFeatures(in_file_1, in_file_2, out_file, delta_low, delta_high, theta_low, theta_high, alpha_low, alpha_high, beta_low, beta_high)

addpath([pwd, '/Callbacks/']);

% Step1 - read data %
tmp = load([pwd, '/Data/', in_file_1]);

eeg = tmp.eeg;
ekg = tmp.ekg;
channels = tmp.channels;
startTime = tmp.startTime;
Fs = tmp.Fs;                % sampling rate %

tmp = load([pwd, '/Data/', in_file_2]);
Sdata = tmp.Sdata;
stimes = tmp.stimes;
sfreqs = tmp.sfreqs;
col = [-10 25];

% Step 2. Artifact train %
data_car = eeg - repmat(mean(eeg, 1), size(eeg,1),1);   
A = NaN(size(data_car));
for ch = 1: 19
    x = data_car(ch,:);
    A(ch, :)=fcn_IdentifyArtifact2(x, Fs, 5, 500, 1E-5);
end
A = sum(A, 1);

% Step 3. compute features  %
featureArray = fcn_computeAllFeatures(eeg, Fs, A, Sdata, sfreqs, delta_low, delta_high, theta_low, theta_high, alpha_low, alpha_high, beta_low, beta_high);

save([pwd, '/Data/feature_',out_file],'featureArray')
end