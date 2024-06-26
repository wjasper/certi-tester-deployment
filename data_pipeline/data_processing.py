from . import analyze_data, data_insertion, file_parser, plot_graph

def data_processing(file):
    """
    Input:- Takes the txt file uploaded by the user.
    Output:- Dictionary of response containing the Table data, Plot data, and Analyzed data
    """
    
    meta_data, df = file_parser.file_parse(file)

    #Checking if the sample with specific sample_tag exists or not, if it doesn't then we add it.
    sample_tag = data_insertion.insert_test_record(meta_data, df, file.filename)
    penetration_data = file_parser.df_data_formatting(df)
    resistance_time_plot_data = plot_graph.generate_plotly_figure(df,'Resistance (mm of H2O)')
    
    response_data = {
        'metaData': meta_data,
        'tableData': penetration_data,
        'resistancePlotData': resistance_time_plot_data
    }
    
    if meta_data[0] == "G":
        response_data.update({
            'analyze_current_penetration_data': None,
            'penetrationPlotData': 0,
            })
                
    else:
        penetration_time_plot_data = plot_graph.generate_plotly_figure(df,'Penetration (%)')
        #We pass the sample_tag ID to get analysis of the current file
        analyze_current_penetration_data = analyze_data.analyze_current_penetration_data(meta_data ,sample_tag)
        response_data.update({
                'penetrationPlotData': penetration_time_plot_data,
                'analyze_current_penetration_data': analyze_current_penetration_data
            })
                
    return response_data
