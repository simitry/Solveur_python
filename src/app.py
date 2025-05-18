from flask import Flask, render_template, request, redirect, url_for
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
        elif selected_option == 'duality':
            return redirect(url_for('duality_route'))
        
    return render_template('index.html')

@app.route('/max', methods=['POST', 'GET'])
def max_route():
    if request.method == 'POST':
        # Objective function input (Z) - 4 variables
        x1 = float(request.form.get("x1") or 0)
        x2 = float(request.form.get("x2") or 0)
        x3 = float(request.form.get("x3") or 0)
        x4 = float(request.form.get("x4") or 0)

        # For maximization, negate all 4 objective coefficients
        c = [-x1, -x2, -x3, -x4]
        
        # Constraints - 4 coefficients per constraint
        cx1 = [float(val) for val in request.form.getlist("cx1")]
        cx2 = [float(val) for val in request.form.getlist("cx2")]
        cx3 = [float(val) for val in request.form.getlist("cx3")]
        cx4 = [float(val) for val in request.form.getlist("cx4")]
        rhs = [float(val) for val in request.form.getlist("rhs")]
        num_constraints = len(cx1)
        
        # Create constraint matrix A_ub with 4 columns
        A_ub = []
        for i in range(num_constraints):
            A_ub.append([cx1[i], cx2[i], cx3[i], cx4[i]])
        
        # Solve using SciPy with all 4 variables
        result = linprog(c, A_ub=A_ub, b_ub=rhs, method='highs')
        
        # Prepare tableau rows - include all 4 variables
        z_row = ['1'] + [str(-float(val)) for val in [x1, x2, x3, x4]] + ['0'] * num_constraints + ['0']
        table_rows = [z_row]
        
        for i in range(num_constraints):
            row = ['0', str(cx1[i]), str(cx2[i]), str(cx3[i]), str(cx4[i])]
            row += ['1' if j == i else '0' for j in range(num_constraints)]
            row.append(str(rhs[i]))
            table_rows.append(row)
        
        headers = ['Z', 'x1', 'x2', 'x3', 'x4'] + [f"e{j+1}" for j in range(num_constraints)] + ['RHS']
        
        optimal_solution = {
            'x1': result.x[0] if result.x is not None and len(result.x) > 0 else 0,
            'x2': result.x[1] if result.x is not None and len(result.x) > 1 else 0,
            'x3': result.x[2] if result.x is not None and len(result.x) > 2 else 0,
            'x4': result.x[3] if result.x is not None and len(result.x) > 3 else 0,
            'objective_value': -result.fun if result.success else 0,
            'success': result.success,
            'status': result.message
        }
        
        return render_template('max.html', headers=headers, rows=table_rows, solution=optimal_solution)

    return render_template('max.html')

@app.route('/min', methods=['POST', 'GET'])
def min_route():
    if request.method == 'POST':
        # Objective function input (Z)
        x1 = float(request.form.get("x1") or 0)
        x2 = float(request.form.get("x2") or 0)
        x3 = float(request.form.get("x3") or 0)

        # For minimization, we can use the coefficients directly
        c = [x1, x2, x3]
        
        # Constraints (should be >= for minimization)
        cx1 = [float(val) for val in request.form.getlist("cx1")]
        cx2 = [float(val) for val in request.form.getlist("cx2")]
        cx3 = [float(val) for val in request.form.getlist("cx3")]
        rhs = [float(val) for val in request.form.getlist("rhs")]
        num_constraints = len(cx1)
        
        # Create constraint matrix A_ub for SciPy
        A_ub = []
        for i in range(num_constraints):
            A_ub.append([-cx1[i], -cx2[i], -cx3[i]])  # Negate for >= constraints
        
        # Solve using SciPy
        result = linprog(c, A_ub=A_ub, b_ub=[-r for r in rhs], method='highs')
        
        optimal_solution = {
            'x1': result.x[0],
            'x2': result.x[1],
            'x3': result.x[2],
            'x4': result.x[3],
            'objective_value': result.fun,
            'success': result.success,
            'status': result.message
        }
        
        return render_template('min.html', solution=optimal_solution)

    return render_template('min.html')

@app.route('/duality', methods=['POST', 'GET'])
def duality_route():
    if request.method == 'POST':
        # Get the primal problem (assume it's a maximization problem)
        primal_obj = [
            float(request.form.get("x1") or 0),
            float(request.form.get("x2") or 0),
            float(request.form.get("x3") or 0),
            float(request.form.get("x4") or 0)
        ]
        
        # Get constraints
        cx1 = [float(val) for val in request.form.getlist("cx1")]
        cx2 = [float(val) for val in request.form.getlist("cx2")]
        cx3 = [float(val) for val in request.form.getlist("cx3")]
        cx4 = [float(val) for val in request.form.getlist("cx4")]
        rhs = [float(val) for val in request.form.getlist("rhs")]
        num_constraints = len(cx1)
        
        # Construct the dual problem
        # The dual of a maximization problem is a minimization problem
        dual_obj = rhs  # RHS becomes objective in dual
        
        # Constraints in dual come from the primal objective coefficients
        # Each primal variable becomes a dual constraint
        dual_constraints = []
        for i in range(4):  # For x1, x2, x3
            constraint = []
            for j in range(num_constraints):
                # Transpose the constraint matrix
                if i == 0:
                    constraint.append(cx1[j])
                elif i == 1:
                    constraint.append(cx2[j])
                elif i == 2:
                    constraint.append(cx3[j])
                elif i == 3:
                    constraint.append(cx4[j])
            dual_constraints.append(constraint)
        
        # Right-hand side of dual constraints comes from primal objective
        dual_rhs = primal_obj
        
        # Solve the dual problem (minimization)
        # Since dual is minimization, we can use coefficients directly
        result = linprog(
            dual_obj,
            A_ub=[[-x for x in const] for const in dual_constraints],  # Negate for >=
            b_ub=[-x for x in dual_rhs],  # Negate for >=
            method='highs'
        )
        
        # Also solve the primal for comparison
        primal_result = linprog(
            [-x for x in primal_obj],  # Negate for maximization
            A_ub=[[cx1[j], cx2[j], cx3[j], cx4[j]] for j in range(num_constraints)],
            b_ub=rhs,
            method='highs'
        )
        
        # Prepare data for display
        duality_data = {
            'primal': {
                'objective': primal_obj,
                'constraints': [[cx1[j], cx2[j], cx3[j], cx4[j]] for j in range(num_constraints)],
                'rhs': rhs,
                'solution': {
                    'x': primal_result.x,
                    'objective_value': -primal_result.fun,
                    'status': primal_result.message
                }
            },
            'dual': {
                'objective': dual_obj,
                'constraints': dual_constraints,
                'rhs': dual_rhs,
                'solution': {
                    'x': result.x,
                    'objective_value': result.fun,
                    'status': result.message
                }
            }
        }
        
        return render_template('duality.html', duality_data=duality_data)
    
    return render_template('duality.html')

if __name__ == '__main__':
    app.run(debug=True)