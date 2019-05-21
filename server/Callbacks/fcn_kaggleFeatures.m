function features = fcn_kaggleFeatures(seg, Fs)
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
        data = fcn_LBipolar(data); % L-Bipolar %
        
        featureSet1 = fcn_kaggleFeature1(data, Fs, [1 40]);
        featureSet2 = fcn_kaggleFeature2(data, Fs);
        
        features = [features [featureSet1, featureSet2]];
    end
end
 