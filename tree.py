import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ScientistQuadTreeNode:
    def __init__(self, bounds):
        self.bounds = bounds  # (x_min, y_min, x_max, y_max)
        self.children = [None, None, None, None]  # NW, NE, SW, SE
        self.data = []
name_to_int = {}  # Dictionary to map names to integers
def insert_scientist_into_quad_tree(node, scientist_data):
    name, awards, education_vector, publications = scientist_data  # Unpack the tuple into individual variables

    # Assign a unique integer to the scientist's name
    name_int = name_to_int.get(name)
    if name_int is None:
        name_int = len(name_to_int) + 1
        name_to_int[name] = name_int
    
    # Use the name's integer representation as x-coordinate and publications as y-coordinate
    point = (name_int, publications)
    
    # Check if the point falls within the bounds of this node
    if (
        node.bounds[0] <= point[0] <= node.bounds[2] and
        node.bounds[1] <= point[1] <= node.bounds[3]
    ):
        # Point is within the bounds of this node
        if all(child is None for child in node.children):
            # Node has no children, insert data here
            node.data.append((name, awards, education_vector, publications, point))

            # Check if the node needs to split
            if len(node.data) > 4:  # Adjust as needed
                split_scientist_quad_tree_node(node)

        else:
            # Point is within bounds, but the node has children
            quadrant = get_scientist_quadrant(node, point)
            if node.children[quadrant] is None:
                # Create a child node if it doesn't exist
                node.children[quadrant] = ScientistQuadTreeNode(calculate_scientist_quadrant_bounds(node, quadrant))
            insert_scientist_into_quad_tree(node.children[quadrant], scientist_data)

         
def get_scientist_quadrant(node, point):
    mid_x = (node.bounds[0] + node.bounds[2]) / 2
    mid_y = (node.bounds[1] + node.bounds[3]) / 2

    if point[0] < mid_x:
        # Point is in the west
        if point[1] < mid_y:
            return 2  # SW
        else:
            return 0  # NW
    else:
        # Point is in the east
        if point[1] < mid_y:
            return 3  # SE
        else:
            return 1  # NE
        
def split_scientist_quad_tree_node(node):
    x_min, y_min, x_max, y_max = node.bounds
    mid_x = (x_min + x_max) / 2
    mid_y = (y_min + y_max) / 2

    node.children[0] = ScientistQuadTreeNode((x_min, mid_y, mid_x, y_max))  # NW
    node.children[1] = ScientistQuadTreeNode((mid_x, mid_y, x_max, y_max))  # NE
    node.children[2] = ScientistQuadTreeNode((x_min, y_min, mid_x, mid_y))  # SW
    node.children[3] = ScientistQuadTreeNode((mid_x, y_min, x_max, mid_y))  # SE

    # Reinsert data into children
    data_points = node.data.copy()  # Copy the data to avoid modifying the list while iterating
    node.data = []  # Clear data in current node after splitting
    for data_point in data_points:
        quadrant = get_scientist_quadrant(node, data_point[4])  # Get the quadrant for the point
        node.children[quadrant].data.append(data_point)  # Insert into the correct child node

def print_quad_tree(node, level=0):
    if node is not None:
        indent = "  " * level
        if node.data:
            print(f"{indent}Level {level}: Bounds - {node.bounds}")
            for scientist_info in node.data:
                name = scientist_info[0]
                awards = scientist_info[1]
                education_vector = scientist_info[2]
                publications = scientist_info[3]
                print(f"{indent}    Scientist: {name}, {name_to_int[name]}")
        for child in node.children:
            print_quad_tree(child, level + 1)



            
# Helper functions (unchanged)

# Importing the data
with open('final_output.json', 'r', encoding='utf-8') as file:
    scientists_data = json.load(file)

# # Initialize variables to store the minimum and maximum awards and publications
# min_awards = float('inf')  # Set to positive infinity to ensure any value will be smaller
# max_awards = float('-inf')  # Set to negative infinity to ensure any value will be larger
# min_publications = float('inf')  # Set to positive infinity to ensure any value will be smaller
# max_publications = float('-inf')  # Set to negative infinity to ensure any value will be larger

# # Iterate over each scientist's data to find the minimum and maximum values
# for scientist, data in scientists_data.items():
#     awards = data.get("Awards", 0)
#     publications = data.get("DBLP Publications", 0)
    
