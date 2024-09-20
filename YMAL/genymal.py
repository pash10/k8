from flask import Flask, render_template, request
import find_k8s_keywords, load_yaml_file from keywords


# Load YAML into Python dictionary
def load_yaml(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

# Save updated Python dictionary as YAML
def save_yaml(data, file_path):
    with open(file_path, 'w') as f:
        yaml.dump(data, f)

# Recursively generate form fields based on YAML data
def generate_form_fields(data, parent_key=''):
    form_fields = []
    if isinstance(data, dict):
        for key, value in data.items():
            current_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict):
                form_fields.extend(generate_form_fields(value, current_key))
            else:
                form_fields.append((current_key, value))
    return form_fields

@app.route('/', methods=['GET', 'POST'])
def edit_k8s_yaml():
    yaml_data = load_yaml('k8s_deployment.yaml')

    if request.method == 'POST':
        # Handle form submission to dynamically update the YAML structure
        for key in request.form:
            keys = key.split('.')
            value = request.form[key]
            
            # Dynamically update nested YAML structure
            d = yaml_data
            for k in keys[:-1]:
                d = d.setdefault(k, {})
            d[keys[-1]] = value
        
        # Save the updated YAML
        save_yaml(yaml_data, 'updated_deployment.yaml')
        return f"YAML updated and saved!"

    form_fields = generate_form_fields(yaml_data)
    return render_template('dynamic_form.html', form_fields=form_fields)
