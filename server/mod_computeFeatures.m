%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% - compute EEG featrues;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_computeFeatures(arg1, arg2)


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

tmp = load([pwd, '/Data/', arg2]);
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
featureArray = fcn_computeAllFeatures(eeg, Fs, A, Sdata, sfreqs);

save([pwd, '/Data/feature_',arg2],'featureArray')

end