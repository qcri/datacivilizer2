function features = fcn_networkF(X)

% X: xcorr coeff array

x = X(~isnan(X));

x_min = min(x);
x_max = max(x);
x_mean = mean(x);
x_std = std(x);

x_q1 = prctile(x, 25);
x_q2 = prctile(x, 50);
x_q3 = prctile(x, 75);
x_q4 = prctile(x, 95);
x_iqr = x_q3 - x_q1;

 
n_thr25 = length(find(x>.25));
n_thr50 = length(find(x>.50));
n_thr75 = length(find(x>.75));
n_thr95 = length(find(x>.95));

features = [x_min x_max x_mean x_std ...
            x_q1 x_q2 x_q3 x_q4 x_iqr ...
            n_thr25 n_thr50 n_thr75 n_thr95];