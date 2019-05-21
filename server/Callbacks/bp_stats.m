function x = bp_stats(rp)

x = NaN(4, 1);
x(1) = mean(rp);
x(2) = std(rp);
x(3)  = min(rp);
x(4) =  prctile(rp,95);