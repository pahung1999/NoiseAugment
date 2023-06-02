import docx 
import subprocess
import os
from tqdm import tqdm
import argparse
from pdf2image import convert_from_path

import warnings
# Set the warning filter to "ignore" to skip all warnings
warnings.filterwarnings("ignore")

def main():
        
    parser = argparse.ArgumentParser(description='Convert ODT file to pdf and pdf to Big Image')
    parser.add_argument('--odt', type=str, help='odt folder ')
    parser.add_argument('--pdf', type=str, help='pdf folder ')
    parser.add_argument('--img', type=str, help='img folder ')

    args = parser.parse_args()

    odt_dir = args.odt
    pdf_dir = args.pdf
    img_dir = args.img

    print("Convert odt to pdf")
    for filename in tqdm(os.listdir(odt_dir)[:]):
        name, ext = os.path.splitext(filename)

        # Path to the input ODT file
        odt_file = os.path.join(odt_dir, filename)

        # Path to the output PDF file
        pdf_file = os.path.join(pdf_dir, f"{name}.pdf")

        # Convert ODT to PDF using unoconv
        subprocess.run(['unoconv', '-f', 'pdf', '-o', pdf_file, odt_file])


    print("Pdf to image")
    for filename in tqdm(os.listdir(pdf_dir)[:]):
        name, ext = os.path.splitext(filename)

        # Path to the output PDF file
        pdf_file = os.path.join(pdf_dir, filename)
        images = convert_from_path(pdf_file)
        
        for i, image in enumerate(images):
            image.save(f'{img_dir}{name}-{i:02d}.jpg', 'JPEG')
    
if __name__ == "__main__":
    main()