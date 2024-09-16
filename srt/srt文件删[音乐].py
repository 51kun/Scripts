import os

def remove_subtitles_by_keywords(folder_path, keywords):
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith(".srt"):
            file_path = os.path.join(folder_path, filename)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # 删除含有指定关键词的行
            updated_lines = [line for line in lines if not any(keyword in line for keyword in keywords)]

            # 将处理后的内容写回文件，覆盖原文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(updated_lines)
            print(f"{filename} 已更新.")

# 需要删除的字符串列表
keywords_to_remove = ["[音乐]", "[音乐", "音乐]","[","]","]["]

# 文件夹路径
folder_A = r"C:\Users\wuwuy\Videos\TubeGet\LUCASの存在。 - 视频"
remove_subtitles_by_keywords(folder_A, keywords_to_remove)
