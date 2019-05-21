function features = fcn_featureSeto(data,Sdata,sfreqs, Fs)


% Input data: EEG segment
%       Sdata: Spectrogram segment [cell[4x2]]

% time features: line length, kurtosis, shannon entropy and nonlinear energy.
% spectral features: delta, theta, alpha and beta bandpower. delta to theta
% ratio, theta to alpha ratio and delta to alpha ratio. Kurtosis of delta,
% theta, alpha and beta bandpower.

win_lens = [14 10 6 2]*Fs;
tc = size(data, 2)/2;        % [pts]

% Time domain features [5x4Rx4W]=80 %
ll = NaN(size(data, 1), 4);
kurts =  NaN(size(data, 1), 4);
sentropy =  NaN(size(data, 1), 4);
nleo_mean_abs =  NaN(size(data, 1), 4);
nleo_std =  NaN(size(data, 1), 4);
 
for i=1:size(data, 1) % channel wise %
    for  j=1:4        % window sizes %
        to = tc-win_lens(j)/2+1;
        t1 = tc+win_lens(j)/2;
        seg = data(i, to:t1);
        
        % f1 - normalized line length [18x4]
        ll(i, j) = mean(abs(diff(seg)));  % line length %
        
        % f2 - unbiased kurtosis [18x4]
        kurts(i, j) = kurtosis(seg);
        
        % f3 - shannon entropy
        sentropy(i, j)  =  wentropy(seg,'shannon');
        
        % f4 - nonlinear energy op
        x =  general_nleo(seg);
        nleo_mean_abs(i, j) = mean(abs(x));
        nleo_std(i, j)  = std(x);
    end
end

% Regional average %
ll_R = feature_regionalAvg(ll);
kurts_R = feature_regionalAvg(kurts);
sentropy_R = feature_regionalAvg(sentropy);
nleo_mean_abs_R = feature_regionalAvg(nleo_mean_abs);
nleo_std_R = feature_regionalAvg(nleo_std);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Spectral features 32x4Rx4W = 512 %
delta_kurt = NaN(4);delta_mean = NaN(4);delta_std = NaN(4);delta_min = NaN(4);delta_95th = NaN(4);
theta_kurt = NaN(4);theta_mean = NaN(4);theta_std = NaN(4);theta_min = NaN(4);theta_95th = NaN(4);
alpha_kurt = NaN(4);alpha_mean = NaN(4);alpha_std = NaN(4);alpha_min = NaN(4);alpha_95th = NaN(4);
beta_kurt = NaN(4);beta_mean = NaN(4);beta_std = NaN(4);beta_min = NaN(4);beta_95th = NaN(4);
delta_theta_mean = NaN(4);delta_theta_std = NaN(4);delta_theta_min = NaN(4);delta_theta_95th = NaN(4);
delta_alpha_mean = NaN(4);delta_alpha_std = NaN(4);delta_alpha_min = NaN(4);delta_alpha_95th = NaN(4);
theta_alpha_mean = NaN(4);theta_alpha_std = NaN(4);theta_alpha_min = NaN(4);theta_alpha_95th = NaN(4);

for k = 1: 4 % 4 regional groups
    for  j=1:4 % window sizes %
        to = round((tc-win_lens(j)/2+1)/Fs) + 1;
        t1 = round((tc+win_lens(j)/2)/Fs);
        %disp([to t1])
        seg_s = Sdata{k}(:, to:t1);

        % band power
        x_total = bandpower(seg_s,sfreqs,[sfreqs(1) sfreqs(end)],'psd')+eps;  % dimonimator %
        x_delta = bandpower(seg_s,sfreqs,[1 4],'psd');   % vec
        x_theta = bandpower(seg_s,sfreqs,[4 8],'psd');
        x_alpha = bandpower(seg_s,sfreqs,[8 12],'psd');
        x_beta = bandpower(seg_s,sfreqs,[12 18],'psd');
        
        r_delta = x_delta./x_total;   
        r_theta = x_theta./x_total;    
        r_alpha = x_alpha./x_total;    
        r_beta = x_beta./x_total;   
        r_delta_theta = x_delta./(x_theta+eps); % delta to theta ratio
        r_delta_alpha = x_delta./(x_alpha+eps); % delta to alpha ratio
        r_theta_alpha = x_theta./(x_alpha+eps); % theta to alpha ratio

        
        delta_kurt(k, j) = kurtosis(x_delta);
        y = bp_stats(r_delta);
        delta_mean(k, j) = y(1); delta_std(k, j) = y(2); delta_min(k, j) = y(3); delta_95th(k, j) = y(4);
        
        theta_kurt(k, j) = kurtosis(x_theta);
        y = bp_stats(r_theta);
        theta_mean(k, j) = y(1); theta_std(k, j) = y(2); theta_min(k, j) = y(3); theta_95th(k, j) = y(4);
        
        alpha_kurt(k, j) = kurtosis(x_alpha);
        y = bp_stats(r_alpha);
        alpha_mean(k, j) = y(1); alpha_std(k, j) = y(2); alpha_min(k, j) = y(3); alpha_95th(k, j) = y(4);
        
        beta_kurt(k, j) = kurtosis(x_beta);
        y = bp_stats(r_beta);
        beta_mean(k, j) = y(1); beta_std(k, j) = y(2); beta_min(k, j) = y(3); beta_95th(k, j) = y(4);
        
        y = bp_stats(r_delta_theta);
        delta_theta_mean(k, j) = y(1); delta_theta_std(k, j) = y(2); delta_theta_min(k, j) = y(3); delta_theta_95th(k, j) = y(4);
        
        y = bp_stats(r_delta_alpha);
        delta_alpha_mean(k, j) = y(1); delta_alpha_std(k, j) = y(2); delta_alpha_min(k, j) = y(3); delta_alpha_95th(k, j) = y(4);
        
        y = bp_stats(r_theta_alpha);
        theta_alpha_mean(k, j) = y(1); theta_alpha_std(k, j) = y(2); theta_alpha_min(k, j) = y(3); theta_alpha_95th(k, j) = y(4);
    end
end

featureT = [ll_R(:); 
            kurts_R(:);
            sentropy_R(:);
            nleo_mean_abs_R(:);
            nleo_std_R(:)];
          
featureS = [delta_kurt(:); delta_mean(:); delta_std(:); delta_min(:); delta_95th(:);
            theta_kurt(:); theta_mean(:); theta_std(:); theta_min(:); theta_95th(:);
            alpha_kurt(:); alpha_mean(:); alpha_std(:); alpha_min(:); alpha_95th(:);
            beta_kurt(:);  beta_mean(:);  beta_std(:);  beta_min(:);  beta_95th(:);
            delta_theta_mean(:); delta_theta_std(:); delta_theta_min(:); delta_theta_95th(:);
            delta_alpha_mean(:); delta_alpha_std(:); delta_alpha_min(:); delta_alpha_95th(:);
            theta_alpha_mean(:); theta_alpha_std(:); theta_alpha_min(:); theta_alpha_95th(:)];

features = [featureT; featureS]';  % 592x1  [16 kurtosis features (4 band x 4 region) in largest win size 14sec]
            
