from flask import Flask, request, jsonify, render_template
import database_management 
from data_pipeline import data_processing, analyze_data, plot_graph, manage_test_records
import socket

#MySQL credentials
HOST = 'localhost'
USER = 'root'
PASSWORD = 'c3rt1test3r'
DATABASE = 'certi_tsi'

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
        
        if file and file.filename and file.stream and file.stream.read(1) == b'':
            return {'Error': 'Empty file'}
        
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
    plot_data = plot_graph.generate_analyzed_graph(all_test_data)
    return jsonify({'plotData': plot_data})

def find_free_port():
    default_port = 7784
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('', default_port))
    except socket.error:
        sock.bind(('', 0))  
    port = sock.getsockname()[1]
    sock.close()
    return port

if __name__ == '__main__':
    port = find_free_port()
    app.run(port=port)