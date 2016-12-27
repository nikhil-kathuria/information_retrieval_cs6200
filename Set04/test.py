
import numpy as np
import math
import random


P = np.array([[1 / 6, 2 / 3, 1 / 6],
              [5 / 12, 1 / 6, 5 / 12],
              [1 / 6, 2 / 3, 1 / 6]])


# Now calculate Eigen Vector
v, V = np.linalg.eig(P.T)
left_vec = V[:, 0].T
# Get the vector sorted
# left_vec = V[:, v.argmax()]
# Normailize (i.e sum of all ranks = 1)
left_vec /= left_vec.sum()
# print(left_vec)

a = float(0.123213)
b = float(0.123)
print("{0:.4f}".format(a))
print("{0:.4f}".format(b))

ddict = {1: 3, 2: 3, 3: 6, 4: 9}
keys = list(ddict.keys())

val = random.choice(keys)
keys.remove(val)
# print(keys)

'''
list1 = [1, 2, 3, 4]
list2 = [4, 3, 2, 1]
zipped = zip(list1, list2)
for val in zipped:
	print(val[0])
'''

d1 = "2015-04-17"
d2 = "2015-04-17"

 

def datematch(d1, d2):
    '''Assuming all date value obey YYYY{delim}MM{delim}DD format
    Check YYYY, MM, and corresponding DD value match between d1 and d2'''
    if d1[0:4] == d2[0:4] and d1[5:7] == d2[5:7] and d1[8:10] == d2[8:10]:
        True
        print("True")
    else:
        False
        print("False")

datematch(d1, d2)