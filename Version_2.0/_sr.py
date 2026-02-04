import os

def put_data_on_txt_file():
    curent_file_path = os.path.abspath(__file__)
    current_folder = os.path.dirname(curent_file_path)

    with open("D:\\main.txt", "w") as f:
        for path, dirs, files in os.walk(current_folder):
            for file in files:
                path_files = os.path.join(path, file)
                if file.endswith('.py') and file != "_sr.py":
                    if '_server' in path_files:
                        f.write("\n# Partie Serveur\n")
                    else:
                        f.write("# Partie Client\n")
                    f.write(f"# Fichier {file}\n\n")
                    with open(path_files, "r") as read_file:
                        f.write(read_file.read())



def get_number_of_lines_code_projet():
    code_line_number = 0
    curent_file_path = os.path.abspath(__file__)
    current_folder = os.path.dirname(curent_file_path)
    
    
    for path, dirs, files in os.walk(str(current_folder)):
        for file in files:
            file_path = os.path.join(path, file)
            if file_path == curent_file_path:
                continue
            
            if file.endswith('.py') or file.endswith('.kv'):
                current_file_number = 0
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        current_file_number += 1
                
                print(f"[ FICHIER {file} ] = {current_file_number}")
            
                code_line_number += current_file_number
    
    print(f"\n\n[ PROJET ] = {code_line_number} Lignes de code")
    


#get_number_of_lines_code_projet()
put_data_on_txt_file()
os.system('pause')