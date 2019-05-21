function [A1, A2] = fcn_bsi(data_r, data_l, band, Fs)

R = 0;
for i = 1:size(data_r, 1)
    R = R+bandpower(data_r(i,:),Fs, band);
end
R = R/size(data_r, 1);


L = 0;
for i = 1:size(data_l, 1)
    L = L+bandpower(data_l(i,:),Fs, band);
end
L = L/size(data_l, 1);

A1 = log(R)-log(L);
A2 = (R-L)/(R+L);