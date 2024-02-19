import os
import json
import re
import folder_paths
from nodes import LoraLoader
from .print_sn0w import print_sn0w

class LoadLoraCharacterNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP", ),
                "character": ("STRING", {"default": ""}),
                "xl": ("BOOLEAN", {"default": False},),
                "lora_strength": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
            },
        }

    RETURN_TYPES = ("MODEL", "CLIP",)
    RETURN_NAMES = ("MODEL", "CLIP",)
    FUNCTION = "find_and_apply_lora"
    CATEGORY = "sn0w"

    def levenshtein_distance(self, s1, s2):
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def clean_string(self, input_string):
        # Remove parentheses and escape characters
        cleaned_string = re.sub(r'[\\()]', '', input_string)
        # Remove patterns like ':1.2'
        cleaned_string = re.sub(r':\d+(\.\d+)?', '', cleaned_string)
        # Remove trailing commas
        cleaned_string = re.sub(r',$', '', cleaned_string.strip())
        # Convert to lowercase for case-insensitive comparison
        return cleaned_string.lower()
        
    def find_and_apply_lora(self, model, clip, character, xl, lora_strength):
        dir_path = os.path.dirname(os.path.realpath(__file__)).replace("\\src", "")
        json_path = os.path.join(dir_path, 'characters.json')
        with open(json_path, 'r') as file:
            character_data = json.load(file)

        character_name = None
        cleaned_character = self.clean_string(character)

        for char in character_data:
            cleaned_associated_string = self.clean_string(char['associated_string'])
            if cleaned_associated_string == cleaned_character:
                character_name = char['name']
                break

        if character_name:
            lora_loader = LoraLoader()

            full_lora_path = folder_paths.get_filename_list("loras")

            # Select the appropriate lora list based on 'xl'
            lora_paths = folder_paths.get_filename_list("loras_xl" if xl else "loras_15")

            # Extract just the filenames for comparison
            lora_filenames = [path.split('\\')[-1] for path in lora_paths]

            character_name_lower = character_name.lower()
            character_name_parts = character_name_lower.split()
            closest_match = None
            lowest_distance = float('inf')

            for filename in lora_filenames:
                # Convert filename to lowercase for case-insensitive comparison and remove file extension.
                filename_lower = os.path.splitext(filename.lower())[0]

                if any(part in filename_lower for part in character_name_parts):
                    # Calculate the Levenshtein distance for the full character name as one of the metrics.
                    full_name_distance = self.levenshtein_distance(character_name_lower, filename_lower)
                    
                    # Calculate the distances for each part of the character name and choose the lowest.
                    parts_distance = min(self.levenshtein_distance(part, filename_lower) for part in character_name_parts)
                    
                    # Use the minimum of full name distance and parts distance as the total distance.
                    total_distance = min(full_name_distance, parts_distance)

                    # Determine which distance was used for the total distance and print accordingly.
                    if total_distance == full_name_distance:
                        print_sn0w("Full Name Distance: " + str(full_name_distance) + " Lora: " + filename + " Name: " + character_name_lower)
                    else:
                        print_sn0w("Part Name Distance: " + str(parts_distance) + " Lora: " + filename + " Name: " + str(character_name_parts))

                    if total_distance < lowest_distance:
                        lowest_distance = total_distance
                        closest_match = filename

            # Find the full path for the closest match
            if closest_match is not None:
                lora_path = next((full_path for full_path in full_lora_path if closest_match.lower() in full_path.lower()), None)
            else:
                lora_path = None

            if lora_path:
                print_sn0w(lora_path)
                model, clip = lora_loader.load_lora(model, clip, lora_path, lora_strength, lora_strength)
            else:
                print_sn0w("No matching Lora found for the character.")

        return model, clip