import os
import shutil
import re
from gimpfu import *

def process_image(file_path, folder_path):
    image = pdb.gimp_file_load(file_path, file_path)
    pdb.plug_in_gauss(image, image.active_layer, 16, 16, 0)
    layer = pdb.gimp_image_get_active_layer(image)
    pdb.gimp_layer_flatten(layer)
    pdb.gimp_image_convert_grayscale(image)
    filename = os.path.basename(file_path)
    base_dir = os.path.dirname(folder_path)
    processing_rules = {
        "forest_jungle_01_mask": ("tree_jungle_01_c_mask.png", process_map_object_masks),
        "forest_pine_01_mask": ("tree_pine_01_a_mask.png", process_map_object_masks),
        "forestfloor_mask": ("tree_cypress_01_mask.png", process_map_object_masks),
        "desert_01_mask": ("tree_palm_01_mask.png", process_map_object_masks),
    }
    for pattern, (new_name, function) in processing_rules.items():
        if re.search(pattern, filename, re.IGNORECASE):
            new_save_path = os.path.join(base_dir, 'content_source', 'map_objects', 'masks', new_name)
            function(image, new_save_path)
            break  
    if "mask" in filename.lower():
        save_path = os.path.join(base_dir, 'gfx', 'map', 'terrain', filename)
    elif "heightmap" in filename.lower():
        save_path = os.path.join(base_dir, 'map_data', filename)
    else:
        save_path = os.path.join(folder_path, filename)
    pdb.file_png_save(image, layer, save_path, save_path, 0, 4, 1, 0, 0, 0, 0)
    pdb.gimp_image_delete(image)

def process_map_object_masks(image, save_path):
    new_image = pdb.gimp_image_duplicate(image)
    new_width = new_image.width // 2
    new_height = new_image.height // 2
    pdb.gimp_image_scale(new_image, new_width, new_height)
    new_layer = pdb.gimp_image_get_active_layer(new_image)
    pdb.file_png_save(new_image, new_layer, save_path, save_path, 0, 9, 1, 0, 0, 0, 0)
    pdb.gimp_image_delete(new_image)

def process_texture_image(file_path, folder_path):
    image = pdb.gimp_file_load(file_path, file_path)
    layer = pdb.gimp_image_get_active_layer(image)
    filename = os.path.basename(file_path)
    base_dir = os.path.dirname(folder_path)
    save_path = os.path.join(base_dir, 'gfx', 'portraits', 'accessory_variations', 'textures', os.path.splitext(filename)[0] + '.dds')
    pdb.file_dds_save(image, layer, save_path, save_path, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0)
    pdb.gimp_image_delete(image)

def process_palette_image(file_path, folder_path):
    image = pdb.gimp_file_load(file_path, file_path)
    layer = pdb.gimp_image_get_active_layer(image)
    filename = os.path.basename(file_path)
    base_dir = os.path.dirname(folder_path)
    save_path = os.path.join(base_dir, 'gfx', 'portraits', os.path.splitext(filename)[0] + '.dds')
    pdb.file_dds_save(image, layer, save_path, save_path, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0)
    pdb.gimp_image_delete(image)

def process_flatmap_image(folder_path):
    file_path = os.path.join(folder_path, 'papyrus.png')
    base_dir = os.path.dirname(folder_path)
    save_path = os.path.join(base_dir, 'gfx', 'map', 'terrain', 'flatmap.dds')
    image = pdb.gimp_file_load(file_path, file_path)
    pdb.plug_in_gauss(image, image.active_layer, 7, 7, 0)
    pdb.gimp_brightness_contrast(image.active_layer, -127, 0)
    pdb.file_dds_save(image, image.active_layer, save_path, save_path, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0)
    pdb.gimp_image_delete(image)

