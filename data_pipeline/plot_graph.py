import pandas as pd
import plotly.graph_objs as go

def generate_plotly_figure(df, column_name, test_type):
    """
    Takes the dataframe.
    Ignore the values where no timestamp is present.
    Graph is plotted using plotly.
    And is returned in json format.
    """
    df = df[df['Timestamp'] != '00-00-0000 00:00:00']
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df = df.dropna(subset=['Timestamp']).reset_index(drop=True)
    df['Minutes Passed'] = (df['Timestamp'] - df['Timestamp'].iloc[0]).dt.total_seconds() / 60

    fig = go.Figure()

    settings = {
        'Penetration (%)': {
            'range': [0, 100],
            'title': 'Penetration (%)'
        },
        'Resistance (mm of H2O)': {
            'range': [0, df[column_name].max() * 1.1],
            'title': 'Resistance (mm of H2O)'
        }
    }

    yaxis_dict = {
        'gridcolor': 'LightGray',
        'range': settings[column_name]['range']
    }

    if test_type == 'P':
        x_axis = df.index
        xaxis_title_value = 'Samples'
    else:
        x_axis = df['Minutes Passed']
        xaxis_title_value = 'Minutes Passed'

    title_value = f"{xaxis_title_value} vs {settings[column_name]['title']}"

    fig.add_trace(go.Scatter(
        x=x_axis,
        y=df[column_name],
        mode='markers+lines',
        marker=dict(symbol='circle', size=8, color='#f50057'),
        line=dict(width=2, color='#4B6888'),
    ))

    fig.update_layout(
        title=title_value,
        xaxis_title=xaxis_title_value,
        yaxis_title=column_name,
        xaxis=dict(gridcolor='LightGray'),
        yaxis=yaxis_dict,
        hovermode='closest',
    )

    return fig.to_json()


def generate_penetration_box_plot(files_array, all_penetration_data):
    fig = go.Figure()
    
    for i, data in enumerate(all_penetration_data):
        fig.add_trace(go.Box(y=data, name=files_array[i]))

    fig.update_layout(title='Penetration Data for Selected Files',
                        xaxis_title='File',
                        yaxis_title='Penetration')
    
    return fig.to_json()

def generate_analyzed_penetration_graph(all_test_data, test_type):
    
    data = all_test_data['penetration_data']
    sample_tags = all_test_data['sample_tags']
    test_time = all_test_data['test_time']
    
    max_y_value = 0 
    
    fig = go.Figure()
    
    if test_type == "P":
    
        # Plot each penetration data series
        for i, data_series in enumerate(data):
            fig.add_trace(go.Scatter(
                x=list(range(len(data_series))),
                y=data_series,
                mode='markers+lines',
                name=sample_tags[i],
                marker=dict(symbol='circle', size=5),
                line=dict(width=2),
            ))
        
        yaxis_dict = dict(gridcolor='LightGray')
        yaxis_dict['range'] = [0, 100]
        
        fig.update_layout(title='Samples vs Penetration (%)',
                            xaxis_title='Samples',
                            yaxis_title='Penetration (%)',
                            yaxis=yaxis_dict)
        
    if test_type == "L":
        for i, (data_series, time_series) in enumerate(zip(data, test_time)):
            fig.add_trace(go.Scatter(
                x=time_series,
                y=data_series,
                mode='markers+lines',
                name=sample_tags[i],
                marker=dict(symbol='circle', size=5),
                line=dict(width=2),
            ))
        
        yaxis_dict = dict(gridcolor='LightGray')
        yaxis_dict['range'] = [0, 100]
        
        fig.update_layout(title='Minutes Passed vs Penetration',
                            xaxis_title='Minutes Passed',
                            yaxis_title='Penetration',
                            yaxis=yaxis_dict)
    
       
        
    return fig.to_json()

def generate_analyzed_resistance_graph(all_test_data, test_type):

    data = all_test_data['resistance_data']
    sample_tags = all_test_data['sample_tags']
    test_time = all_test_data['test_time']
    fig = go.Figure()
    
    max_y_value = 0 
    
    if test_type == "P":
        
        # Plot each penetration data series
        for i, data_series in enumerate(data):
            max_y_value = max(max_y_value, max(data_series))  
            fig.add_trace(go.Scatter(
                x=list(range(len(data_series))),
                y=data_series,
                mode='markers+lines',
                name=sample_tags[i],
                marker=dict(symbol='circle', size=5),
                line=dict(width=2),
            ))
        
        yaxis_dict = dict(gridcolor='LightGray')
        yaxis_dict['range'] = [0, max_y_value*1.1]
        
        fig.update_layout(title='Samples vs Resistance',
                            xaxis_title='Samples',
                            yaxis_title='Resistance',
                            yaxis=yaxis_dict)
        
    if test_type == "G":
        for i, (data_series, time_series) in enumerate(zip(data, test_time)):
            max_y_value = max(max_y_value, max(data_series))  
            fig.add_trace(go.Scatter(
                x=time_series,
                y=data_series,
                mode='markers+lines',
                name=sample_tags[i],
                marker=dict(symbol='circle', size=5),
                line=dict(width=2),
            ))
        
        yaxis_dict = dict(gridcolor='LightGray')
        yaxis_dict['range'] = [0, max_y_value*1.1]
        
        fig.update_layout(title='Minutes Passed vs Resistance',
                            xaxis_title='Minutes Passed',
                            yaxis_title='Resistance',
                            yaxis=yaxis_dict)
        
    if test_type == "L":
        for i, (data_series, time_series) in enumerate(zip(data, test_time)):
            max_y_value = max(max_y_value, max(data_series))  
            fig.add_trace(go.Scatter(
                x=time_series,
                y=data_series,
                mode='markers+lines',
                name=sample_tags[i],
                marker=dict(symbol='circle', size=5),
                line=dict(width=2),
            ))
        
        yaxis_dict = dict(gridcolor='LightGray')
        yaxis_dict['range'] = [0, max_y_value*1.1]
        
        fig.update_layout(title='Minutes Passed vs Resistance',
                            xaxis_title='Minutes Passed',
                            yaxis_title='Resistance',
                            yaxis=yaxis_dict)
        
    return fig.to_json()