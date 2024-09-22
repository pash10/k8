import  yaml
from yaml.loader import SafeLoader

# Define a dictionary with common Kubernetes YAML keywords
k8s_keywords = {
    "metadata": ["apiVersion", "kind", "name", "namespace", "labels", "annotations"],
    "spec": {
        "Pod": {
            "containers": {
                "name": [],
                "image": [],
                "ports": ["containerPort"],
                "env": ["name", "value", "valueFrom"],
                "resources": ["limits", "requests"],
                "volumeMounts": ["name", "mountPath"],
            },
            "volumes": ["name", "persistentVolumeClaim", "configMap", "secret"],
            "restartPolicy": [],
            "nodeSelector": [],
            "affinity": [],
            "tolerations": [],
        },
        "Deployment": {
            "replicas": [],
            "selector": ["matchLabels"],
            "strategy": ["type", "rollingUpdate"],
            "template": {
                "metadata": ["labels"],
                "spec": {
                    "containers": {
                        "name": [],
                        "image": [],
                        "ports": ["containerPort"],
                        "env": ["name", "value", "valueFrom"],
                        "resources": ["limits", "requests"],
                        "volumeMounts": ["name", "mountPath"],
                    }
                }
            }
        },
        "Service": ["type", "ports", "port", "targetPort", "nodePort", "selector"],
        "Ingress": ["rules", "host", "http", "paths", "backend", "serviceName", "servicePort"],
        "ConfigMap": ["data"],
        "Secret": ["data", "stringData"],
        "PVC": ["accessModes", "resources", "requests", "storageClassName"],
        "StatefulSet": {
            "serviceName": [],
            "replicas": [],
            "selector": ["matchLabels"],
            "template": {
                "metadata": ["labels"],
                "spec": {
                    "containers": {
                        "name": [],
                        "image": [],
                        "ports": ["containerPort"],
                        "env": ["name", "value", "valueFrom"],
                        "resources": ["limits", "requests"],
                        "volumeMounts": ["name", "mountPath"],
                    }
                }
            },
            "volumeClaimTemplates": []
        },
        "DaemonSet": {
            "selector": ["matchLabels"],
            "template": {
                "metadata": ["labels"],
                "spec": {
                    "containers": {
                        "name": [],
                        "image": [],
                        "ports": ["containerPort"],
                        "env": ["name", "value", "valueFrom"],
                        "resources": ["limits", "requests"],
                        "volumeMounts": ["name", "mountPath"],
                    }
                }
            },
            "updateStrategy": ["type"]
        },
        "Job": {
            "template": {
                "metadata": ["labels"],
                "spec": {
                    "containers": {
                        "name": [],
                        "image": [],
                        "ports": ["containerPort"],
                        "env": ["name", "value", "valueFrom"],
                        "resources": ["limits", "requests"],
                        "volumeMounts": ["name", "mountPath"],
                    }
                }
            },
            "backoffLimit": []
        },
        "CronJob": {
            "schedule": [],
            "jobTemplate": {
                "metadata": ["labels"],
                "spec": {
                    "containers": {
                        "name": [],
                        "image": [],
                        "ports": ["containerPort"],
                        "env": ["name", "value", "valueFrom"],
                        "resources": ["limits", "requests"],
                        "volumeMounts": ["name", "mountPath"],
                    }
                }
            }
        },
        "NetworkPolicy": ["podSelector", "policyTypes", "ingress", "egress"],
        "HPA": ["scaleTargetRef", "minReplicas", "maxReplicas", "metrics"],
        "ServiceAccount": ["secrets"]
    },
    "additional": [
        "imagePullSecrets", 
        "affinity", 
        "tolerations", 
        "nodeSelector", 
        "hostNetwork", 
        "terminationGracePeriodSeconds", 
        "livenessProbe", 
        "readinessProbe", 
        "restartPolicy", 
        "dnsPolicy"
    ]
}

def yaml_to_graph(yaml_dict):
    """Convert YAML dictionary to a graph structure."""
    graph = {}

    def build_graph(node, parent_key=""):
        if isinstance(node, dict):
            for key, value in node.items():
                full_key = f"{parent_key}.{key}" if parent_key else key
                graph[full_key] = value
                build_graph(value, full_key)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                full_key = f"{parent_key}[{i}]"
                graph[full_key] = item
                build_graph(item, full_key)

    build_graph(yaml_dict)
    return graph

def dfs_search(graph, keyword, current_node):
    # Check if the current node exists in the graph
    if current_node in graph:
        # If the keyword matches the current node, return the match
        if keyword in current_node:
            return current_node, graph[current_node]
        elif isinstance(graph[current_node], dict):
            # Recursively search deeper in the nested dictionary
            for key in graph[current_node]:
                result = dfs_search(graph, keyword, f"{current_node}.{key}")
                if result:
                    return result

    # Handle cases where the keyword is part of an array (e.g., containers[0])
    for key in graph:
        # Simplified check to handle array indices like [0], [1]
        if keyword in key.replace("[0]", "").replace("[1]", ""):  # Ignore list indices for matching
            return key, graph[key]

    return None


