
import dill
import numpy as np
from scipy.interpolate import interp1d

with open('Dolgoprudnyj.dump', 'rb') as dump:
    meteosonde_data = dill.load(dump)

max_km = 21
grid = np.linspace(0.187, 15, 1000)

DATA = {}
for key in meteosonde_data.keys():
    T, P, rel, alt = meteosonde_data[key]

    if np.max(alt) < 15:
        continue

    T, P, rel, alt = T[alt < max_km], P[alt < max_km], rel[alt < max_km], alt[alt < max_km]

    try:
        fT, fP, frel = interp1d(alt, T), interp1d(alt, P), interp1d(alt, rel)

        T_grid, P_grid, rel_grid = fT(grid), fP(grid), frel(grid)

    except ValueError:
        continue

    DATA[key] = (T_grid, P_grid, rel_grid, grid)

print('Было {}'.format(len(list(meteosonde_data.keys()))))
print('Стало {}'.format(len(list(DATA.keys()))))

with open('Dolgoprudnyj_gridded.dump', 'wb') as dump:
    dill.dump(DATA, dump, recurse=True)