def process_folder(folder_path):
    # Call the new method to process the flatmap image
    process_flatmap_image(folder_path)
    
    for file in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file)
        base_dir = os.path.dirname(folder_path)
        file_mappings = {
            "default.map": 'map_data',
            "definition.csv": 'map_data',
            "provinces.png": 'map_data',
            "00_landed_titles.txt": os.path.join('common', 'landed_titles'),
            "00_province_terrain.txt": os.path.join('common', 'province_terrain'),
            "gtitles_l_english.yml": os.path.join('localization', 'english'),
            "gen_cultures_l_english.yml": os.path.join('localization', 'english', 'culture'),
            "k_generated.txt": os.path.join('history', 'provinces'),
            "hist_titles.txt": os.path.join('history', 'titles'),
            "gen_characters.txt": os.path.join('history', 'characters'),
            "gen_dynasties.txt": os.path.join('common', 'dynasties'),
            "cultural_name_lists.txt": os.path.join('common', 'culture', 'name_lists'),
            "generated_cultures.txt": os.path.join('common', 'culture', 'cultures'),
            "01_ethnicities_placeholder.txt": os.path.join('common', 'ethnicities'),
            "00_bookmarks.txt": os.path.join('common', 'bookmarks', 'bookmarks'),
            "00_bookmark_groups.txt": os.path.join('common', 'bookmarks', 'groups'),
            "generated_languages.txt": os.path.join('common', 'culture', 'pillars'),
            "generated_heritages.txt": os.path.join('common', 'culture', 'pillars'),
            "cultural_names_l_english.yml": os.path.join('localization', 'english', 'names'),
            "gen_cultural_heritages_l_english.yml": os.path.join('localization', 'english', 'culture', 'traditions'),
            "gen_cultural_languages_l_english.yml": os.path.join('localization', 'english', 'culture', 'traditions'),
            "gen_name_lists_l_english.yml": os.path.join('localization', 'english', 'culture'),
            "gen_dynasty_names_l_english.yml": os.path.join('localization', 'english', 'dynasties'),
            "gen_religions_l_english.yml": os.path.join('localization', 'english', 'religion'),
            "gen_religions.txt": os.path.join('common', 'religion', 'religions'),
            "gen_holy_sites.txt": os.path.join('common', 'religion', 'holy_sites'),
            "gen_hybrid_creation_names.txt": os.path.join('common', 'culture', 'creation_names'),
            "gen_hybrid_cultures_l_english.yml": os.path.join('localization', 'english', 'culture'),
            "building_locators.txt": os.path.join('gfx', 'map', 'map_object_data'),
            "combat_locators.txt": os.path.join('gfx', 'map', 'map_object_data'),
            "other_stack_locators.txt": os.path.join('gfx', 'map', 'map_object_data'),
            "player_stack_locators.txt": os.path.join('gfx', 'map', 'map_object_data'),
            "siege_locators.txt": os.path.join('gfx', 'map', 'map_object_data'),
            "special_building_locators.txt": os.path.join('gfx', 'map', 'map_object_data'),
            "stack_locators.txt": os.path.join('gfx', 'map', 'map_object_data')
            "activities.txt": os.path.join('gfx', 'map', 'map_object_data')
        }
        lower_file = file.lower()
        if lower_file in file_mappings:
            target_dir = os.path.join(base_dir, file_mappings[lower_file])
            target_path = os.path.join(target_dir, file)
            shutil.move(full_path, target_path)
        elif ("skin_palette" in lower_file or "eye_palette" in lower_file or "hair_palette" in lower_file):
            process_palette_image(full_path, folder_path)
        elif lower_file.endswith(".png") and ("heightmap" in lower_file or "mask" in lower_file):
            process_image(full_path, folder_path)
        elif ("color_palette" in lower_file):
            process_texture_image(full_path, folder_path)
    
    # Log message to console
    print("Your Gimp Process is complete. Don't forget to complete the rest of the steps!")

process_folder('C:\\Users\\YOURUSERNAME\\Documents\\Paradox Interactive\\Crusader Kings III\\mod\\YOURMODNAME\\replacers')
