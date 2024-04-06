from flask import Flask, render_template, request, session,  redirect, url_for
import ahpy
import secrets
import string

def generate_secret_key(length=24):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

app = Flask(__name__)
app.secret_key = generate_secret_key()

def get_criteria():
    return ["Availability Joki",
            "Playerbase", 
            "Market Size",
            "Policy", 
            "Competitors",
            "Underlying Cost",
            "Price Competition",
            "Category Joki",
            "Skill Ceiling"]
    # return ['Playerbase','Market Size','Policy','Competitors']

def check_consistency(pairwise_comparisons):
    ratios = {}
    for criterion, comparisons in pairwise_comparisons.items():
        comparison = ahpy.Compare(criterion, comparisons, precision=3, random_index='saaty')
        consistency_ratio = comparison.consistency_ratio
        ratios[criterion] = consistency_ratio
        if consistency_ratio > 0.1:
            return True, ratios
    return False, ratios


def perform_calculation(pairwise_comparisons):
    # criteria_weights = {}
    criteria = get_criteria()

    # Construct criteria comparisons
    criteria_comparisons = {
        ('Playerbase', 'Market Size'): 1,
        ('Playerbase', 'Policy'): 3,
        ('Playerbase', 'Competitors'): 3,
        ('Playerbase', 'Availability Joki'): 5,
        ('Playerbase', 'Underlying Cost'): 3,
        ('Playerbase', 'Price Competition'): 5,
        ('Playerbase', 'Category Joki'): 3,
        ('Playerbase', 'Skill Ceiling'): 5,

        ('Market Size', 'Policy'): 2,
        ('Market Size', 'Competitors'): 3,
        ('Market Size', 'Availability Joki'): 7,
        ('Market Size', 'Underlying Cost'): 7,
        ('Market Size', 'Price Competition'): 7,
        ('Market Size', 'Category Joki'): 7,
        ('Market Size', 'Skill Ceiling'): 7,

        ('Policy', 'Competitiors'): 2,
        ('Policy', 'Availability Joki'): 5,
        ('Policy', 'Underlying Cost'): 3,
        ('Policy', 'Price Competition'): 3,
        ('Policy', 'Category Joki'): 3,
        ('Policy', 'Skill Ceiling'): 5,

        ('Competitors', 'Availability Joki'): 5,
        ('Competitors', 'Underlying Cost'): 3,
        ('Competitors', 'Price Competition'): 3,
        ('Competitors', 'Category Joki'): 3,
        ('Competitors', 'Skill Ceiling'): 5,

        ('Availability Joki', 'Underlying Cost'): 3,
        ('Availability Joki', 'Price Competition'): 2,
        ('Availability Joki', 'Category Joki'): 3,
        ('Availability Joki', 'Skill Ceiling'): 1,

        ('Underlying Cost', 'Price Competition'): 1,
        ('Underlying Cost', 'Category Joki'): 1,
        ('Underlying Cost', 'Skill Ceiling'): 3,

        ('Price Competition', 'Category Joki'): 2,
        ('Price Competition', 'Skill Ceiling'): 3,

        ('Category Joki', 'Skill Ceiling'): 3,
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
                    pairwise_comparisons[criterion][(alt_i, alt_j)] = float(weights[f"{criterion}_{i}_{j}_value"])
                elif f"{criterion}_{j}_{i}_value" in weights:
                    pairwise_comparisons[criterion][(alt_i, alt_j)] = 1 / float(weights[f"{criterion}_{j}_{i}_value"])
                else:
                    # Handle the case where the key is not found
                    # You may choose to set a default value or take appropriate action
                    pairwise_comparisons[criterion][(alt_i, alt_j)] = 1  # Default value

    # Execute consistency check
    consistency_check_passed, consistency_ratios = check_consistency(pairwise_comparisons)

    if consistency_check_passed:
        # Redirect to invalid.html if consistency check fails
        # return redirect(url_for('invalid', consistency_ratios=consistency_ratios))
        return render_template('invalid.html', consistency_ratios=consistency_ratios)
    else:
        # Calculate weights and render results.html
        ranked = perform_calculation(pairwise_comparisons)
        return render_template('results.html', results=ranked, pairwise_comparisons=pairwise_comparisons, consistency_ratios=consistency_ratios)



# @app.route('/invalid')
# def invalid():
#     return render_template('invalid.html')

if __name__ == '__main__':
    app.run(debug=True)