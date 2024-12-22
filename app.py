from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
import database_management 
from data_pipeline import data_processing, analyze_data, plot_graph, manage_test_records
from certi_tester import certi_device as certi_device_dev
import threading
import time

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

last_known_data = None
# Function to check if the Data field has changed
def check_for_data_update():
    global last_known_data
    # Fetch the current 'Data' field from Redis
    current_data = certi_device_dev.read_live_data_from_persistent_storage()
    
    # Compare with the last known state
    if current_data != last_known_data:
        print("Data field updated!")
        print("Updated Data:", current_data)
        last_known_data = current_data
        # Emit the updated data to the frontend through WebSockets
        socketio.emit('data_update', {'data': current_data})


# Polling loop (checks every 10 seconds)
def poll_redis():
    while True:
        if certi_device_dev.is_reading_active: 
            print("checking because timer active")
            check_for_data_update()
        time.sleep(10)  
        

# Monitor certi_device.is_reading_active for changes
def monitor_timer_status():
    previous_status = None  # Store the last known status
    while True:
        current_status = certi_device_dev.is_reading_active
        if current_status != previous_status:  # If the status has changed
            socketio.emit('timer_status', {'status': current_status})  # Emit the new status
            print(f"Timer status changed to: {current_status}")
            previous_status = current_status
    
        time.sleep(1)

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    print("Timer status" + str(certi_device_dev.is_reading_active))  
    socketio.emit('timer_status', {'status':  certi_device_dev.is_reading_active})
  
# Start the monitoring thread
threading.Thread(target=monitor_timer_status, daemon=True).start()
threading.Thread(target=poll_redis, daemon=True).start()



@app.route('/api/start-reading', methods=['POST'])
def start_timer_endpoint():
    # pass the buffer, date_time to frontend ig
    socketio.emit('new_experiment_started')
    start_test_parameters = request.get_json()
    certi_device_dev.buffer_initialization(start_test_parameters)
    return jsonify("buffer")



@app.route('/api/end-reading', methods=['GET'])
def stop_timer_endpoint():
    experiment_output = certi_device_dev.end_reading()  # Call the function to stop the timer
    #experiment_output['Data'] = json.loads(experiment_output.get('Data', ''))
    print("Buffer by the machine sent if timer hit in the middle")
    print(experiment_output)
    socketio.emit('experiment_data', {'experimentOutput': experiment_output})
    return jsonify("experiment_output")

if __name__ == '__main__':
    socketio.run(app, debug=True, port=7784)
    #socketio.run(app, debug=True, port=7784) 
   # socketio.run(app, host='0.0.0.0', debug=True, port=7784)
    #app.run(host='0.0.0.0', debug=True, port=7784)
