function features = fcn_bsiFeatures(seg, Fs)
    % seg - monopolar channel EEG %
    % Fs  - sampling rate % 

    tc = 1400; w = [2 6 10 14];
        
    % Loop per temporal window % 
    features = [];  % row per center %
    
    % 4 temporal windows #
    for n = 1:4 

        a = tc-round(.5*w(n)*Fs)+1;
        b = a+w(n)*Fs-1;

        data = seg(:, a:b);
        data = data - repmat(mean(data, 1), size(data, 1), 1);  % CAR montage %

        % BSI feature x2 %
        [A1_delta, A2_delta] = fcn_bsi(data(1:8,:), data(12:19,:), [.5, 4], Fs);
        [A1_theta, A2_theta] = fcn_bsi(data(1:8,:), data(12:19,:), [ 4, 7], Fs);
        [A1_alpha, A2_alpha] = fcn_bsi(data(1:8,:), data(12:19,:), [ 8, 15], Fs);
        [A1_beta ,  A2_beta] = fcn_bsi(data(1:8,:), data(12:19,:), [ 16, 31], Fs);
        [A1_gamma, A2_gamma] = fcn_bsi(data(1:8,:), data(12:19,:), [ 32, 50], Fs);

        BSI = [A1_delta, A2_delta, A1_theta, A2_theta, A1_alpha, A2_alpha, A1_beta ,  A2_beta, A1_gamma, A2_gamma];
        
        % Network features %
        xCorr = NaN(size(data, 1));
        for n1 = 1: size(data, 1)
            s1 = data(n1, :);
            for n2 = n1+1:size(data, 1)
                s2 = data(n2, :);
                xCorr(n1, n2) = max(xcorr(s1, s2, 'coeff'));
            end
        end
        featuresNet = fcn_networkF(xCorr);

        features = [features [BSI, featuresNet]];
    end
end
 