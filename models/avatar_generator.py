import os
import random
from typing import List
from PIL import Image, ImageDraw
from models.layer import Layer
import re


class AvatarGenerator:
    def __init__(self, images_path: str):
        self.layers: List[Layer] = self.load_image_layers(images_path)
        self.background_color = (120, 150, 180)
        self.rare_background_color = (255, 255, 0)
        self.rare_background_chance = 0.01
        self.rare_chance = 0.001
        self.output_path: str = "templates/static/images"
        os.makedirs(self.output_path, exist_ok=True)
        self.nu_of_dimons =0

    def load_image_layers(self, images_path: str):
        sub_paths = sorted(os.listdir(images_path))
        layers: List[Layer] = []
        for sub_path in sub_paths:
                layer_path = os.path.join(images_path, sub_path)
                layer = Layer(layer_path)
                layers.append(layer)

        layers[0].rarity = 0.3
        layers[1].rarity = 0.3
        layers[2].rarity = 1
        layers[3].rarity = 1
        layers[4].rarity = 1
        layers[5].rarity = 1
        return layers

    def generate_image_sequence(self):
        image_path_sequence = []
        rarity_sum =0
        for layer in self.layers:
            if layer.should_generate():
                image_path , rarity = layer.get_random_image_path()
                rarity_sum+=rarity
                image_path_sequence.append(image_path)
        return image_path_sequence, rarity_sum

    def render_avatar_image(self, image_path_sequence: List[str], rarity_sum, index,timestamp, proof,  previous_hash):
        bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        while bg_color == self.rare_background_chance:
            bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        largeur=1000
        longueur=1000
        image = Image.new("RGBA", (largeur, longueur),bg_color)

        for image_path in image_path_sequence:
            layer_image = Image.open(image_path)
            m = re.search('\(([^\)]+)\)', image_path)
            m.group(0)
            rarity_sum+=float(m.group(0)[1:-1])
            print(rarity_sum)
            image = Image.alpha_composite(image, layer_image)
        raraty=0
        if random.random()<0.5:
            image, raraty= self.rarity_draw(largeur, longueur, image)
        amount = 10000
        a = int((amount / (raraty+rarity_sum)) - ((raraty+rarity_sum) * 100))
        if a < 0:
            a = 1
        season="First edition"
        image = self.print_raraty(image, raraty+rarity_sum,self.nu_of_dimons,  index,timestamp, proof,  previous_hash, season, a)
        return image, raraty+rarity_sum, self.nu_of_dimons, season, a


    def rarity_draw(self,largeur , longueur, image):
        for x in range(largeur):
            for y in range(longueur):
                    if random.random() < 0.001:
                        r = 255
                        g = 255
                        b = 0
                        image.putpixel((x, y), (r, g, b))
                        image.putpixel((x - 1, y - 1), (r, g, b))
                        image.putpixel((x - 2, y - 2), (r, g, b))
                        image.putpixel((x - 1, y), (r, g, b))
                        image.putpixel((x - 2, y), (r, g, b))
                        image.putpixel((x - 3, y), (r, g, b))
                        image.putpixel((x - 1, y - 1), (r, g, b))
                        image.putpixel((x - 2, y - 1), (255, 255, 255))
                        image.putpixel((x - 3, y - 1), (r, g, b))
                        image.putpixel((x, y - 1), (r, g, b))
                        image.putpixel((x, y - 2), (r, g, b))
                        image.putpixel((x, y - 3), (r, g, b))
                        image.putpixel((x - 1, y - 1), (255, 255, 255))
                        image.putpixel((x - 1, y - 2), (255, 255, 255))
                        image.putpixel((x - 1, y - 3), (r, g, b))
                        self.nu_of_dimons += 1
        raraty = ((self.nu_of_dimons*15) / (largeur * longueur))*400
        return image, raraty

    def  print_raraty(self, image, raraty, dimons,  index,timestamp, proof,  previous_hash, season, amount):
        ImageDraw.Draw(
            image  # Image
        ).text(
            (10, 980),  # Coordinates
            "Season : {} Number {} Created {} Rarity :{:.4f} Dimons :{} ".format(season,index ,timestamp,raraty,dimons),  # Text
            self.rare_background_color  # Color
        )
        ImageDraw.Draw(
            image  # Image
        ).text(
            (10, 990),  # Coordinates
            "{} : {}".format(previous_hash, proof,),  # Text
            self.rare_background_color  # Color
        )
        return image
    def save_image(self, image: Image.Image,previous_hash):
        image_file_name = f"{previous_hash}.png"
        image_save_path = os.path.join(self.output_path, image_file_name)
        print(image_save_path)
        image.save(image_save_path)

        self.nu_of_dimons=0

    def generate_avatar(self,  index,timestamp, proof,  previous_hash):
        print("AvatarGenerator: Generating Avatar!")
        image_path_sequence, rarity_sum = self.generate_image_sequence()
        image, raraty, dimons , season, a= self.render_avatar_image(image_path_sequence, rarity_sum, index,timestamp, proof,  previous_hash)
        self.save_image(image, previous_hash )
        print("Avatar created")
        return raraty, dimons, season, a
