from flask import Flask, render_template, request, session
import ahpy
import secrets
import string

def generate_secret_key(length=24):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

app = Flask(__name__)
app.secret_key = generate_secret_key()

def get_criteria():
    return ["Playerbase", "Market Size", "Policy", "Competitors"]


def perform_calculation(pairwise_comparisons):
    # criteria_weights = {}
    criteria = get_criteria()

    # Construct criteria comparisons
    criteria_comparisons = {
        ('Playerbase', 'Market Size'): 2,
        ('Playerbase', 'Policy'): 3,
        ('Playerbase', 'Competitors'): 5,
        ('Market Size', 'Policy'): 1/4,
        ('Market Size', 'Competitors'): 1/3,
        ('Policy', 'Competitors'): 2
    }

    criteria_comparison = ahpy.Compare('Criteria', criteria_comparisons, precision=3, random_index='saaty')

    criteria_objects = []
    for criterion in criteria:
        comparison = ahpy.Compare(criterion, pairwise_comparisons[criterion], precision=3, random_index='saaty')
        criteria_objects.append(comparison)

    print('DEBUGS___=', criteria_objects)
    criteria_comparison.add_children(criteria_objects)


    return criteria_comparison.target_weights

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    num_alternatives = int(request.form.get("num_alternatives"))
    alternatives = [request.form.get(f"alternative{i+1}") for i in range(num_alternatives)]
    criteria = get_criteria()
    session['alternatives'] = alternatives
    print(alternatives)
    return render_template('process.html', criteria=criteria, alternatives=alternatives, num_alternatives=num_alternatives)

@app.route('/calculate', methods=['POST'])
def calculate():
    pairwise_comparisons = {}
    criteria = get_criteria()

    alternatives = session.get('alternatives')
    weights = request.form.to_dict()
    print(f'WEIGHTSSS = {weights}')

    for criterion in criteria:
        pairwise_comparisons[criterion] = {}
        for i in range(len(alternatives)):
            for j in range(i + 1, len(alternatives)):
                key = f"{criterion}_{i}_{j}_value"
                alt_i = alternatives[i]
                alt_j = alternatives[j]
                if f"{criterion}_{i}_{j}_value" in weights:
                    pairwise_comparisons[criterion][(alt_i, alt_j)] = int(weights[f"{criterion}_{i}_{j}_value"])
                elif f"{criterion}_{j}_{i}_value" in weights:
                    pairwise_comparisons[criterion][(alt_i, alt_j)] = 1 / int(weights[f"{criterion}_{j}_{i}_value"])
                else:
                    # Handle the case where the key is not found
                    # You may choose to set a default value or take appropriate action
                    pairwise_comparisons[criterion][(alt_i, alt_j)] = 1  # Default value

    

    # Calculate weights
    ranked = perform_calculation(pairwise_comparisons)
    print(f'rankssss{ranked}')

    return render_template('results.html', results=ranked, pairwise_comparisons=pairwise_comparisons)




if __name__ == '__main__':
    app.run(debug=True)