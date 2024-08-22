import os
import shutil
import re
from gimpfu import *

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def calculate_blur_factor(original_width, new_width, base_width, resolution, map_size):
    # Determine the base blur factor based on map size
    base_blur_factor = 16
    if map_size == "8192x4096":
        base_blur_factor = 16
    elif map_size == "4096x2048":
        base_blur_factor = 8  # base_blur_factor / 2
    elif map_size == "2048x1024":
        base_blur_factor = 4  # base_blur_factor / 4
    elif map_size == "1024x512":
        base_blur_factor = 2  # base_blur_factor / 8
    else:
        raise ValueError("Unexpected map size: {}".format(map_size))
    # Calculate the reduction ratio
    reduction_ratio = float(new_width) / base_width
    adjusted_blur_factor = base_blur_factor * reduction_ratio
    
    # Check if resolution matches map size
    if resolution == map_size:
        # If resolution and map size are equal, no blur should be applied
        adjusted_blur_factor = 0
    
    return int(adjusted_blur_factor)

def replace_with_black(folder_path, file_names):
    black_image_path = os.path.join(folder_path, "black1_mask.png")
    for file_name in file_names:
        file_path = os.path.join(folder_path, file_name)
        if not os.path.exists(file_path):
            shutil.copy(black_image_path, file_path)

def resize_image_to_match(src_image_path, dest_image_path):
    src_image = pdb.gimp_file_load(src_image_path, src_image_path)
    dest_image = pdb.gimp_file_load(dest_image_path, dest_image_path)
    new_width = pdb.gimp_image_width(src_image)
    new_height = pdb.gimp_image_height(src_image)
    pdb.gimp_image_scale(dest_image, new_width, new_height)
    pdb.gimp_file_save(dest_image, pdb.gimp_image_get_active_layer(dest_image), dest_image_path, dest_image_path)
    pdb.gimp_image_delete(src_image)
    pdb.gimp_image_delete(dest_image)

def read_settings(settings_file_path):
    with open(settings_file_path, 'r') as f:
        settings = f.readlines()
    
    resolution = None
    map_size = None
    
    for line in settings:
        if line.startswith("Resolution:"):
            resolution = line.split("Resolution:")[1].strip()
        elif line.startswith("Map Size:"):
            map_size = line.split("Map Size:")[1].strip()
    
    return resolution, map_size

