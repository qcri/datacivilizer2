%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% - detect burst suppressions
% - detect artifacts (several different kinds of artifacts) 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_binarySegmentation(in_file, out_file)

format compact; 
 
addpath([pwd, '/Callbacks/'])

%%%% Step 1 Load your data %%%%
tmp = load([pwd, '/Data/', in_file]);
% data [5xN] 5 channels [Fp1; Fp2; Fpz; F7; F8]
% t: time number vector in unit [days]
% Fs: sampling rate
data = tmp.data;
t = tmp.t;
Fs = double(tmp.Fs);

%%%% Step 2 Get binary segmentation %%%%    
[z,a,e,s]=fcn_IdentifyArtifact(data,Fs);
save([pwd, '/Data/',out_file],'z','a','e','t','Fs');

end