from flask import Flask, request, render_template_string
from keywords import find_k8s_keywords_dfs, load_yaml_file , save_yaml_file

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

def form_view():
    if request.method == 'POST':
        # Capture submitted form data and update the dynamic data
        submitted_data = {field: request.form[field] for field in form_structure if field != 'submit'}

        # Convert the submitted data back into the original YAML format
        updated_yaml_data = update_yaml_structure(dynamic_data, submitted_data)

        # Save the updated data to a new YAML file
        save_yaml_file(updated_yaml_data, 'updated_example.yaml')

        # Return a confirmation message
        return f"Form submitted and YAML saved! Data: {submitted_data}"

    # Generate the form HTML dynamically
    form_html = '<form method="POST">'
    for field, props in form_structure.items():
        if props['type'] != 'submit':
            current_value = props.get('value', '')

            # Render the form field
            form_html += f'<label for="{field}">{props["label"]}</label>'
            form_html += f'<input type="{props["type"]}" name="{field}" id="{field}" placeholder="{props["placeholder"]}" value="{current_value}">'
            form_html += f' <span>Value: {current_value}</span> <br><br>'
        else:
            form_html += f'<button type="submit">{props["label"]}</button>'
    form_html += '</form>'

    return render_template_string(form_html)

# Helper function to update the YAML structure with the submitted form data
def update_yaml_structure(original_yaml_data, submitted_data):
    for field, new_value in submitted_data.items():
        # Update the value in the original YAML data
        sections = field.split('.')
        target = original_yaml_data
        for section in sections[:-1]:
            target = target.setdefault(section, {})
        target[sections[-1]] = new_value
    return original_yaml_data


