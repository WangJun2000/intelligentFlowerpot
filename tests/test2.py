'''
import math
m=-float('inf')
maxSumDict={}

def maxsum(i,array):
    if i in maxSumDict:
        return maxSumDict[i]
    if i == len(array)-1:
        maxSumDict[i]=array[i]
        return maxSumDict[i]
    maxSumDict[i]=max(array[i],maxsum(i+1,array)+array[i])
    return maxSumDict[i]
'''   
maxSumDict={}
array=[1,2,3,-10,5,-10,6,8,-20,19]


for i in range(len(array)-1,-1,-1):
    if i == len(array)-1:
        maxSumDict[i]=array[i]
    else:
        maxSumDict[i]=max(array[i],maxSumDict[i+1]+array[i])

print(max(maxSumDict.values()))
print(maxSumDict)