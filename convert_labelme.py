import argparse
import json
import os
from PIL import Image
import base64
from tqdm import tqdm

def main():
        
    parser = argparse.ArgumentParser(description='Convert Labelme json of small image to Big image')
    parser.add_argument('--inputdir', type=str, help='Labelme json folder ')
    parser.add_argument('--outputdir', type=str, help='Big image folder, new labelme json will be saved here too')

    args = parser.parse_args()

    input_dir = args.inputdir
    output_dir = args.outputdir

    for filename in tqdm(os.listdir(input_dir)):
        if "json" not in filename:
            continue
        json_path = os.path.join(input_dir, filename)
        name, ext = os.path.splitext(filename)
        with open(json_path, "r") as f:
            json_data = json.load(f)
        new_img_path = os.path.join(output_dir, f"{name}.jpg")
        
        image=Image.open(new_img_path)
        new_w, new_h = image.size
        or_w, or_h = json_data['imageWidth'], json_data['imageHeight']
        
        
        for i, shape in enumerate(json_data['shapes']):
            old_point = json_data['shapes'][i]['points']
            
            new_point = [[old_point[0][0]/or_w*new_w, old_point[0][1]/or_h*new_h], 
                        [old_point[1][0]/or_w*new_w, old_point[1][1]/or_h*new_h]]
            
            json_data['shapes'][i]['points'] = new_point
        try:
            with open(new_img_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        except:
            print(new_img_path)
            continue
        json_data['imageWidth'] = new_w
        json_data['imageHeight'] = new_h
        json_data['imagePath'] = f"{name}.jpg"
        json_data['imageData'] = encoded_string
        
        json_out = f"{output_dir}{name}.json"
        with open(json_out, "w") as out:
            json.dump(json_data, out)
        

    
if __name__ == "__main__":
    main()