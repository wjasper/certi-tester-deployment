from flask import Flask, request, jsonify, render_template
import database_management 
from data_pipeline import data_processing, analyze_data, plot_graph, manage_test_records
from certi_tester import certi_device

app = Flask(__name__, static_folder='dist/assets', template_folder='dist')

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


# WORKING ONLY WITH TIMER AS OF NOW
@app.route('/api/certi-tester-device', methods=['POST'])
def certi_tester_device():
    meta_data = request.get_json()
    
    buffer = certi_device.buffer_initialization(meta_data)
    
    print("Buffer by the machine sent", buffer)
    
    return jsonify(buffer)

@app.route('/api/end-timer', methods=['GET'])
def stop_timer_endpoint():
    certi_device.end_reading()  # Call the function to stop the timer
    print("Buffer by the machine sent if timer hit in the middle")
    return jsonify("buffer")


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=7784)
