import argparse
from tqdm import tqdm
import os
from PIL import Image
import numpy as np
from shapely.geometry import Polygon
import random
import json
import base64
from io import BytesIO


def image_convert(noise_img, or_img, size_max = 0.2):
    #Noise image augment
    or_w, or_h = or_img.size
    MAX_SIZE = (int(or_w*np.random.uniform(0.1, size_max)), 
                int(or_h*np.random.uniform(0.1, size_max)))
    noise_img.thumbnail(MAX_SIZE)
    noise_w, noise_h = noise_img.size

    #Noise image position
    start_point = [np.random.randint(1, or_w), 
                   np.random.randint(1, or_h)]
    end_point = [start_point[0]+noise_w, start_point[1]+noise_h]
    if end_point[0] > or_w:
        end_point[0] = or_w
    if end_point[1] > or_h:
        end_point[1] = or_h
        
    while end_point[0]-start_point[0]<0.5*noise_w or end_point[1]-start_point[1]<0.5*noise_h:
        start_point = [np.random.randint(1, or_w), 
                   np.random.randint(1, or_h)]
        end_point = [start_point[0]+noise_w, start_point[1]+noise_h]
        if end_point[0] > or_w:
            end_point[0] = or_w
        if end_point[1] > or_h:
            end_point[1] = or_h
    
    #Noise image polygon
    noise_polygon = [[start_point[0], start_point[1]],
                    [end_point[0], start_point[1]],
                     [end_point[0], end_point[1]],
                    [start_point[0], end_point[1]]]
    return noise_img, noise_polygon

def check_over_polygon(polygon1, polygon2):
    polygon_A = Polygon(polygon1)
    polygon_B = Polygon(polygon2)

    # A,B intersects check
    return polygon_A.intersects(polygon_B)
        
def check_noise_on_polygons(noise_polygon, polygons):
    for polygon in polygons:
        if check_over_polygon(noise_polygon, polygon):
            return True
    return False
    
def noise_insert(or_img, shapes, noise_list, max_noise = 10):
    #Get polygons list from shapes
    polygons = []
    for i, shape in enumerate(shapes):
        x = shape['points']
        polygon = [[x[0][0],x[0][1]],
                   [x[1][0],x[0][1]],
                   [x[1][0],x[1][1]],
                   [x[0][0],x[1][1]]]
        polygons.append(polygon)
    
    num_noise = np.random.randint(3, max_noise)
    #Chèn noise
    max_loop = 10000
    for i in range(num_noise):
        noise_img, noise_polygon = image_convert(random.choice(noise_list), or_img, size_max = 0.4)
        while check_noise_on_polygons(noise_polygon, polygons) and max_loop>0:
            max_loop -=1
            noise_img, noise_polygon = image_convert(random.choice(noise_list), or_img, size_max = 0.4)
            
        if max_loop <= 0:
            break
        or_img.paste(noise_img, (noise_polygon[0][0], noise_polygon[0][1]))
        polygons.append(noise_polygon)
        shapes.append({'description': '',
                     'label': 'noise',
                     'points': [[noise_polygon[0][0], noise_polygon[0][1]],
                      [noise_polygon[2][0], noise_polygon[2][1]]],
                     'group_id': None,
                     'shape_type': 'rectangle',
                     'flags': {}})
        
    return or_img, shapes

def main():
        
    parser = argparse.ArgumentParser(description='Augment Image with noise from Labelme json file and Image file')
    parser.add_argument('--inputdir', type=str, help='Input folder with labelme jsonfile and image ')
    parser.add_argument('--outputdir', type=str, help='Output folder with new labelme jsonfile and image ')
    parser.add_argument('--noisedir', type=str, default='./noise_img/', help='Noise images folder')
    parser.add_argument('--maxnoise', type=int, default=10, help='Max noise per image')

    args = parser.parse_args()

    input_dir = args.inputdir
    output_dir = args.outputdir
    noise_dir = args.noisedir
    max_noise = args.maxnoise

    print("Load noise image")
    noise_list = []
    for filename in tqdm(os.listdir(noise_dir)):
        noise_path = os.path.join(noise_dir, filename)
        image = Image.open(noise_path)
        noise_list.append(image)

    print("Augment Image and Labelme json")
    for filename in tqdm(os.listdir(input_dir)):
        if "json" not in filename:
            continue
        json_path = os.path.join(input_dir, filename)
        name, ext = os.path.splitext(filename)
        img_path = os.path.join(input_dir, f"{name}.jpg")
        or_img = Image.open(img_path)
        
        with open(json_path, "r") as f:
            json_data = json.load(f)
        shapes = json_data['shapes']
        new_img, new_shapes = noise_insert(or_img, shapes, noise_list, max_noise = max_noise)
        
        json_data['shapes'] = new_shapes
        
        buffered = BytesIO()
        new_img.save(buffered, format="JPEG")
        encoded_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
        json_data['imageData'] = encoded_string
        json_data['imagePath'] = f"{name}_noise.jpg"
        
        
        img_out_path = os.path.join(output_dir, f"{name}_noise.jpg")
        new_img.save(img_out_path)
        json_out_path = os.path.join(output_dir, f"{name}_noise.json")
        with open(json_out_path, "w") as out:
            json.dump(json_data, out) 
        

    
if __name__ == "__main__":
    main()
