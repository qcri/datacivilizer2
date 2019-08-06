%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% - detect changepoints;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = mod_changePoints(in_file, out_file, thr)

% Step1 - read data %
tmp = load([pwd, '/Data/', in_file]);

Sdata = cell2mat(flipud(tmp.Sdata(:, 2)));
stimes = tmp.stimes;
sfreqs = tmp.sfreqs;
col = [-10 25];

% step2. Compute total power %
P  = sum(pow2db(Sdata+eps), 1)/4;

% step3. Smooth %
P_ = smooth(P, 5,'sgolay');

% step4. Clip at 1000dB %
P_(P_>1000) = 1000;
P_(P_<-1000) = -1000;
% thr = .5; %

[icp, ~] = findchangepts(P_, 'Statistic', 'mean','MinThreshold',thr*var(P_));

% step5. Display %
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

    saveas(f, out_file);

end

end



