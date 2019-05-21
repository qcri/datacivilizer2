function [featureArray, isOutlier, timings] = fcn_computeAllFeatures(data, Fs, A, Sdata, sfreqs)
        
        % L-bipolar %
        data_bi = fcn_LBipolar(data);
        
        % para on sliding windows %
        seg_len = Fs*2;           % 2 sec per segment %
        win_len = 14*Fs;          % longest window size - 14sec %
        data_len = size(data, 2); % data size in time [pts] %

        nWin = floor((data_len - (win_len-seg_len))/seg_len) - 1; % -1 due to spectrogram zero pads in the end %

       
        featureArray =[];
        isOutlier = zeros(nWin, 1);
        timings = zeros(nWin, 4);
        thr = 2; % arifact thr on active channels %
 
        % loop for each 2-sec seg centered 14-sec window %
        for i = 1:nWin
            to = (i-1)*seg_len+1;    % [pts]   1
            t1 = to+win_len-1;       % [pts]   2800
            to_s = round(to/Fs) + 1; % [sec]   1
            t1_s = round(t1/Fs);     % [sec]   14

            timings(i,:) = [to, t1, to_s, t1_s];

            aa = A(to:t1);

            if ~isempty(find(aa>=thr, 1))    % artifacts
                 
                isOutlier(i) = 1;
                featureArray = [featureArray; NaN(1, 1188)];
                
            else % compute features %
                
                % Set 1 - 592 old feature set %
                eeg_seg = data_bi(:, to:t1);
                clear spe_seg
                for j = 1:4
                    spe_seg{j, 1} = Sdata{j, 2}(:, to_s:t1_s);
                end
                featureSeto = fcn_featureSeto(eeg_seg,spe_seg,sfreqs, Fs);
                
                % Set 2 - Network and BSI feature set %
                seg = data(:, to:t1);
                featureSet1 = fcn_bsiFeatures(seg, Fs);

                % Set 3 - Kaggle feature set %
                featureSet2 = fcn_kaggleFeatures(seg, Fs);
                featureArray = [featureArray; [featureSeto, featureSet1, featureSet2]];
                

            end     
        end
    end
