from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'os_mini'

def format_sequence(sequence):
    return ' -> '.join([f'lane{i + 1}' for i in sequence])

def initialize_resources(number_of_lanes, number_of_traffic_lights, system_available_resources, max_claim, allocation):
    need = [[0] * number_of_traffic_lights for _ in range(number_of_lanes)]
    for i in range(number_of_lanes):
        for j in range(number_of_traffic_lights):
            need[i][j] = max_claim[i][j] - allocation[i][j]
    available = system_available_resources[:]

    return need, available

def request_extra(number_of_lanes, number_of_traffic_lights, need, available, allocation, max_claim, request):
    lane_number = int(request.form['lane_number']) - 1
    request_input = request.form['extra_resources']
    request = list(map(int, request_input.split()))

    if all(request[j] <= need[lane_number][j] for j in range(number_of_traffic_lights)) and all(request[j] <= available[j] for j in range(number_of_traffic_lights)):
        for j in range(number_of_traffic_lights):
            need[lane_number][j] -= request[j]
            available[j] -= request[j]
            allocation[lane_number][j] += request[j]

        return is_safe(number_of_lanes, number_of_traffic_lights, need, available, allocation, max_claim)
    else:
        return []

def is_safe(number_of_lanes, number_of_traffic_lights, need, available, allocation, max_claim):
    safe_sequence = []
    finished_boolean_track = [False] * number_of_lanes
    temp_available = available[:]

    for _ in range(number_of_lanes):
        for process in range(number_of_lanes):
            if not finished_boolean_track[process] and all(need[process][j] <= available[j] for j in range(number_of_traffic_lights)):
                for j in range(number_of_traffic_lights):
                    temp_available[j] += allocation[process][j]
                finished_boolean_track[process] = True
                safe_sequence.append(process)
                available = temp_available

    if all(finished_boolean_track):
        return safe_sequence
    else:
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process_input', methods=['POST'])
def process_input():
    if request.method == 'POST':
        number_of_lanes = int(request.form['number_of_lanes'])
        number_of_traffic_lights = int(request.form['number_of_traffic_lights'])
        system_available_resources = list(map(int, request.form['system_available_resources'].split()))
        max_claim = [list(map(int, row.split())) for row in request.form['max_claim'].split('\n')]
        allocation = [list(map(int, row.split())) for row in request.form['allocation'].split('\n')]

        need, available = initialize_resources(number_of_lanes, number_of_traffic_lights, system_available_resources, max_claim, allocation)

        session['number_of_lanes'] = number_of_lanes
        session['number_of_traffic_lights'] = number_of_traffic_lights
        session['system_available_resources'] = system_available_resources
        session['max_claim'] = max_claim
        session['allocation'] = allocation
        session['need'] = need
        session['available'] = available

        return redirect(url_for('request_resources'))

@app.route('/request_resources', methods=['POST', 'GET'])
def request_resources():
    if request.method == 'POST':
        request_resources_option = request.form.get('request_resources')
        if request_resources_option == 'yes':
            result = request_extra(session['number_of_lanes'], session['number_of_traffic_lights'], session['need'], session['available'], session['allocation'], session['max_claim'], request)
            results = format_sequence(result)
        else:
            result = is_safe(session['number_of_lanes'], session['number_of_traffic_lights'], session['need'], session['available'], session['allocation'], session['max_claim'])
            results = format_sequence(result)

        if not result:
            results = "Request denied"

        session['results'] = results

        return redirect(url_for('result'))

    return render_template('land.html')

@app.route('/result')
def result():
    if 'results' in session:
        formatted_results = session['results']
        return render_template('result.html', results=formatted_results)
    else:
        return "No safe sequence is generated"

if __name__ == '__main__':
    app.run(debug=True)
