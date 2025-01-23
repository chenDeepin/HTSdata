import dash
from dash import html, dcc, Input, Output, State, callback_context
import pandas as pd
import base64
import io
import string
import os
import json

LICENSE_INFO = """
*********************************************************************************************************************************************************************
MIT License     Version: 0.1 (2025.1.22)
Copyright (c) Chenran Jiang @chenDeepin     All rights reserved
*********************************************************************************************************************************************************************
"""
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.layout = html.Div(style={'font-family': 'Arial, sans-serif', 'padding': '20px'}, children=[
    html.Div(LICENSE_INFO, style={
        'background-color': 'white',
        'color': '#0b7b66', 
        'padding': '2px',
        'border': '0.5px solid #ccc',
        'margin-bottom': '5px',
        'text-align': 'center',
        'font-family': 'Arial, sans-serif',
        'white-space': 'pre-wrap'  
    }),
    html.Div([
        dcc.Upload(
            id='upload-template',
            children=html.Div(['Drag and Drop or Select Template File']),
            style={'border': '2px dashed #a5d2b1', 'padding': '10px', 'text-align': 'center', 'width': '300px', 'margin-bottom': '10px'}
        ),
        dcc.Upload(
            id='upload-files',
            children=html.Div(['Drag and Drop or Select Files']),
            multiple=True, 
            style={'border': '2px dashed #a5d2b1', 'padding': '10px', 'text-align': 'center', 'width': '300px', 'margin-bottom': '10px'}
        ),
        html.Div([
            dcc.Dropdown(id='file-selector', placeholder="Select a file to view", style={'text-align': 'center', 'width': '320px', 'margin-right': '10px'}),
        ], style={'margin-bottom': '20px'}),
        html.Div([
            html.Label("Start Region:", style={'font-weight': 'bold'}),
            dcc.Input(id='start-region', type='text', placeholder='e.g., B2', value='', style={'height': '25px', 'width': '80px',  'margin-right': '10px'}),
            html.Label("End Region:", style={'font-weight': 'bold'}),
            dcc.Input(id='end-region', type='text', placeholder='e.g., D10', value='', style={'height': '25px', 'width': '80px',  'margin-right': '10px'}),
            html.Button('Load Region', id='load-region-button', style={'font-weight': 'bold', 'background-color': '#1eaa9d', 'color': 'white', 'border': 'none', 'height': '35px', 'width': '150px', 'cursor': 'pointer'}),
        ], style={'margin-bottom': '20px'}),
        html.Div([
            html.Label("Positive Ctrl Region:", style={'font-weight': 'bold'}),
            dcc.Input(id='positive-ctrl-cells', type='text', placeholder='e.g., A3-A21,column 1-5,row 2-4', value='', style={'height': '25px', 'width': '220px', 'margin-right': '10px'}),
            html.Label("Negative Ctrl Region:", style={'font-weight': 'bold'}),
            dcc.Input(id='negative-ctrl-cells', type='text', placeholder='e.g., A3-A21,column 1-5,row 2-4', value='', style={'height': '25px', 'width': '220px', 'margin-right': '10px'}),
            html.Label("Blank Ctrl Region:", style={'font-weight': 'bold'}),
            dcc.Input(id='blank-ctrl-cells', type='text', placeholder='e.g., A3-A21,column 1-5,row 2-4', value='', style={'height': '25px', 'width': '220px', 'margin-right': '10px'}),
            html.Label("None Region:", style={'font-weight': 'bold'}),
            dcc.Input(id='none-cells', type='text', placeholder='e.g., A3-A21,column 1-5,row 2-4', value='', style={'height': '25px', 'width': '220px', 'margin-right': '10px'}),
        ], style={'margin-bottom': '20px'}),
        html.Div([
            html.Label("Calculation Equation:", style={'font-weight': 'bold'}),
            dcc.Input(id='equation', type='text', placeholder='e.g., (neg-sample)/(neg-pos)*100%', style={'height': '25px', 'width': '220px', 'margin-right': '10px'}),
            html.Button('Calculate', id='calculate-button', style={'font-weight': 'bold', 'background-color': '#1eaa9d', 'color': 'white', 'border': 'none', 'height': '35px', 'width': '150px', 'cursor': 'pointer'}),
        ], style={'margin-top': '20px'}),
        html.Div([
            html.Label("Template File Name:", style={'font-weight': 'bold'}),
            dcc.Input(id='template-file-name', type='text', placeholder='e.g., template_settings.json', style={'height': '25px', 'width': '220px', 'margin-right': '10px'}),
            html.Button('Save Template', id='save-template-button', style={'font-weight': 'bold', 'background-color': '#427974', 'color': 'white', 'border': 'none', 'height': '35px', 'width': '150px', 'cursor': 'pointer', 'margin-right': '10px'}),
            html.Button('Save Results', id='save-button', style={'font-weight': 'bold', 'background-color': '#427974', 'color': 'white', 'border': 'none', 'height': '35px', 'width': '150px', 'cursor': 'pointer', 'margin-right': '10px'}),
        ], style={'margin-top': '20px'}),
        html.Div(id='save-status', style={'margin-top': '20px'}), 
        html.Div(id='file-list', style={'margin-top': '20px'}),
        html.Div(id='selected-region-table', style={'background-color': '#a5d2b1', 'margin-top': '20px'}),
        html.Div(id='role-layout', style={'background-color': '#1eaa9d', 'margin-top': '20px'}),
        html.Div(id='result-table', style={'background-color': '#427974', 'color': 'white', 'margin-top': '20px'})
    ])
])
@app.callback(
    [Output('start-region', 'value'),
     Output('end-region', 'value'),
     Output('positive-ctrl-cells', 'value'),
     Output('negative-ctrl-cells', 'value'),
     Output('blank-ctrl-cells', 'value'),
     Output('none-cells', 'value'),
     Output('equation', 'value')],
    [Input('upload-template', 'contents')],  
    [State('upload-template', 'filename')]
)
def import_template(contents, filename):
    if contents is None:
        return "", "", "", "", "", "", ""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if filename.endswith('.json'):
            template = json.loads(decoded)
        else:
            return "", "", "", "", "", "", "Invalid file format. Please upload a JSON file."
    except Exception as e:
        return "", "", "", "", "", "", f"Error reading template file: {e}"
    return (
        template.get('start_region', ''),
        template.get('end_region', ''),
        template.get('positive_ctrl_cells', ''),
        template.get('negative_ctrl_cells', ''),
        template.get('blank_ctrl_cells', ''),
        template.get('none_cells', ''),
        template.get('equation', '')
    )