def find_k8s_keywords_dfs(input_text):
    # Convert YAML to a graph structure
    graph = yaml_to_graph(input_text)
       # Debugging output to check the flattened structure


    matches = {}

    # Print flattened YAML structure for debugging
    print("Flattened YAML structure:")
    for key , value in graph.items():
      print(f"{key}: {value}")
    # Extract the kind (resource type) from the YAML file
    print('/n')
    resource_type = graph.get("kind")
    if not resource_type:
        print("Resource type (kind) not found in YAML.")
        return matches

    print(f"Resource type identified: {resource_type}")
    
    
    # Perform DFS-based search only for the relevant resource type
    if resource_type in k8s_keywords["spec"]:
        print(f"Searching resource type: {resource_type}")
        resource_keywords = k8s_keywords["spec"][resource_type]
        if isinstance(resource_keywords, dict):
            for sub_key, sub_keywords in resource_keywords.items():
                for keyword in sub_keywords:
                    match = dfs_search(graph, keyword, f"{resource_type}.{sub_key}")
                    if match:
                        if resource_type not in matches:
                            matches[resource_type] = []
                        matches[resource_type].append(match)

        else:
            for keyword in resource_keywords:
                match = dfs_search(graph, keyword, resource_type)
                if match:
                    if resource_type not in matches:
                        matches[resource_type] = []
                    matches[resource_type].append(match)
    else:
        print(f"No keywords found for resource type: {resource_type}")

    # Print matches for debugging
    print("Matches found:", matches)
    return matches

def rebuild_k8s_yaml_from_graph(matches, graph):
    """Rebuild the YAML structure based on the matches and graph, ensuring metadata fields are added."""
    rebuilt_yaml = {}

    # Metadata fields to check and add if they exist
    metadata_fields = ["apiVersion", "kind", "name", "namespace", "labels", "annotations"]

    # Ensure apiVersion and kind are added
    if "apiVersion" in graph:
        rebuilt_yaml["apiVersion"] = graph["apiVersion"]
    if "kind" in graph:
        rebuilt_yaml["kind"] = graph["kind"]

    # Rebuild the metadata section
    rebuilt_yaml["metadata"] = {}
    for field in metadata_fields:
        field_key = f"metadata.{field}"
        if field_key in graph:
            rebuilt_yaml["metadata"][field] = graph[field_key]

    # Rebuild the spec section based on resource type
    if "spec" in graph:
        rebuilt_yaml["spec"] = graph["spec"]

    # Insert matched elements back into the proper structure
    for resource_type, match_list in matches.items():
        for match in match_list:
            key, value = match
            keys = key.split(".")  # Split the key into its nested components
            d_nested = rebuilt_yaml
            for k in keys[:-1]:
                if "[" in k and "]" in k:  # Handle list indices
                    list_key, index = k.split("[")
                    index = int(index[:-1])  # Get the actual index
                    if list_key not in d_nested:
                        d_nested[list_key] = []
                    while len(d_nested[list_key]) <= index:
                        d_nested[list_key].append({})
                    d_nested = d_nested[list_key][index]
                else:
                    d_nested = d_nested.setdefault(k, {})

            # Correct handling of string values with extra quotes
            if isinstance(value, str):
                # If the value starts and ends with quotes, remove them
                if value.startswith('"') and value.endswith('"'):
                    d_nested[keys[-1]] = value[1:-1]  # Strip the extra quotes
                else:
                    d_nested[keys[-1]] = value  # Leave as-is if no extra quotes
            else:
                d_nested[keys[-1]] = value  # Handle non-string values as-is

    return rebuilt_yaml


class QuotedLoader(SafeLoader):
    """Custom loader to preserve quotes in the YAML data."""
    def construct_scalar(self, node):
        value = super().construct_scalar(node)
        # Return the value with quotes if the node style requires it
        if isinstance(value, str) and node.style == '"':
            # Keep quotes if explicitly required in the YAML
            return f'"{value}"'
        return value

# Custom dumper to ensure strings are quoted when necessary
class QuotedDumper(yaml.SafeDumper):
    def represent_str(self, data):
        # Only wrap the string in quotes if necessary
        if isinstance(data, str) and (":" in data or " " in data):
            # Wrap the string in quotes if it contains special characters
            return self.represent_scalar('tag:yaml.org,2002:str', data)
        # Otherwise, return the string without extra quotes
        return self.represent_scalar('tag:yaml.org,2002:str', data)


# Load a YAML file using the QuotedLoader
def load_yaml_file(file_path):
    """Loads the given YAML file and preserves quoted strings."""
    with open(file_path, 'r') as file:
        data = yaml.load(file, Loader=QuotedLoader)  # Load the YAML file into a Python dict
    return data

# Save a YAML file using the QuotedDumper
def save_yaml_file(yaml_data, file_path):
    """Saves the given YAML data to a specified file, ensuring quoted strings."""
    with open(file_path, 'w') as file:
        yaml.dump(yaml_data, file, Dumper=QuotedDumper, default_flow_style=False, sort_keys=False)


# Example usage:

# Example usage
yaml_file_path = 'exmple.yaml'  # Ensure the file path is correct
input_text = load_yaml_file(yaml_file_path)

# Convert YAML to graph
graph = yaml_to_graph(input_text)

# Find matching keywords in the graph
matching_keywords = find_k8s_keywords_dfs(input_text)

# Rebuild the YAML from the matches and the graph
rebuilt_yaml = rebuild_k8s_yaml_from_graph(matching_keywords, graph)

# Save the rebuilt YAML to a file
save_yaml_file(rebuilt_yaml, "rebuilt_output.yaml")

# Print the matching keywords
for key, value in matching_keywords.items():
    print(f"Section: {key}")
    for keyword_data in value:
        print(f"  Keyword: {keyword_data[0]}, Value: {keyword_data[1]}")
