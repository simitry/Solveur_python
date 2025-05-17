from flask import Flask, render_template, request, redirect, url_for
import numpy as np

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
        x1 = request.form.get("x1")
        x2 = request.form.get("x2")
        x3 = request.form.get("x3")

        # Convert to floats and negate for Z row
        z_row = [
            '1',                         # Z column
            str(-float(x1 or 0)),        # x1
            str(-float(x2 or 0)),        # x2
            str(-float(x3 or 0)),        # x3
        ]

        # Constraints
        cx1 = request.form.getlist("cx1")
        cx2 = request.form.getlist("cx2")
        cx3 = request.form.getlist("cx3")
        rhs = request.form.getlist("rhs")
        num_constraints = len(cx1)

        # Add zeroed slack variables to Z row
        z_row += ['0'] * num_constraints  # Slack vars
        z_row.append('0')  # RHS for Z

        # Constraint rows
        table_rows = [z_row]  # Start with Z row

        for i in range(num_constraints):
            row = [
                '0',                  # Z column for constraints
                cx1[i],
                cx2[i],
                cx3[i],
            ]
            # Identity matrix for slack variables
            row += ['1' if j == i else '0' for j in range(num_constraints)]
            row.append(rhs[i])
            table_rows.append(row)

        headers = ['Z', 'x1', 'x2', 'x3'] + [f"e{j+1}" for j in range(num_constraints)] + ['RHS']

        return render_template('max.html', headers=headers, rows=table_rows)

        done = False
        while not done:
            tableau, done = simplex_iteration(tableau)

    return render_template('max.html')



@app.route('/min')
def min_route():
    return render_template('min.html')


def simplex_iteration(tableau):
    tableau = np.array(tableau, dtype=float)
    z_row = tableau[0, 1:-1]
    if all(c >= 0 for c in z_row):
        return tableau.tolist(), True

    pivot_col = np.argmin(z_row) + 1

    ratios = []
    for row in tableau[1:]:
        val = row[pivot_col]
        rhs = row[-1]
        if val > 0:
            ratios.append(rhs / val)
        else:
            ratios.append(np.inf)

    pivot_row_index = np.argmin(ratios) + 1

    pivot_element = tableau[pivot_row_index][pivot_col]
    tableau[pivot_row_index] = tableau[pivot_row_index] / pivot_element

    for i in range(len(tableau)):
        if i != pivot_row_index:
            row_factor = tableau[i][pivot_col]
            tableau[i] -= row_factor * tableau[pivot_row_index]

    return tableau.tolist(), False


if __name__ == '__main__':
    app.run(debug=True)
