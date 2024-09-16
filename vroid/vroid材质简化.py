import bpy

def remove_invalid_and_reposition_nodes(material):
    if material.node_tree:
        nodes_to_remove = []
        image_nodes = {}
        
        # First pass: identify and collect nodes to remove
        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE':
                # Check if the image is valid
                if not node.image:
                    nodes_to_remove.append(node)
                else:
                    # Collect image nodes, but only keep one node per image
                    if node.image.name not in image_nodes:
                        image_nodes[node.image.name] = node
                    else:
                        nodes_to_remove.append(node)
            else:
                nodes_to_remove.append(node)
        
        # Remove the invalid nodes
        for node in nodes_to_remove:
            material.node_tree.nodes.remove(node)
        
        # Reposition remaining nodes
        remaining_nodes = [node for node in material.node_tree.nodes if node.type == 'TEX_IMAGE']
        
        # Arrange nodes horizontally
        x_offset = 0
        y_offset = 0
        spacing = 300  # Adjust spacing as needed

        for node in remaining_nodes:
            node.location.x = x_offset
            node.location.y = y_offset
            x_offset += spacing
        
        # Add Principled BSDF and Material Output nodes
        node_tree = material.node_tree
        
        # Create Principled BSDF node
        bsdf_node = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf_node.location = (x_offset, y_offset)  # Place it right after the last image node
        
        # Create Material Output node
        output_node = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (x_offset + spacing, y_offset)
        
        # Connect the Principled BSDF node to the Material Output node
        bsdf_output = bsdf_node.outputs['BSDF']
        output_surface = output_node.inputs['Surface']
        node_tree.links.new(bsdf_output, output_surface)
        
        # Find image textures with the label 'Lit Color Texture' and connect them to Principled BSDF
        for node in node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.label == 'Lit Color Texture':
                # Connect the image texture color to the Principled BSDF Base Color
                color_socket = bsdf_node.inputs['Base Color']
                alpha_socket = bsdf_node.inputs.get('Alpha', None)
                
                if color_socket:
                    node_tree.links.new(node.outputs['Color'], color_socket)
                
                if alpha_socket and 'Alpha' in node.outputs:
                    node_tree.links.new(node.outputs['Alpha'], alpha_socket)
        
        # Find image textures with the label 'Normal Map Texture' and connect them to Principled BSDF
        for node in node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.label == 'Normal Map Texture':
                # Connect the image texture color to the Principled BSDF Normal
                normal_socket = bsdf_node.inputs.get('Normal', None)
                
                if normal_socket:
                    # Use a Normal Map node to convert the image texture to a normal vector
                    normal_map_node = node_tree.nodes.new(type='ShaderNodeNormalMap')
                    normal_map_node.location = (x_offset, y_offset + spacing)
                    
                    # Connect the image texture to the Normal Map node
                    node_tree.links.new(node.outputs['Color'], normal_map_node.inputs['Color'])
                    
                    # Connect the Normal Map node to the Principled BSDF Normal input
                    node_tree.links.new(normal_map_node.outputs['Normal'], normal_socket)

# Iterate over all materials in the current blend file
for material in bpy.data.materials:
    remove_invalid_and_reposition_nodes(material)

print("完成了移除无效节点、重新定位剩余节点、添加Principled BSDF和Material Output节点，并将'Lit Color Texture'图像纹理连接到Base Color，同时将'Normal Map Texture'图像纹理连接到法线输入。")
