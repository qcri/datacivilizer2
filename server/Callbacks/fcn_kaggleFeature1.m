function featureSet1 = fcn_kaggleFeature1(X, Fs, band)
    
    M = size(X, 1);
    n = Fs;
    
    P2 = abs(fft(X, n, 2));
    P1 = P2(:,1:n/2+1);
    P1(:,2:end-1) = 2*P1(:,2:end-1);
    
    f = 0:(Fs/n):(Fs/2-Fs/n); % [0 Fs/2-1]
    
    % 1. FFT magnitudes in band [1, 40Hz] %
    P = log10(P1(:, f>=band(1)&f<=band(2))); 
   
    % 2. Correlation coeffs and their eigenvalues in frequency domain: FFT 1-47Hz -> normalization -> correlation coefficients -> eigenvalues
    % normalize for each frequency [column] %
    Pn = (P - repmat(mean(P, 1), size(P, 1), 1))./ repmat(std(P, [], 1), size(P, 1), 1);
    CCf = NaN(M);
    CCf1 = NaN(M);
    for m1 = 1:M
        p1 = Pn(m1, :);
        for m2 = m1:M
            p2 = Pn(m2, :);
            cc = max(xcorr(p1, p2, 'coeff'));
            
            CCf(m1,m2) = cc;
            CCf(m2,m1) = cc;
            
            CCf1(m1,m2) = cc;
        end
    end
    [~, D] = eig(CCf);
    eigVf = abs(diag(D));
    ccf = CCf1(~isnan(CCf1));
    
    % 3. Correlation coeffis and their eigenvalues in time domain: Time series -> normalization -> correlation coefficients -> eigenvalues
    % normalize for each channel [row] %
    Xn = (X - repmat(mean(X, 2), 1, size(X, 2)))./ repmat(std(X, [], 2), 1, size(X, 2));
    CCt = NaN(M);
    CCt1 = NaN(M);
    for m1 = 1:M
        x1 = Xn(m1, :);
        for m2 = m1:M
            x2 = Xn(m2, :);
            cc = max(xcorr(x1, x2, 'coeff'));
            
            CCt(m1,m2) = cc;
            CCt(m2,m1) = cc;
            
            CCt1(m1,m2) = cc;
        end
    end
    [~,D] = eig(CCt);
    eigVt = abs(diag(D));
    cct = CCt1(~isnan(CCt1));
    
    featureSet1 = [fcn_featureStats(P(:))  fcn_featureStats(ccf) fcn_featureStats(eigVf) fcn_featureStats(cct) fcn_featureStats(eigVt)];
    
    
end
        
        
        
        
        
    
   
 
 