def excel_col_to_num(col):
    num = 0
    for c in col:
        if c in string.ascii_letters:
            num = num * 26 + (ord(c.upper()) - ord('A')) + 1
    return num
def adjust_start_region(start_region):
    start_col, start_row = ''.join(filter(str.isalpha, start_region)), ''.join(filter(str.isdigit, start_region))
    start_row = int(start_row) - 2  
    return start_col, start_row
def parse_cell_intervals(interval_str, df, start_row_offset=0, start_col_offset=0):
    cell_ranges = []
    for interval in interval_str.split(','):
        interval = interval.strip().upper()  
        if interval.lower().startswith('column'):
            # Handle column ranges like 'column 1-5,7-9'
            parts = interval.split()
            if len(parts) < 2:
                continue
            column_ranges = parts[1].split(',')
            for col_range in column_ranges:
                if '-' in col_range:
                    start_col, end_col = col_range.split('-')
                    start_col = int(start_col) - 1  
                    end_col = int(end_col) - 1
                    for col in range(start_col, end_col + 1):
                        cell_ranges.extend([(row, col) for row in range(len(df))])
                else:
                    col = int(col_range) - 1
                    cell_ranges.extend([(row, col) for row in range(len(df))])
        elif interval.lower().startswith('row'):
            parts = interval.split()
            if len(parts) < 2:
                continue
            row_ranges = parts[1].split(',')
            for row_range in row_ranges:
                if '-' in row_range:
                    start_row, end_row = row_range.split('-')
                    start_row = int(start_row) - 1  
                    end_row = int(end_row) - 1
                    for row in range(start_row, end_row + 1):
                        cell_ranges.extend([(row, col) for col in range(len(df.columns))])
                else:
                    row = int(row_range) - 1
                    cell_ranges.extend([(row, col) for col in range(len(df.columns))])
        elif '-' in interval:
            start, end = interval.split('-')
            start_col, start_row = ''.join(filter(str.isalpha, start)), ''.join(filter(str.isdigit, start))
            end_col, end_row = ''.join(filter(str.isalpha, end)), ''.join(filter(str.isdigit, end))
            start_col_num = excel_col_to_num(start_col) - 1 - start_col_offset
            end_col_num = excel_col_to_num(end_col) - 1 - start_col_offset
            start_row_num = int(start_row) - 2 - start_row_offset
            end_row_num = int(end_row) - 2 - start_row_offset
            for row in range(start_row_num, end_row_num + 1):
                for col in range(start_col_num, end_col_num + 1):
                    cell_ranges.append((row, col))
        else:
            col, row = ''.join(filter(str.isalpha, interval)), ''.join(filter(str.isdigit, interval))
            col_num = excel_col_to_num(col) - 1 - start_col_offset
            row_num = int(row) - 2 - start_row_offset
            cell_ranges.append((row_num, col_num))
    return cell_ranges
