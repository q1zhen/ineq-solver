from sympy import *
from sympy.parsing.sympy_parser import T
from flask import Flask, render_template, request, jsonify

C = {
	"pi": {
		"ex": lambda x, n, p: ( x**n * (1-x)**n * (p[0] + p[1]*x + p[2]*x**2) ) / ( 1 + x**2 ),
		"inner": lambda x, n, p: p[0] + p[1]*x + p[2]*x**2,
	},
	"e": {
		"ex": lambda x, n, p: x**n * (1 - x)**n * (p[0] + p[1]*x) * E**x,
		"inner": lambda x, n, p: p[0] + p[1]*x,
	}
}

def above0(inner, n, params, prec=1000):
	for i in range(0, prec):
		x = i / prec
		if inner(x, n, params) <= 0:
			return False
	return True

def getEq(ex, n, params, collects):
	x = symbols("x")
	r = collect(simplify(integrate(ex(x, n, params), (x, 0, 1))).expand(), collects, evaluate=False)
	return {
		str(key): dict(sorted({
			str(k): str(v) for k, v in collect(value, params, evaluate=False).items()
		}.items())) for key, value in r.items()
	}

# print(getEq(C["pi"]["ex"], [1, a, b, c], [a, b, c], ["log(2)", "pi"]))

def generate(ex, inner, params, desired):
	collects = [i for i in desired if i != "1"]
	for i in range(100):
		eqs = getEq(ex, i, params, collects)
		matrix = [
			[
				eqs[k].get(str(e)) if eqs[k].get(str(e)) != None else 0
				for e in params
			] + [v]
			for k, v in desired.items()
		]
		solution = solve_linear_system(Matrix(matrix), *params)
		if above0(inner, i, list(solution.values())):
			return i, solution

def main(mode, value):
	global C
	if mode == "pi":
		a, b, c, x = symbols("a b c x")
		v = parse_expr(value, transformations=T[:])
		piGreater = N(pi) > N(v)
		n, sol = generate(C["pi"]["ex"], C["pi"]["inner"], [a, b, c], {
			"log(2)": 0,
			"pi": 1 if piGreater else -1,
			"1": -v if piGreater else v
		})
		r = simplify(C["pi"]["ex"](x, n, list(sol.values())))
		return " ".join([
			"\\int_0^1", latex(r), "\\textrm{d} x =",
			f"\\pi - {latex(parse_expr(value))}" if piGreater else f"{latex(parse_expr(value))} - \\pi",
			"> 0"
		])
	elif mode == "e":
		a, b, x = symbols("a b x")
		v = parse_expr(value, transformations=T[:])
		eGreater = N(E) > N(v)
		n, sol = generate(C["e"]["ex"], C["e"]["inner"], [a, b], {
			"E": 1 if eGreater else -1,
			"1": -v if eGreater else v
		})
		r = simplify(C["e"]["ex"](x, n, list(sol.values())))
		return " ".join([
			"\\int_0^1", latex(r), "\\textrm{d} x =",
			f"e - {latex(parse_expr(value))}" if eGreater else f"{latex(parse_expr(value))} - e",
			"> 0"
		])


app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
	user_input = request.form['input_box']
	mode = request.form['mode']
	try:
		result = main(mode, str(user_input))
	except Exception as e:
		result = "ERROR"
	return jsonify(result=result)

if __name__ == '__main__':
    app.run(debug=True)

