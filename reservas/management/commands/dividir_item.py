import os
import json

def split_json_file(file_path, chunk_size_mb=150):
    output_dir = os.path.dirname(file_path)
    base_name = os.path.basename(file_path).split('.')[0]

    chunk_size = chunk_size_mb * 1024 * 1024  # Convert MB to bytes
    file_count = 0
    buffer = []
    buffer_size = 0

    with open(file_path, 'r', encoding='utf-8') as json_file:
        json_file.readline()  # Skip the initial '[' character

        while True:
            current_line = json_file.readline()
            if not current_line:
                break  # Final del archivo
            if current_line.strip() == "]":
                continue  # Omitir la última línea del archivo

            buffer.append(current_line.strip())
            buffer_size += len(current_line.encode('utf-8'))  # Estimación más precisa del tamaño en bytes

            if buffer_size >= chunk_size:
                write_to_file(buffer, output_dir, base_name, file_count)
                file_count += 1
                buffer = []
                buffer_size = 0

        if buffer:
            write_to_file(buffer, output_dir, base_name, file_count)

def write_to_file(buffer, output_dir, base_name, file_count):
    output_file_path = os.path.join(output_dir, f"{base_name}_part_{file_count}.json")
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        if buffer:
            # Asegura que el primer objeto aparezca en la misma línea que el corchete de apertura
            output_file.write("[")
            output_file.write(buffer[0])
            if len(buffer) > 1:
                output_file.write("\n" + "\n".join(buffer[1:]))
            output_file.write("\n]")


split_json_file('/home/tvacation/thatvacation/json/flatfile_usa_items.json', chunk_size_mb=150)