def assign_roles(df, positive_ctrl_cells, negative_ctrl_cells, blank_ctrl_cells, none_cells, start_row_offset, start_col_offset):
    roles = {}
    if positive_ctrl_cells:
        positive_cells = parse_cell_intervals(positive_ctrl_cells, df, start_row_offset, start_col_offset)
        for cell in positive_cells:
            roles[cell] = 'pos'
    if negative_ctrl_cells:
        negative_cells = parse_cell_intervals(negative_ctrl_cells, df, start_row_offset, start_col_offset)
        for cell in negative_cells:
            roles[cell] = 'neg'
    if blank_ctrl_cells:
        blank_cells = parse_cell_intervals(blank_ctrl_cells, df, start_row_offset, start_col_offset)
        for cell in blank_cells:
            roles[cell] = 'blank'
    if none_cells:
        none_cells = parse_cell_intervals(none_cells, df, start_row_offset, start_col_offset)
        for cell in none_cells:
            roles[cell] = 'none'

    return roles
def calculate_averages(df, roles):
    role_sums = {'pos': 0, 'neg': 0, 'blank': 0, 'none': 0}
    role_counts = {'pos': 0, 'neg': 0, 'blank': 0, 'none': 0}

    for (row, col), role in roles.items():
        value = pd.to_numeric(df.iloc[row][col], errors='coerce')
        if not pd.isna(value):
            role_sums[role] += value
            role_counts[role] += 1
    role_averages = {role: (role_sums[role] / role_counts[role]) if role_counts[role] > 0 else 0 for role in role_sums}
    return role_averages
def normalize_values(df, equation, roles, role_averages):
    equation_safe = equation    
    equation_safe = equation_safe.replace('pos', str(role_averages['pos']))
    equation_safe = equation_safe.replace('neg', str(role_averages['neg']))
    equation_safe = equation_safe.replace('blank', str(role_averages['blank']))    
    result_df = df.copy()
    for i in range(len(df)):  
        for j in range(len(df.columns)):  
            role = roles.get((i, j), 'sample')  
            value = pd.to_numeric(df.iloc[i][j], errors='coerce')  
            if pd.isna(value):  
                result_df.iat[i, j] = '-'  
            elif role == 'none':  
                result_df.iat[i, j] = '-'  
            else:
                try:
                    cell_equation = equation_safe.replace('sample', str(value))
                    cell_equation = cell_equation.replace('%', '')
                    result = eval(cell_equation)
                    result_df.iat[i, j] = result  
                except Exception as e:  
                    result_df.iat[i, j] = f"Error: {e}"  
    return result_df  
