temp1 = list(range(100))
temp2 = [i * 2 for i in range(50)]

temp1 = [1,2,3,4]
temp2 = [3,4,5,6]

s = set(temp2)
new_list = [x for x in temp1 if x not in s] + [x for x in temp2 if x not in set(temp1)]

print(temp1)
print(temp2)
print(new_list)