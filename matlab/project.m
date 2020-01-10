close all
clear all
clc

S=load("data.mat");

data=S.data;
% a=data{57,6};
% b=a;
% c=b(1,1);
% d=b(1,2);
S=sparse(zeros(size(data,2)+4096));

for i = 1: length(data)
     a=data{i,6};     
     for j= 1:size(a,1)
         color=a(j,1);
         weight=a(j,2);
         S(color,i+4096)=weight;
         S(i+4096,color)=weight;
     end
end

figure(1)
spy(S)
