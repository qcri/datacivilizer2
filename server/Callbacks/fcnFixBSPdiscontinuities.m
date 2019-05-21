function absp=fcnFixBSPdiscontinuities(tbsp,absp); 
 
%clear all; clc; format compact; 
 
%% fix residual discontinuities in the bsp that arise from artifact
 
% try removing any portions that are flanked by less than n seconds of good data
n=5*60; 
t=(tbsp-tbsp(1))*24*60*60; % convert to seconds
dt=t(2)-t(1); 
Fs=1/dt; % should be 1 second
 
np=round(Fs*n); 
as=smooth(absp,np); 
 
ind=find(as>0); bsp(ind)=nan; 
absp(ind)=1; 
 
% figure(1); clf; plot(tbsp,bsp,tbsp,absp*.01,tbsp,as*.02,'m--'); 
% xlim([min(tbsp) max(tbsp)]); 
% ylim([0 1]); 