@app.callback(
    [Output('selected-region-table', 'children'),
     Output('file-list', 'children'),
     Output('file-selector', 'options'),
     Output('file-selector', 'value')],  
    [Input('upload-files', 'contents'),
     Input('load-region-button', 'n_clicks'),  
     Input('file-selector', 'value')],  
    [State('upload-files', 'filename'),
     State('start-region', 'value'),
     State('end-region', 'value')]
)
def display_selected_region(contents, load_region_clicks, selected_file, filenames, start_region, end_region):
    if contents is None:
        return "No file uploaded.", "", [], None  
    file_list = html.Div([
        html.H5("Uploaded Files:"),
        html.Ul([html.Li(filename) for filename in filenames])
    ])
    file_options = [{'label': filename, 'value': i} for i, filename in enumerate(filenames)]
    selected_index = selected_file if selected_file is not None else 0  
    content_type, content_string = contents[selected_index].split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_excel(io.BytesIO(decoded), engine='openpyxl')
    if load_region_clicks is not None and start_region and end_region:
        try:
            start_col = ''.join(filter(str.isalpha, start_region))
            start_row = int(''.join(filter(str.isdigit, start_region))) - 2  
            end_col = ''.join(filter(str.isalpha, end_region))
            end_row = int(''.join(filter(str.isdigit, end_region)))  
            start_col_num = excel_col_to_num(start_col) - 1  
            end_col_num = excel_col_to_num(end_col)  
            selected_df = df.iloc[start_row:end_row, start_col_num:end_col_num]
        except Exception as e:
            return "Error accessing the data slice.", file_list, file_options, selected_index  
        global start_region_cell, start_row_offset, start_col_offset
        start_region_cell = start_region
        start_row_offset = start_row
        start_col_offset = start_col_num  
        selected_region_table = html.Div([
            html.H5("Selected Region:"),
            html.Table(
                [html.Tr([html.Th("Row")] + [html.Th(f"Column {i+1}") for i in range(len(selected_df.columns))])] +
                [html.Tr([html.Td(i + 1)] + [html.Td(selected_df.iloc[i][j]) for j in range(len(selected_df.columns))]) for i in range(len(selected_df))]
            )
        ])
        return selected_region_table, file_list, file_options, selected_index  
    else:
        return "Please specify Start Region and End Region.", file_list, file_options, selected_index  
