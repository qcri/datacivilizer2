
function [] = mod_bsp(in_file, out_file)

addpath([pwd, '/Callbacks/']);

%%%% Step 3 Compute the BSP  %%%%
% initialize bsp algorithm
sig=(1e-6)/3; 
z0=log(1); 
z1=z0; 
sig0=sig; 
W0=sig; 
W1=W0;

%Nt=[]; An=[]; tn=[]; an=[]; tmin=inf; tmax=0; tt=[];
  
% get data -- t,z,a [t is in actual time, dt in days]
tmp = load([pwd, '/Data/',in_file]);
z = tmp.z;
a = tmp.a;
t = tmp.t;
Fs = tmp.Fs;

% prepare the current chunk of data for bsp algorithm
nsec=1; 
[Nt,tn,N,An]=fcnGetSuppressionCounts(z,a,t,Fs,nsec); % an marks missing data     

ind = find(tn==0,1); if ~isempty(ind); keyboard; end
tmin=min(inf,min(tn)); 
tmax=max(0,max(tn)); 
 
% interpolate; note: tn is in days
Ttot=(tmax-tmin)*24*60*60; % total number of seconds
dtn=1; % 1 second intervals
Ntot=ceil(Ttot/dtn);
ti=linspace(tmin,tmax,Ntot);
Nti=nan(size(ti));
Ani=ones(size(ti));

temp=tn; 
ntemp=Nt; 
atemp=An;

% find index of best match for temp(1) in ti
[d,jj]=min(abs(temp(1)-ti)); 
Nti(jj:jj+length(temp)-1)=ntemp; 
Ani(jj:jj+length(temp)-1)=atemp; 
 
Nt=Nti; 
absp=Ani;
tbsp=linspace(tmin,tmax,length(absp));    % necessary rarely b/c the above process inserts some zeros
absp=fcnFixBSPdiscontinuities(tbsp,absp); % remove residual discontinuities -- edge effects
ind=find(absp); Nt(ind)=nan; 

% initialize z1, W1 by running bsp algorithm on a short initial segment
nn=min(500,length(Nt));
[W1,z1,~]=fcnGetBSP_WithMissingData(Nt(1:nn),N,W1,z1,sig);

% calculate entire bsp 
if (isnan(z1)||isnan(W1)); W1=1; z1=1; end
[W1,z1, bsp]=fcnGetBSP_WithMissingData(Nt,N,W1,z1,sig); 

save([pwd, '/Data/',out_file],'W1','z1','bsp'); 

