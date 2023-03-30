import os
import json
import networkx as nx
import rdflib
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

# Set the path to the folder containing the JSON-LD files
folder_path = "kg_json"

# Set the path to the output folder
output_folder = "output"

# Make sure the output folder exists; if not, create it
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Function to convert JSON-LD to RDF graph
def jsonld_to_rdf_graph(jsonld_data):
    g = rdflib.Graph()
    g.parse(data=json.dumps(jsonld_data), format='json-ld')
    return g

def convert_attribute_to_string(value):
    if isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, dict):
        return {k: convert_attribute_to_string(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [convert_attribute_to_string(v) for v in value]
    else:
        return str(value)

def convert_attributes_to_string(graph):
    for node, attrs in list(graph.nodes(data=True)):
        for key, value in list(attrs.items()):
            graph.nodes[node][key] = convert_attribute_to_string(value)

    for source, target, attrs in list(graph.edges(data=True)):
        for key, value in list(attrs.items()):
            graph.edges[source, target][key] = convert_attribute_to_string(value)

# Iterate through the files in the folder
for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)

    # Attempt to load the JSON-LD file
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        # If an error occurs while loading the file, print the error and skip the file
        print(f"Error while loading {file_name}: {e}")
        continue

    # Attempt to convert the JSON-LD data to a GEXF file
    try:
        rdf_graph = jsonld_to_rdf_graph(data)
        nx_graph = rdflib_to_networkx_multidigraph(rdf_graph)
        convert_attributes_to_string(nx_graph)  # Convert unsupported attribute types to string

        # Write the GEXF graph to a file in the output folder
        output_file_path = os.path.join(output_folder, f"{file_name}.gexf")
        nx.write_gexf(nx_graph, output_file_path, encoding='utf-8')

        print(f"{file_name} converted to GEXF format and saved in {output_folder}")
    except Exception as e:
        # If an error occurs while converting the file, print the error
        print(f"Error while converting {file_name}: {e}")
