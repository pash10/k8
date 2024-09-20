import  yaml

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


def flatten_dict(input_dict, parent_key='', sep='.'):
    """Flatten a nested dictionary, handling lists and sub-dictionaries."""
    items = []
    for k, v in input_dict.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    # Handle dictionaries inside lists (like containers)
                    items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                else:
                    # Add list items as individual elements
                    items.append((f"{new_key}[{i}]", item))
        else:
            items.append((new_key, v))
    return dict(items)

def unflatten_dict(d, sep='.'):
    result = {}
    for key, value in d.items():
        keys = key.split(sep)
        d_nested = result
        for k in keys[:-1]:
            d_nested = d_nested.setdefault(k, {})
        d_nested[keys[-1]] = value
    return result

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
        if keyword in current_node:
            return current_node, graph[current_node]
        elif isinstance(graph[current_node], dict):
            # Continue searching deeper into the nested structure
            for key in graph[current_node]:
                result = dfs_search(graph, keyword, f"{current_node}.{key}")
                if result:
                    return result
    # Check if there's an array-like structure (e.g., spec.containers[0])
    for key in graph:
        if keyword in key.replace("[0]", ""):
            return key, graph[key]
    return None
def find_k8s_keywords_dfs(input_text):
    # Convert YAML to a graph structure
    graph = yaml_to_graph(input_text)
    matches = {}

    # Print flattened YAML structure for debugging
    print("Flattened YAML structure:")
    for key, value in graph.items():
        print(f"{key}: {value}")
    
    # Extract the kind (resource type) from the YAML file
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

# Load a YAML file
def load_yaml_file(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)  # Load the YAML file into a Python dict
    return data

# Example usage
yaml_file_path = 'exmple.yaml'  # Ensure the file path is correct
input_text = load_yaml_file(yaml_file_path)
matching_keywords = find_k8s_keywords_dfs(input_text)

# Print the matching keywords
for key, value in matching_keywords.items():
    print(f"Section: {key}")
    for keyword_data in value:
        print(f"  Keyword: {keyword_data[0]}, Value: {keyword_data[1]}")