def process_image(file_path, folder_path, resolution, map_size):
    filename = os.path.basename(file_path)
    image = pdb.gimp_file_load(file_path, file_path)
    original_width = pdb.gimp_image_width(image)
    new_width = pdb.gimp_image_width(image)
    base_width = 8192  # Assuming base width is 8192 for calculations
    blur_factor = calculate_blur_factor(original_width, new_width, base_width, resolution, map_size)
    if blur_factor == 0 and ("heightmap" in filename.lower()):
        blur_factor = 4
    if blur_factor > 0:
        pdb.plug_in_gauss(image, image.active_layer, blur_factor, blur_factor, 0)
    layer = pdb.gimp_image_get_active_layer(image)
    pdb.gimp_layer_flatten(layer)
    pdb.gimp_image_convert_grayscale(image)
    base_dir = os.path.dirname(folder_path)
    processing_rules = {
        "forest_jungle_01_mask": ("tree_jungle_01_c_mask.png", process_map_object_masks),
        "forest_pine_01_mask": ("tree_pine_01_a_mask.png", process_map_object_masks),
        "forestfloor_mask": ("tree_cypress_01_mask.png", process_map_object_masks),
        "black1_mask": ("tree_palm_01_mask.png", process_map_object_masks),
        "black1_mask": ("reeds_01_mask.png", process_map_object_masks),
        "black2_mask": ("steppe_bush_01_mask.png", process_map_object_masks),
        "black3_mask": ("tree_jungle_01_d_mask.png", process_map_object_masks),
        "black4_mask": ("tree_leaf_01_c_mask.png", process_map_object_masks),
        "black5_mask": ("tree_leaf_01_mask.png", process_map_object_masks),
        "black6_mask": ("tree_leaf_01_single_mask.png", process_map_object_masks),
        "black7_mask": ("tree_leaf_02_mask.png", process_map_object_masks),
        "black8_mask": ("tree_pine_01_b_mask.png", process_map_object_masks),
        "black9_mask": ("tree_pine_impassable_01_a_mask.png", process_map_object_masks)
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
    dest_image_path = os.path.join(base_dir, 'gfx', 'map', 'terrain', 'flatmap.dds')
    # Resize the destination image first
    resize_image_to_match(file_path, dest_image_path)
    # Load images and calculate the blur factor
    replacers_image = pdb.gimp_file_load(file_path, file_path)
    original_width = pdb.gimp_image_width(replacers_image)
    new_width = pdb.gimp_image_width(replacers_image)
    resolution, map_size = read_settings(os.path.join(folder_path, 'settings.txt'))
    blur_factor = calculate_blur_factor(original_width, new_width, 8192, resolution, map_size)
    # Apply blur and save
    if blur_factor > 0:
        pdb.plug_in_gauss(replacers_image, replacers_image.active_layer, blur_factor, blur_factor, 0)
    pdb.gimp_brightness_contrast(replacers_image.active_layer, -127, 0)
    pdb.file_dds_save(replacers_image, replacers_image.active_layer, dest_image_path, dest_image_path, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0)
    pdb.gimp_image_delete(replacers_image)

def replace_rivers_image(folder_path):
    base_dir = os.path.dirname(folder_path)
    replacers_image_path = os.path.join(folder_path, "rivers.png")
    replacers_image = pdb.gimp_file_load(replacers_image_path, replacers_image_path)
    replacers_layer = pdb.gimp_image_get_active_layer(replacers_image)
    map_data_image_path = os.path.join(base_dir, 'map_data', "rivers.png")
    # Resize the destination image first
    resize_image_to_match(replacers_image_path, map_data_image_path)
    # Now process and paste the image from the replacers folder
    map_data_image = pdb.gimp_file_load(map_data_image_path, map_data_image_path)
    map_data_layer = pdb.gimp_image_get_active_layer(map_data_image)
    pdb.gimp_edit_copy(replacers_layer)
    floating_sel = pdb.gimp_edit_paste(map_data_layer, True)
    pdb.gimp_floating_sel_anchor(floating_sel)
    pdb.file_png_save(map_data_image, map_data_layer, map_data_image_path, map_data_image_path, 0, 4, 1, 0, 0, 0, 0)
    pdb.gimp_image_delete(replacers_image)
    pdb.gimp_image_delete(map_data_image)

def process_folder(folder_path):
    settings_file_path = os.path.join(folder_path, 'settings.txt')
    resolution, map_size = read_settings(settings_file_path)
    
    create_folder_if_not_exists(os.path.join(folder_path, '..', 'gfx', 'FX'))
    unused_files = [
        "beach_02_mask.png",
		"beach_02_mediterranean_mask.png",
        "beach_02_pebbles_mask.png",
        "black2_mask.png",
		"black3_mask.png",
		"black4_mask.png",
		"black5_mask.png",
		"black6_mask.png",
		"black7_mask.png",
		"black8_mask.png",
		"black9_mask.png",
		"coastline_cliff_brown_mask.png",
		"coastline_cliff_desert_mask.png",
		"coastline_cliff_grey_mask.png",
		"desert_01_mask.png",
		"desert_02_mask.png",
		"desert_cracked_mask.png",
		"desert_flat_01_mask.png",
		"desert_rocky_mask.png",
		"desert_wavy_01_mask.png",
		"drylands_01_cracked_mask.png",
		"drylands_01_grassy_mask.png",
		"drylands_01_mask.png",
		"farmlands_01_mask.png",
		"floodplains_01_mask.png",
		"forest_jungle_01_mask.png",
		"forest_leaf_01_mask.png",
		"forest_pine_01_mask.png",
		"forestfloor_02_mask.png",
		"forestfloor_mask.png",
		"hills_01_mask.png",
		"hills_01_rocks_mask.png",
		"hills_01_rocks_medi_mask.png",
		"hills_01_rocks_small_mask.png",
		"india_farmlands_mask.png",
		"medi_dry_mud_mask.png",
		"medi_farmlands_mask.png",
		"medi_grass_01_mask.png",
		"medi_grass_02_mask.png",
		"medi_hills_01_mask.png",
		"medi_lumpy_grass_mask.png",
		"medi_noisy_grass_mask.png",
		"mountain_02_b_mask.png",
		"mountain_02_c_mask.png",
		"mountain_02_d_mask.png",
		"mountain_02_d_snow_mask.png",
		"mountain_02_d_valleys_mask.png",
		"mountain_02_desert_c_mask.png",
		"mountain_02_desert_mask.png",
		"mountain_02_mask.png",
		"mountain_02_snow_mask.png",
		"mud_wet_01_mask.png",
		"northern_hills_01_mask.png",
		"northern_plains_01_mask.png",
		"oasis_mask.png",
		"plains_01_desat_mask.png",
		"plains_01_dry_mask.png",
		"plains_01_dry_mud_mask.png",
		"plains_01_mask.png",
		"plains_01_noisy_mask.png",
		"plains_01_rough_mask.png",
		"snow_mask.png",
		"steppe_01_mask.png",
		"steppe_bushes_mask.png",
		"steppe_rocks_mask.png",
		"wetlands_02_mask.png",
		"wetlands_02_mud_mask.png"
    ]
    replace_with_black(folder_path, unused_files)
    process_flatmap_image(folder_path)
    replace_rivers_image(folder_path)
    
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
            "stack_locators.txt": os.path.join('gfx', 'map', 'map_object_data'),
            "activities.txt": os.path.join('gfx', 'map', 'map_object_data'),
            "tree_cypress_01_generator_1.txt": os.path.join('gfx', 'map', 'map_object_data', 'generated'),
            "tree_jungle_01_c_generator_1.txt": os.path.join('gfx', 'map', 'map_object_data', 'generated'),
            "tree_palm_generator_1.txt": os.path.join('gfx', 'map', 'map_object_data', 'generated'),
            "tree_pine_01_a_generator_1.txt": os.path.join('gfx', 'map', 'map_object_data', 'generated'),
	        "gen_game_start.txt": os.path.join('common', 'on_action'),
            "01_gen_defines.txt": os.path.join('common', 'defines'),
            "heightmap.heightmap": 'map_data',
	        "pdxterrain.shader": os.path.join('gfx', 'fx'),
	        "pdxwater.shader": os.path.join('gfx', 'fx')
        }
        lower_file = file.lower()
        if lower_file in file_mappings:
            target_dir = os.path.join(base_dir, file_mappings[lower_file])
            target_path = os.path.join(target_dir, file)
            shutil.move(full_path, target_path)
        elif ("skin_palette" in lower_file or "eye_palette" in lower_file or "hair_palette" in lower_file):
            process_palette_image(full_path, folder_path)
        elif lower_file.endswith(".png") and ("heightmap" in lower_file or "mask" in lower_file):
            process_image(full_path, folder_path, resolution, map_size)
        elif ("color_palette" in lower_file):
            process_texture_image(full_path, folder_path)
    
    print("Your Gimp Process is complete. Don't forget to complete the rest of the steps!")

process_folder('C:\\Users\\YOURUSERNAME\\Documents\\Paradox Interactive\\Crusader Kings III\\mod\\YOURMODNAME\\replacers')
