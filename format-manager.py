from PIL import Image
import zipfile
import os

def convert_to_cbz(input_folder, output_cbz):
    with zipfile.ZipFile(output_cbz, 'w') as cbz_file:
        for file_name in sorted(os.listdir(input_folder)):
            if file_name.lower().endswith('.jpg'):
                image_path = os.path.join(input_folder, file_name)
                with Image.open(image_path) as img:
                    cbz_file.write(image_path, os.path.basename(image_path))


#input_folder = 'D:\j'
#output_cbz = 'D:\j\output.cbz'

#convert_to_cbz(input_folder, output_cbz)