function [Nt,tn,N,an]=fcnGetSuppressionCounts(z,a,t,Fs,nsec); 
 
%% get suppression counts
 
ct=0; n=0; 
N=nsec*Fs; % number of segments; each segment is nsec long (usually use 1 sec)
for j=1:length(z); 
   n=n+z(j); % counting up number of suppressions
   if a(j)==1; n=nan; end
   if ~mod(j,N); 
      ct=ct+1; 
      tn(ct)=t(j); 
      Nt(ct)=n; 
      n=0; 
      if isnan(Nt(ct))
          an(ct)=1; 
      else
          an(ct)=0; 
      end
   end
end