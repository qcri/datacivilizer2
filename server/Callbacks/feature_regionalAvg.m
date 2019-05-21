function Y = feature_regionalAvg(X)

X_R1 = mean(X(1:4, :), 1);
X_R2 = mean(X(5:8, :), 1);
X_R3 = mean(X(9:12, :), 1);
X_R4 = mean(X(13:16, :), 1);
% X_R5 = mean(X(17:18, :), 1);

% Y = [X_R1; X_R2; X_R3;X_R4;X_R5];
Y = [X_R1; X_R2; X_R3;X_R4];