#     # Update minimum and maximum values
#     min_awards = min(min_awards, awards)
#     max_awards = max(max_awards, awards)
#     min_publications = min(min_publications, publications)
#     max_publications = max(max_publications, publications)

# # Print the minimum and maximum values found
# print("Minimum Awards:", min_awards)
# print("Maximum Awards:", max_awards)
# print("Minimum Publications:", min_publications)
# print("Maximum Publications:", max_publications)

# Create the root node of the quad tree
root_node_bounds = (0, 0, 700, 1500)  # Adjust the bounds based on your data
quad_tree_root = ScientistQuadTreeNode(root_node_bounds)

# Insert each scientist's data into the quad tree
for name, data in scientists_data.items():
    awards = data.get("Awards", 0)  # Default to 0 if "Awards" key is not present
    publications = data.get("DBLP Publications", 0)  # Default to 0 if "DBLP Publications" key is not present
    education_vector = data.get("Education", "")  # Default to an empty string if "Education" key is not present
    
    # Create a tuple with the required information
    scientist_info = (name, awards, education_vector, publications)
    #print (scientist_info)
    insert_scientist_into_quad_tree(quad_tree_root, scientist_info)

# Print the root of the quad tree
print_quad_tree(quad_tree_root)


def get_last_name(name):
    # Function to extract the last name from the scientist's full name
    return name.split()[-1]

def query_last_names_range(node, start_letter, end_letter, start_prizes, end_prizes, start_publications, end_publications, education_query_keywords, similarity_threshold):
    result = []
    
    # Helper function to traverse the quad tree
    def traverse_tree(node):
        if node is not None:
            for scientist_info in node.data:
                name = scientist_info[0]
                last_name = get_last_name(name)
                # Check if the last name falls within the specified range
                if start_letter <= last_name[0] <= end_letter:
                    # Check if the prizes and publications fall within the specified ranges
                    if start_prizes <= scientist_info[1] <= end_prizes and start_publications <= scientist_info[3] <= end_publications:
                        # Calculate education similarity
                        if scientist_info[2] == "" or scientist_info[2].lower() == "no recorded education":
                            education_similarity=1
                        else:
                            education_similarity = calculate_education_similarity(scientist_info[2], education_query_keywords)
                        # Include the scientist in the results only if education similarity is above the specified threshold
                        if education_similarity >= similarity_threshold:
                            result.append((name, node.bounds, scientist_info[1], scientist_info[2], scientist_info[3], education_similarity))
                            break  # No need to continue searching this node
            for child in node.children:
                traverse_tree(child)

    traverse_tree(node)
    return result


def calculate_education_similarity(education_vector, education_query_keywords):
    # Split education vector and query keywords into sets of unique words
    education_words = set(education_vector.lower().split())
    query_words = set(word.lower() for word in education_query_keywords)

    # Count the number of matching unique keywords found in the education vector
    matching_keywords = sum(1 for word in education_words if word in query_words)

    # Calculate the percentage of matching unique keywords
    total_keywords = len(query_words)
    if total_keywords == 0:
        return 0  # Avoid division by zero
    education_similarity = matching_keywords / total_keywords
    
    return education_similarity

# Example usage:
# Assuming quad_tree_root is the root node of your quad tree
# Prompt the user to input the range of letters
start_letter = input("Enter the start letter of the last name range: ").upper()
end_letter = input("Enter the end letter of the last name range: ").upper()

# Prompt the user to input the range of prizes
start_prizes = int(input("Enter the start range of prizes: "))
end_prizes = int(input("Enter the end range of prizes: "))

# Prompt the user to input the range of publications
start_publications = int(input("Enter the start range of publications: "))
end_publications = int(input("Enter the end range of publications: "))

# Education similarity based query
education_query_keywords = input("Enter the query keywords for education: ").split()  # Split the input into keywords
similarity_threshold = float(input("Enter the threshold for education similarity: "))


nodes_in_range = query_last_names_range(quad_tree_root, start_letter, end_letter, start_prizes, end_prizes, start_publications, end_publications, education_query_keywords, similarity_threshold)
for name, position, awards,education_vector, publications, education_similarity in nodes_in_range:
    print(f"Scientist: {name}, Position: {position}, Awards: {awards}, Publications: {publications}")
    #print(f"education_vector: {education_vector}")
    if not education_vector or education_vector.lower() == "no recorded education":
        print("No recorded education")
    else:
        print(f"education_similarity: {education_similarity:.2f}")
