%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% - detect changepoints;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_changePoints(arg1, arg2)


fileName = arg1;
 
tmp = load([pwd, '/Data/', fileName]);

Sdata = cell2mat(flipud(tmp.Sdata(:, 2)));
stimes = tmp.stimes;
sfreqs = tmp.sfreqs;
col = [-10 25];

% step1. Compute total power %
P  = sum(pow2db(Sdata+eps), 1)/4;

% step2. Smooth %
P_ = smooth(P, 5,'sgolay');

% step3. Clip at 1000dB %
P_(P_>1000) = 1000;
P_(P_<-1000) = -1000;
thr = .5;

[icp, ~] = findchangepts(P_, 'Statistic', 'mean','MinThreshold',thr*var(P_));

% step4. Display %
verbose = 1;
if verbose 
    close all
    f = figure('units','normalized','outerposition',[0 0 1 1]);
    subplot(6, 1, 1:5)
    colormap jet
    imagesc(stimes, sfreqs, pow2db(Sdata), col);    
    axis(gca,'xy');
    xlim([2500 3400])
    set(gca, 'xticklabels', [], 'yticklabels', [])

    subplot(6, 1,  6)
    title(['1:',num2str(round(length(stimes)/length(icp)))])

    hold on
    plot(stimes, P, 'b')
    plot(stimes, P_, 'm')

    for i = 1:length(icp)
        x_ = stimes(icp(i));
        plot([x_, x_], [-1000 1000], 'g')
    end
    xlim([2500 3400])
    ylim([-1000 1000])
    hold off
    box on

    saveas(f, arg2);

end

end