@app.callback(
    [Output('role-layout', 'children'),
     Output('result-table', 'children')],
    Input('calculate-button', 'n_clicks'),
    [State('equation', 'value'),
     State('selected-region-table', 'children'),
     State('positive-ctrl-cells', 'value'),
     State('negative-ctrl-cells', 'value'),
     State('blank-ctrl-cells', 'value'),
     State('none-cells', 'value')]
)
def calculate_and_display_results(n_clicks, equation, selected_region, positive_ctrl_cells, negative_ctrl_cells, blank_ctrl_cells, none_cells):
    if n_clicks is None:
        return "", "No calculation performed."
    if not isinstance(selected_region, dict):
        return "", "Invalid selected region data."
    try:
        table_data = selected_region['props']['children'][1]['props']['children']
        rows = []
        for row in table_data[1:]:  
            cells = row['props']['children']
            row_data = [cell['props']['children'] for cell in cells[1:]]  
            rows.append(row_data)
        df = pd.DataFrame(rows)
        global start_row_offset, start_col_offset
        role_errors = {}  
        overlapping_cells = {}  
        roles = {}
        role_cells = {
            'pos': set(),
            'neg': set(),
            'blank': set(),
            'none': set()
        }
        role_inputs = {
            'pos': positive_ctrl_cells,
            'neg': negative_ctrl_cells,
            'blank': blank_ctrl_cells,
            'none': none_cells
        }
        try:
            positive_roles = parse_cell_intervals(positive_ctrl_cells, df, start_row_offset, start_col_offset) if positive_ctrl_cells else []
            for cell in positive_roles:
                if cell in roles:
                    if cell not in overlapping_cells:
                        overlapping_cells[cell] = set()
                    overlapping_cells[cell].add(roles[cell])
                    overlapping_cells[cell].add('pos')
                roles[cell] = 'pos'
                role_cells['pos'].add(cell)
        except Exception as e:
            role_errors['Positive Ctrl'] = str(e)
        try:
            negative_roles = parse_cell_intervals(negative_ctrl_cells, df, start_row_offset, start_col_offset) if negative_ctrl_cells else []
            for cell in negative_roles:
                if cell in roles:
                    if cell not in overlapping_cells:
                        overlapping_cells[cell] = set()
                    overlapping_cells[cell].add(roles[cell])
                    overlapping_cells[cell].add('neg')
                roles[cell] = 'neg'
                role_cells['neg'].add(cell)
        except Exception as e:
            role_errors['Negative Ctrl'] = str(e)
        try:
            blank_roles = parse_cell_intervals(blank_ctrl_cells, df, start_row_offset, start_col_offset) if blank_ctrl_cells else []
            for cell in blank_roles:
                if cell in roles:
                    if cell not in overlapping_cells:
                        overlapping_cells[cell] = set()
                    overlapping_cells[cell].add(roles[cell])
                    overlapping_cells[cell].add('blank')
                roles[cell] = 'blank'
                role_cells['blank'].add(cell)
        except Exception as e:
            role_errors['Blank Ctrl'] = str(e)
        try:
            none_roles = parse_cell_intervals(none_cells, df, start_row_offset, start_col_offset) if none_cells else []
            for cell in none_roles:
                if cell in roles:
                    if cell not in overlapping_cells:
                        overlapping_cells[cell] = set()
                    overlapping_cells[cell].add(roles[cell])
                    overlapping_cells[cell].add('none')
                roles[cell] = 'none'
                role_cells['none'].add(cell)
        except Exception as e:
            role_errors['None'] = str(e)
        if role_errors:
            error_messages = [html.P(f"{role}: Invalid input - {error}") for role, error in role_errors.items()]
            return html.Div([
                html.H5("Role Layout:"),
                html.Div(error_messages),
                html.P(f"Equation: {equation}")
            ]), "Error in role selection. Please check your inputs."
        if overlapping_cells:
            overlapping_messages = []
            for cell, conflicting_roles in overlapping_cells.items():
                row, col = cell
                conflicting_inputs = []
                for role in conflicting_roles:
                    input_str = role_inputs[role]
                    if input_str.lower().startswith('row'):
                        conflicting_inputs.append(f"row {row + 1}")
                    elif input_str.lower().startswith('column'):
                        conflicting_inputs.append(f"column {col + 1}")
                    else:
                        adjusted_row = row + start_row_offset + 2  
                        adjusted_col = col + start_col_offset + 1  
                        col_letter = chr(ord('A') + adjusted_col - 1)
                        conflicting_inputs.append(f"{col_letter}{adjusted_row}")
                adjusted_row = row + start_row_offset + 2  
                adjusted_col = col + start_col_offset + 1  
                col_letter = chr(ord('A') + adjusted_col - 1)
                cell_reference = f"{col_letter}{adjusted_row}"
                overlapping_messages.append(f"Cell {cell_reference} is assigned to roles: {', '.join(conflicting_roles)} (from inputs: {', '.join(conflicting_inputs)})")
            overlapping_message = html.Div([
                html.P("Warning: Overlapping cells detected in role assignments. The following roles have conflicts:"),
                html.Ul([html.Li(message) for message in overlapping_messages])
            ])
        else:
            overlapping_message = None
        role_averages = calculate_averages(df, roles)
        result_df = normalize_values(df, equation, roles, role_averages)
        role_layout = html.Div([
            html.H5("Role Layout:"),
            html.Div([
                overlapping_message,
                html.P(f"None: {none_cells if none_cells else '-'}; Averaged value is {role_averages['none']:.2f}" if none_cells else "None: -"),
                html.P(f"Positive Ctrl: {positive_ctrl_cells if positive_ctrl_cells else '-'}; Averaged value is {role_averages['pos']:.2f}" if positive_ctrl_cells else "Positive Ctrl: -"),
                html.P(f"Negative Ctrl: {negative_ctrl_cells if negative_ctrl_cells else '-'}; Averaged value is {role_averages['neg']:.2f}" if negative_ctrl_cells else "Negative Ctrl: -"),
                html.P(f"Blank Ctrl: {blank_ctrl_cells if blank_ctrl_cells else '-'}; Averaged value is {role_averages['blank']:.2f}" if blank_ctrl_cells else "Blank Ctrl: -"),
                html.P(f"Equation: {equation}")
            ])
        ])
        result_table = html.Div([
            html.H5("Calculated Results:"),
            html.Table(
                [html.Tr([html.Th("Row")] + [html.Th(f"Column {i+1}") for i in range(len(result_df.columns))])] +
                [html.Tr([html.Td(i + 1)] + [html.Td(result_df.iloc[i][j]) for j in range(len(result_df.columns))]) for i in range(len(result_df))]
            )
        ])
        return role_layout, result_table
    except Exception as e:
        return "", f"An error occurred: {e}"
