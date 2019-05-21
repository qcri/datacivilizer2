function featureSet2 = fcn_kaggleFeature2(X, Fs)

    [M, N] = size(X);
       
    % 1. Scater coeff %
    % Set up default filter bank with averaging scale of Fs samples.
    T = 2*Fs;
    filt_opt = default_filter_options('audio', T);

    % Only compute zeroth-, first- and second-order scattering.
    scat_opt.M = 0;

    % Prepare wavelet transforms to use in scattering.
    [Wop, ~] = wavelet_factory_1d(N, filt_opt, scat_opt);
    
    SC = [];
    for m = 1:M
        x = X(m,:)';
        
        % Compute the scattering coefficients of x.
        S = scat(x, Wop);
        SC = [SC; (S{1, 1}.signal{1})];
    end
    
    SC = fcn_featureStats(SC);
    
    % 2. covarance matrix for different EEG bands %
    bands = [.5, 4; 4, 7; 8, 15; 16, 31; 32, 50];
    C = [];
    for i = 1:size(bands, 1)
        [Bi, Ai] = butter(3, bands(i,:)/(0.5*Fs));
        Xi = X;
        for m = 1:M
            Xi(m,:) = filter(Bi, Ai, X(m,:));
        end
        C = [C, fcn_featureStats(cov(Xi))];
    end
    
    % 3. Data 1st 2nd derivertive %
    t = 1:N;
    D1 = [];
    D2 = [];
    for m = 1:M
        x = X(m,:);
        dxdt = diff(x, 1);
        d2xdt2 = diff(x, 2);
        D1 = [D1; dxdt];
        D2 = [D2; d2xdt2];
    end
   
    D  = fcn_featureStats(X);
    D1 = fcn_featureStats(D1);
    D2 = fcn_featureStats(D2);
    
    featureSet2 = [SC C D D1 D2];
end
        
        
        
        
        
    
   
 
 