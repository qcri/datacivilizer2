function [Sdata, stimes, sfreqs] = fcn_computeSpec(data_bi, params)

    label_bi = {'Fp1-F7';'F7-T3';'T3-T5';'T5-O1';...
                'Fp2-F8';'F8-T4';'T4-T6';'T6-O2';...
                'Fp1-F3';'F3-C3';'C3-P3';'P3-O1';...
                'Fp2-F4';'F4-C4';'C4-P4';'P4-O2';...
                'Fz-Cz';'Cz-Pz'}; 

    ROInickname={'LL','RL','LP','RP'};
    spec_bi = cell(size(data_bi,1)-2,4);

    for k=1:size(data_bi,1)-2 
        [S,stimes,sfreqs]=mtspecgram_jj(data_bi(k,:)',params,params.movingwin,1); 
        spec_bi{k,1} = label_bi{k};
        spec_bi{k,2} = S';
        spec_bi{k,3} = stimes;
        spec_bi{k,4} = sfreqs;  
    end

    % compute regional average %
    Sdata = cell(4, 2);
    for k = 1:4
        S = zeros(size(spec_bi{1,2}));
        for kk = 1:4
            kkk = (k-1)*4+kk;
            S = S + spec_bi{kkk,2};
        end

        Sdata{k,1} = ROInickname{k};
        Sdata{k,2} = S/4;
    end
end
        