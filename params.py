from sympy import *
import tqdm
import json

x = symbols("x")
a, b, c = symbols("a b c")

ex = lambda n: ( x**n * (1-x)**n * (a + b*x + c*x**2) ) / ( 1 + x**2 )
params = {}

for n in tqdm.tqdm(range(1, 21)):
	r = collect(simplify(integrate(ex(n), (x, 0, 1))).expand(), [pi, log(2)], evaluate=False)
	params[str(n)] = {str(key): {
		str(k): str(v) for k, v in collect(value, [a, b, c], evaluate=False).items()
	} for key, value in r.items()}

with open("params_pi.json", "w+") as f:
	json.dump(params, f, indent="\t")


