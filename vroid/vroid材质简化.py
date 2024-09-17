import bpy

def get_armature_and_children_materials(armature):
    """
    获取指定Armature及其子对象使用的所有材质。
    
    参数：
    armature (bpy.types.Object): 要处理的Armature对象。
    
    返回：
    set: 包含所有相关材质的集合。
    """
    materials = set()
    for obj in armature.children:
        if obj.type == 'MESH':
            for slot in obj.material_slots:
                if slot.material:
                    materials.add(slot.material)
    return materials

def remove_invalid_and_reposition_nodes(material):
    """
    移除无效节点，重新定位剩余节点，并添加Principled BSDF和Material Output节点，
    将图像纹理节点连接到Principled BSDF节点的相应输入。
    
    参数：
    material (bpy.types.Material): 要处理的材质。
    """
    if material.node_tree:
        nodes_to_remove = []
        image_nodes = {}
        
        # 第一遍：识别并收集要移除的节点
        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE':
                # 检查图像是否有效
                if not node.image:
                    nodes_to_remove.append(node)
                else:
                    # 收集图像节点，但只保留每个图像的一个节点
                    if node.image.name not in image_nodes:
                        image_nodes[node.image.name] = node
                    else:
                        nodes_to_remove.append(node)
            else:
                nodes_to_remove.append(node)
        
        # 移除无效节点
        for node in nodes_to_remove:
            material.node_tree.nodes.remove(node)
        
        # 分组节点
        connected_nodes = set()
        unconnected_nodes = []
        
        for node in material.node_tree.nodes:
            if any(input.is_linked for input in node.inputs):
                connected_nodes.add(node)
            else:
                unconnected_nodes.append(node)
        
        # 重新定位节点
        x_offset = 0
        spacing = 300  # 根据需要调整间距
        y_connected = 0
        y_unconnected = -spacing  # 在另一行显示无连线节点
        
        # 水平排列有连线的节点
        for node in connected_nodes:
            node.location.x = x_offset
            node.location.y = y_connected
            x_offset += spacing
        
        x_offset = 0  # 重置X偏移量
        
        # 水平排列没有连线的节点
        for node in unconnected_nodes:
            node.location.x = x_offset
            node.location.y = y_unconnected
            x_offset += spacing
        
        # 添加Principled BSDF和Material Output节点
        node_tree = material.node_tree
        
        # 创建Principled BSDF节点
        bsdf_node = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf_node.location = (x_offset, y_connected)  # 将其放在有连线的节点之后
        
        # 创建Material Output节点
        output_node = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (x_offset + spacing, y_connected)
        
        # 将Principled BSDF节点连接到Material Output节点
        bsdf_output = bsdf_node.outputs['BSDF']
        output_surface = output_node.inputs['Surface']
        node_tree.links.new(bsdf_output, output_surface)
        
        # 查找标记为'Lit Color Texture'的图像纹理，并连接到Principled BSDF的Base Color
        for node in node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.label == 'Lit Color Texture':
                color_socket = bsdf_node.inputs['Base Color']
                alpha_socket = bsdf_node.inputs.get('Alpha', None)
                
                if color_socket:
                    node_tree.links.new(node.outputs['Color'], color_socket)
                
                if alpha_socket and 'Alpha' in node.outputs:
                    node_tree.links.new(node.outputs['Alpha'], alpha_socket)
        
        # 查找标记为'Normal Map Texture'的图像纹理，并连接到Principled BSDF的法线输入
        for node in node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.label == 'Normal Map Texture':
                normal_socket = bsdf_node.inputs.get('Normal', None)
                
                if normal_socket:
                    # 使用Normal Map节点将图像纹理转换为法线向量
                    normal_map_node = node_tree.nodes.new(type='ShaderNodeNormalMap')
                    normal_map_node.location = (x_offset, y_connected + spacing)
                    
                    # 将图像纹理连接到Normal Map节点
                    node_tree.links.new(node.outputs['Color'], normal_map_node.inputs['Color'])
                    
                    # 将Normal Map节点连接到Principled BSDF的法线输入
                    node_tree.links.new(normal_map_node.outputs['Normal'], normal_socket)

# 查找名为'Armature'的Armature对象（请根据实际情况修改名称）
armature = bpy.data.objects.get('Armature')

if armature and armature.type == 'ARMATURE':
    # 获取Armature及其子对象使用的所有材质
    materials_to_process = get_armature_and_children_materials(armature)
    
    # 处理这些材质
    for material in materials_to_process:
        remove_invalid_and_reposition_nodes(material)
    
    print("完成了只处理Armature及其子集的材质的操作。")
else:
    print("未找到名为'Armature'的Armature对象。")
