from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
import database_management 
from data_pipeline import data_processing, analyze_data, plot_graph, manage_test_records
from certi_tester import certi_device

app = Flask(__name__, static_folder='dist/assets', template_folder='dist')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow CORS for Socket.IO

# Serve the build version of frontend code (REACT)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    connection_successful = database_management.verify_database_connection()
    if connection_successful:
        output = {"status": "true"}
    else:
        output = {"status": "false"}
    return output

@app.route('/api/reset-database', methods=['GET'])
@app.route('/api/initialize-database', methods=['GET'])
def reset_or_initialized_db():
    database_management.initialize_database()
    return "Database initalize successfully"


@app.route('/api/get-p-test-file-name', methods=['GET'])
def analyze():
    return analyze_data.get_penetration_test_options()
     
@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        
        file = request.files['file']
        
        if file.filename == '':
            return 'No selected file'
        
        if file:
            responseData = data_processing.data_processing(file)
            return jsonify(responseData)
        
@app.route('/api/analyze-selected-penetration-data', methods=['POST'])
def analyze_selected_penetration_data():
    data = request.json
    selected_values = data.get('selectedValues', [])
    
    # Selecting the data from the database
    all_penetration_data = analyze_data.get_penetration_data_for_selected_files(selected_values)
    # Passing the filename and the merged data for plotting
    penetration_box_plot_data = plot_graph.generate_penetration_box_plot(selected_values, all_penetration_data)
    return jsonify({'penetrationPlotComparionData': penetration_box_plot_data})

@app.route('/api/get-test-records', methods=['GET'])
def analyze_test_records():
    analyze_dataframe = analyze_data.analyze_test_records()
    return jsonify({'analyzedData': analyze_dataframe})

@app.route('/api/delete-test-records', methods=['POST'])
def delete_test_records():
    data = request.json
    selected_values = data.get('selectedValues', [])
    manage_test_records.delete_test_records(selected_values)
    return {"status": "true"}

@app.route('/api/analyse-test-records', methods=['POST'])
def analyse_test_records():
    data = request.json
    selected_values = data.get('selectedValues', [])
    test_type = data.get('testType')
    
    all_test_data = analyze_data.analyze_test_record(test_type, selected_values)
    penetration_plot_data = plot_graph.generate_analyzed_penetration_graph(all_test_data, test_type)
    resistance_plot_data = plot_graph.generate_analyzed_resistance_graph(all_test_data, test_type)
    
    return jsonify({'penetrationPlotData': penetration_plot_data, 'resistancePlotData':resistance_plot_data})

@app.route('/api/export-test-records', methods=['POST'])
def export_test_records():
    data = request.json
    selected_values = data.get('selectedValues', [])
    export_data = manage_test_records.export_test_records(selected_values)
    return jsonify(export_data)

@app.route('/api/start-certi-tester-connection', methods=['POST'])
def certi_tester_device():
    test_meta_data = request.get_json()
    print(test_meta_data)
    # this function creates buffer, and starts reading immediatly if timer is give
    # always going to return the buffer, but only need to render it sometimes
    
    # could be with data without data
    certi_tester_output = certi_device.connect_certi_tester(test_meta_data)
    
    print("Buffer by the machine sent", certi_tester_output)
    
    return jsonify(certi_tester_output)

@socketio.on('connect')
def handle_connect():
    print("connect_certi_tester called", flush=True)
    print('Client connected')
    # Start a background task to monitor live data
    socketio.start_background_task(monitor_live_data)

def monitor_live_data():
    last_data_length = 0  # Variable to track the last emitted data length

    while True:
        if certi_device.is_reading_active:
            data = certi_device.get_live_data()

            # Emit data only if the length has changed
            if len(data) != last_data_length:  # Check if the current data length is different from the last emitted length
                if data:  # Check if data is not empty
                    print("Emitting live data:", data, flush=True)
                    socketio.emit('live_data', data)  # Emit data immediately
                else:
                    print("No live data available", flush=True)

                last_data_length = len(data)  # Update the last emitted data length

        socketio.sleep(1)  # Check for new data every second

@app.route('/api/start-timer', methods=['POST'])
def start_timer_endpoint():
    # pass the buffer, date_time to frontend ig
    start_test_parameters = request.get_json()
    print(start_test_parameters)
    # Call the function to start the timer
    print("start timer")
    buffer = certi_device.start_reading(timer=None,buffer=start_test_parameters[0], date_time=start_test_parameters[1])  
    print("Buffer by the machine sent if timer hit in the middle")
    return jsonify(buffer)


@app.route('/api/end-timer', methods=['GET'])
def stop_timer_endpoint():
    certi_device.end_reading()  # Call the function to stop the timer
    print("Buffer by the machine sent if timer hit in the middle")
    return jsonify("buffer")

if __name__ == '__main__':
    socketio.run(app, debug=True, port=7784)
    #socketio.run(app, debug=True, port=7784) 
   # socketio.run(app, host='0.0.0.0', debug=True, port=7784)
    #app.run(host='0.0.0.0', debug=True, port=7784)
