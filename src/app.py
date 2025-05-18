from flask import Flask, render_template, request, redirect, url_for
import numpy as np
from scipy.optimize import linprog

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_option = request.form.get('option')
        
        if selected_option == 'max':
            return redirect(url_for('max_route'))
        elif selected_option == 'min':
            return redirect(url_for('min_route'))
        
    return render_template('index.html')

@app.route('/max', methods=['POST', 'GET'])
def max_route():
    if request.method == 'POST':
        # Objective function input (Z)
        x1 = float(request.form.get("x1") or 0)
        x2 = float(request.form.get("x2") or 0)
        x3 = float(request.form.get("x3") or 0)

        # For maximization, we negate the objective coefficients for SciPy (which minimizes by default)
        c = [-x1, -x2, -x3]
        
        # Constraints
        cx1 = [float(val) for val in request.form.getlist("cx1")]
        cx2 = [float(val) for val in request.form.getlist("cx2")]
        cx3 = [float(val) for val in request.form.getlist("cx3")]
        rhs = [float(val) for val in request.form.getlist("rhs")]
        num_constraints = len(cx1)
        
        # Create constraint matrix A_ub for SciPy
        A_ub = []
        for i in range(num_constraints):
            A_ub.append([cx1[i], cx2[i], cx3[i]])
        
        # Solve using SciPy
        result = linprog(c, A_ub=A_ub, b_ub=rhs, method='highs')
        
        z_row = ['1'] + [str(-float(val)) for val in [x1, x2, x3]] + ['0'] * num_constraints + ['0']
        table_rows = [z_row]
        
        for i in range(num_constraints):
            row = ['0', str(cx1[i]), str(cx2[i]), str(cx3[i])]
            row += ['1' if j == i else '0' for j in range(num_constraints)]
            row.append(str(rhs[i]))
            table_rows.append(row)
        
        headers = ['Z', 'x1', 'x2', 'x3'] + [f"e{j+1}" for j in range(num_constraints)] + ['RHS']
        
        optimal_solution = {
            'x1': result.x[0],
            'x2': result.x[1],
            'x3': result.x[2],
            'objective_value': -result.fun,
            'success': result.success,
            'status': result.message
        }
        
        return render_template('max.html', headers=headers, rows=table_rows, solution=optimal_solution)

    return render_template('max.html')

@app.route('/min')
def min_route():
    return render_template('min.html')


if __name__ == '__main__':
    app.run(debug=True)
