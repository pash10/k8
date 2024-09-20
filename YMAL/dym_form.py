from flask import Flask, request
from keywords import find_k8s_keywords_dfs, load_yaml_file

# Base form structure
form_structure = {
    
    'submit': {
        'type': 'submit',
        'label': 'Submit'
    }
}

# Function to convert dynamic data into form fields
def add_dynamic_fields(data):
    dynamic_fields = {}
    for section, values in data.items():
        for field, value in values:
            dynamic_fields[field] = {
                'label': field,
                'type': 'text',  # You can adjust the type based on the value
                'placeholder': f'Enter {field} (current: {value})'
            }
    return dynamic_fields

# Example of dynamic data (this can be replaced with any other nested data)
dynamic_data = load_yaml_file('exmple.yaml')
dynamic_data = find_k8s_keywords_dfs(dynamic_data)



# Add dynamic fields to the form structure
form_structure.update(add_dynamic_fields(dynamic_data))

# Route for displaying the form

def Form():
    if request.method == 'POST':
        # Handle form submission
        submitted_data = {field: request.form[field] for field in form_structure if field != 'submit'}
        return f"Form submitted! Data: {submitted_data}"

    # Generate HTML for the form dynamically
    form_html = '<form method="POST">'
    for field, props in form_structure.items():
        if props['type'] != 'submit':
            # Retrieve the current value, handling nested structures (like dictionaries or lists)
            current_value = props.get('value', '')
            
            # If current_value is a dictionary or list, format it as a string
            if isinstance(current_value, (dict, list)):
                formatted_value = f'{current_value}'
            else:
                formatted_value = current_value

            # Render the form field
            form_html += f'<label for="{field}">{props["label"]}</label>'
            form_html += f'<input type="{props["type"]}" name="{field}" id="{field}" placeholder="{props["placeholder"]}" value="{formatted_value}">'
            # Add the current value (formatted) next to the form field
            form_html += f' <span>Value: {formatted_value}</span> <br><br>'
        else:
            form_html += f'<button type="submit">{props["label"]}</button>'
    form_html += '</form>'

    return form_html  # Send the generated HTML as the response


