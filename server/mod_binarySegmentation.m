%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% - detect burst suppressions
% - detect artifacts (several different kinds of artifacts) 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_binarySegmentation(arg1, arg2)

format compact; 
 
addpath([pwd, '/Callbacks/'])

%%%% Step 1 Load your data %%%%
load([pwd, '/Data/',arg1])
% data [5xN] 5 channels [Fp1; Fp2; Fpz; F7; F8]
% t: time number vector in unit [days]
% Fs: sampling rate

%%%% Step 2 Get binary segmentation %%%%    
[z,a,e,s]=fcn_IdentifyArtifact(data,Fs);
save([pwd, '/Data/',arg2],'z','a','e','t','Fs');

end