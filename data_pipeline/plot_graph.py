import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio

def generate_plotly_figure(df, column_name):
    """
    Takes the dataframe.
    Ignore the values where no timestamp is present.
    Graph is plotted using plotly.
    And is returned in json format.
    """
    df = df[df['Timestamp'] != '00-00-0000 00:00:00']
    df = df.reset_index(drop=True)
    df['Minutes Passed'] = (df['Timestamp'] - df['Timestamp'].iloc[0]).dt.total_seconds() / 60
    fig = go.Figure()

    yaxis_dict = dict(gridcolor='LightGray')
    if column_name == 'Penetration (%)':
        yaxis_dict['range'] = [0, 100]
        x_axis = df.index
        xaxis_title_value = 'Samples'
        title_value = f'Samples vs Penetration (%)'
        
    elif column_name == 'Resistance (mm of H2O)':
        yaxis_dict['range'] = [0, df[column_name].max() * 1.1]
        x_axis = df['Minutes Passed']
        xaxis_title_value = 'Minutes Passed'
        title_value = f'Minutes Passed vs Resistance (mm of H2O)'
        
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

def generate_analyzed_graph(all_test_data):
    
    penetration_data = all_test_data['penetration_data']
    resistance_data = all_test_data['resistance_data']
    sample_tags = all_test_data['sample_tags']

    fig = go.Figure()
    
    # Plot each penetration data series
    for i, data_series in enumerate(penetration_data):
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
    return fig.to_json()