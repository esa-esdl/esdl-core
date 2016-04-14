import timeit

import numpy as np
from cablab.resize import resize

MAIN = 'from __main__ import np, resize, a'
times = 100
N = 10

print('\nUpsampling:')
print('No\tSize\tCython')
s = 4
for i in range(N):
    a = np.arange(0, s * s, dtype=np.float64)
    a.shape = s, s
    t1 = timeit.timeit(setup=MAIN, number=times, stmt='resize(%d, %d, a, %d, %d)' % (s, s, int(s * 2.5), int(s * 2.1)))
    print('%d\t%d\t%f' % (i + 1, s, t1))
    s *= 2

print('\nDownsampling:')
print('No\tSize\tndarray\tma\tloss')
s = 4
for i in range(N):
    a = np.arange(0, s * s, dtype=np.float64)
    a.shape = s, s
    t1 = timeit.timeit(setup=MAIN, number=times, stmt='resize(%d, %d, a, %d, %d)' % (s, s, int(s / 2.5), int(s / 2.1)))

    b = np.arange(0, s * s, dtype=np.float64)
    b.shape = s, s
    mask = np.full((s, s), False, dtype=np.bool)
    mask[1:3, 1:3] = True
    b_masked = np.ma.array(b, mask=mask)
    t2 = timeit.timeit(setup='from __main__ import np, resize, b_masked', number=times,
                       stmt='resize(%d, %d, b_masked, %d, %d)' % (s, s, int(s / 2.5), int(s / 2.1)))
    print('%d\t%d\t%f\t%f\t%f' % (i + 1, s, t1, t2, t2 / t1))
    s *= 2