@app.callback(
    Output('save-status', 'children'),
    [Input('save-template-button', 'n_clicks'),
     Input('save-button', 'n_clicks')],
    [State('start-region', 'value'),
     State('end-region', 'value'),
     State('positive-ctrl-cells', 'value'),
     State('negative-ctrl-cells', 'value'),
     State('blank-ctrl-cells', 'value'),
     State('none-cells', 'value'),
     State('equation', 'value'),
     State('result-table', 'children'),  
     State('upload-files', 'contents'),   
     State('upload-files', 'filename'),   
     State('template-file-name', 'value'),
     State('selected-region-table', 'children')]  
)
def save_template_and_results(
    save_template_clicks,  
    save_results_clicks,  
    start_region,          
    end_region,            
    positive_ctrl_cells,  
    negative_ctrl_cells,   
    blank_ctrl_cells,     
    none_cells,            
    equation,             
    result_table,         
    contents,             
    filenames,            
    template_file_name,    
    selected_region        
):
    ctx = callback_context
    if not ctx.triggered:
        return ""
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == 'save-template-button':
        if save_template_clicks is None:
            return ""
        if not template_file_name:
            template_file_name = "file_process.json"
        template = {
            'start_region': start_region,
            'end_region': end_region,
            'positive_ctrl_cells': positive_ctrl_cells,
            'negative_ctrl_cells': negative_ctrl_cells,
            'blank_ctrl_cells': blank_ctrl_cells,
            'none_cells': none_cells,
            'equation': equation
        }
        try:
            with open(template_file_name, 'w') as f:
                json.dump(template, f)
            return f"Template saved to {template_file_name}."
        except Exception as e:
            return f"Error saving template: {e}"
    elif triggered_id == 'save-button':
        if save_results_clicks is None:
            return ""
        if not contents or not filenames:
            return "No files uploaded or filenames missing."
        start_col, start_row = adjust_start_region(start_region)
        start_col_num = excel_col_to_num(start_col) - 1
        start_row_num = int(''.join(filter(str.isdigit, start_region))) - 2
        end_col_num = excel_col_to_num(''.join(filter(str.isalpha, end_region))) - 1
        end_row_num = int(''.join(filter(str.isdigit, end_region))) - 1
        for i, (content, filename) in enumerate(zip(contents, filenames)):
            try:
                content_type, content_string = content.split(',')
                decoded = base64.b64decode(content_string)
                df = pd.read_excel(io.BytesIO(decoded), engine='openpyxl')
                selected_df = df.iloc[start_row_num:end_row_num+1, start_col_num:end_col_num+1]
                roles = assign_roles(selected_df, positive_ctrl_cells, negative_ctrl_cells,
                                    blank_ctrl_cells, none_cells, start_row_num, start_col_num)
                role_averages = calculate_averages(selected_df, roles)
                result_df = normalize_values(selected_df, equation, roles, role_averages)
                output_df = df.copy()
                output_df.iloc[start_row_num:end_row_num+1, start_col_num:end_col_num+1] = result_df.values
                output_filename = f"{os.path.splitext(filenames[i])[0]}_processed.xlsx"
                output_df.to_excel(output_filename, index=False)
            except Exception as e:
                return f"Error processing {filename}: {str(e)}"
        return f"Successfully processed {len(filenames)} files"
    return ""
if __name__ == '__main__':
    app.run_server(debug=True)