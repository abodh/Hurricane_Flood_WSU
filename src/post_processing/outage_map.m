D = dir;
all_probab = [];
for folders = 6:length(D)
    currD = D(folders).name;
    probab = csvread(strcat(currD,"\overall_outage.csv"));
    max_probab = max(probab);
    all_probab = [all_probab;max_probab];
end

counter = sum(all_probab>0);
%%
figure('color',[1,1,1], 'position', [100, 100, 1200, 1200])
[totalData,str,raw] = xlsread('storms_name.csv');
for i =1:29
    subplot(5,6,i)
    plot(all_probab(i,:))
    title(strcat("track ",num2str(i)))
%     xlabel('line idxs')
%     ylabel('outage probability')
    title(str{i})
    axis tight
    hold on
end
    