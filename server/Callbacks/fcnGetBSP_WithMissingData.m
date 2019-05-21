function [W1,z1,ph]=fcnGetBSP_WithMissingData(Nt,N,W1,z1,sig); 
 
%% Get BSP for a new chunk of data
% data format: Nt -- number of 1s (suppressions) in the observation interval
 
% input: 
% Nt [sequence of observations]
% W1, z1 -- initial values
% maximum possible value of Nt [number of samples included in the interval]
% sig -- smoothness/memory parameter
 
for j=1:length(Nt)
    %% observations
    %if j>64000; keyboard; end
%     if isnan(z1); keyboard; end
%     if W1<0; keyboard; end
 
    y(j)=Nt(j); 
 
    %% inference
    z0= z1;         % 1-step prediction
    W0 = W1 + sig;  % 1-step prediction variance
    W0i = 1/W0;
    x0 = exp(z0); % 1-step prediction value of x
    p0 = (1-exp(-x0))/(1+exp(-x0)); % estimated bsp - eval at 1-step prediction
    p0=min(p0,0.999); 
 
    % data not missing
    if ~isnan(Nt(j))
        c = x0*exp(x0)/(1+exp(x0))*(1-p0); % first derivative, eval at 1-step pred
        d = c*(1+x0-(1-p0)*x0*exp(x0));
        g = (1/(p0*(1-p0)))*(N*c^2 - (Nt(j)-N*p0)*(d-c^2*(1-2*p0)/(p0*(1-p0))));
        g = max(g,0.0001); 
        W1i = W0i + g;         
        W1 = 1/W1i;
        z1 = z0 + W1*c*(1/(p0*(1-p0)))*(Nt(j)-p0*N); 
    else
        W1 = W0; 
        z1 = z0; 
    end
         
%     zz1(j)=z1; 
%     zz0(j)=z0; 
%     w0(j)=W0; 
%     w1(j)=W1; 
%     pp(j)=p0; 
%     gg(j)=g; 
     
    % estimated bsp
    x1 = exp(z1); 
    ph(j) = (1-exp(-x1))/(1+exp(-x1));  
     
end