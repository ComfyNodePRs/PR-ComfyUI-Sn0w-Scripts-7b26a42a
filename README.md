<h1 align="center">
    sn0w-scripts
</h1>

A collection of nodes and improvements created for general ease and testing loras. These are just nodes I made and found useful, they should work with most other nodes. Most nodes that take in a prompt are made with booru tags in mind and might not work as expected with other prompts.

# Get Started

## Install

1. Install [ComfyUi](https://github.com/comfyanonymous/ComfyUI).
2. Clone this repo into `custom_nodes`:
    ```
    git clone https://github.com/sn0w12/ComfyUI-Sn0w-Scripts
    ```
3. Start up ComfyUI.

# Important Note
Many of the nodes require these paths to be in your extra_model_paths.yaml (with your real directories of course).

- loras_xl: C:/path/XL
- loras_15: C:/path/1.5

![Example](./imgs/lora_paths_example.png)

# Nodes

## Find Resolution
> An easy way to select a width and height.
> <details>
>    <summary>ℹ️ <i>See More Information</i></summary>
>
>    - Enable flip if you want to swap the resolutions
>
>    ![Find Resolution](./imgs/find_res.png)
>    </details>

## Lora Selector
> Automatically selects X amount of loras between two numbers.
> <details>
>    <summary>ℹ️ <i>See More Information</i></summary>
>
>    - Loras have to be formatted like the default kohya_ss outputs. (lora_name-000001)
>    - Select the first lora.
>    - Select the number of the highest lora you want to test.
>    - Select the amount of loras you want to test.
>    - Outputs list of loras like this: \<lora:name:strength>
>    - Add default generation adds an extra "nothing" at the end of the list, used in Lora Tester to generate an image without the lora.
> 
>    ![Lora Selector](./imgs/lora_selector.png)
>    </details>

## Lora Tester (XL)
> Automatically generates X amount of images with provided loras.
> <details>
>    <summary>ℹ️ <i>See More Information</i></summary>
>
>    - I recommend making lora_info and add_default_generation inputs and using the outputs from the Lora Selector.
>    - Takes normal KSampler input but takes positive and negative inputs as text.
>    - Outputs a batch of images.
> 
>    ![Lora Tester](./imgs/lora_tester.png)
>    </details>

## Character Selector
> Outputs a character name and prompt.
> <details>
>    <summary>ℹ️ <i>See More Information</i></summary>
>
>    - Loads `characters.json` and outputs prompt based on it.
>    - You can create a file named `custom_characters.json` and add characters there if you want, they will be loaded with all the other characters if you format it like the `characters.json` file.
> 
>    ![Character Selector](./imgs/character_selector.png)
>    </details>

## Prompt Combine
> Combines multiple strings with a specified separator and optionally simplifies the result by removing redundant or incompatible tags.
> <details>
>    <summary>ℹ️ <i>See More Information</i></summary>
>
>    - If simplify is enabled, the simplification process identifies and removes redundant tags (e.g., when a tag is fully encompassed by another, more descriptive tag) and tags incompatible with factors such as facing away, covered eyes, etc. Any tags that are in parentheses will not be removed.
>    - Simplify will also move 1girl/ 1boy to the front of the prompt to be in line with animagine 3's tagging.
> 
>    ![Prompt Combine](./imgs/prompt_combine.png)
>    </details>

## Lora Stacker
> Outputs a list of loras for Lora Tester. Does not load any loras by itself.
> <details>
>    <summary>ℹ️ <i>See More Information</i></summary>
>
>    - Basically Lora Selector but manual.
>    - Specifically for the lora testers.
> 
>    ![Lora Stacker](./imgs/lora_stacker.png)
>    </details>

## Load Lora XL/1.5
> Normal load lora but from another folder.
> <details>
>    <summary>ℹ️ <i>See More Information</i></summary>
>
>    - Add these to your extra_model_paths.yaml (for example):
>    - loras_xl: C:/path/XL
>    - loras_15: C:/path/1.5
>
>    ![Load Lora](./imgs/load_lora.png)
>    ![Example](./imgs/lora_paths_example.png)
>    </details>

## Load Lora Character
> Finds and applies the closest matching Lora model to a character based on name similarity.
> <details>
>    <summary>ℹ️ <i>See More Information</i></summary>
>
>    - The process begins by cleaning the input character string for comparison. It then searches a JSON file for a matching character name. If a match is found, it proceeds to select the appropriate folder based on the `xl` boolean flag.
>    - To find the closest Lora model, it calculates the Levenshtein distance between the character name (in full and in parts) and the filenames of available Lora models. This ensures a case-insensitive match with the best possible model.
>    - If no lora is found it just returns the input model and the workflow can continue.
>
>    ![Load Lora Character](./imgs/load_lora_character.png)
>    </details>

## Load Lora Concept
> Dynamically applies Lora models based on similarity to a provided prompt.
> <details>
>    <summary>ℹ️ <i>See More Information</i></summary>
>
>    - This node processes a given prompt to identify and apply the most similar Lora models of the tags found in the prompt. 
>    - For each part of the prompt, the node calculates a distance between tags and available Lora model filenames. Models with a difference of under 5 is applied to the input `model` and `clip`.
>    - Note: You need the loras you want to be selected to be in a folder called `concept` for this to work, they also need to be seperated into XL and 1.5 like stated in the `Important Note`.
>    - Note: Loras need to be named very similarly to the tag, with at most 5 different characters different. The words in the lora can be seperated by spaces or underscores.
>
>    ![Load Lora Concept](./imgs/load_lora_concept.png)
>    </details>

## Get Font Size Node
> Estimates the optimal font size for text to fit within an image based on Lora information.
> <details>
>    <summary>ℹ️ <i>See More Information</i></summary>
>
>    - This node takes an image and a string, estimating the best font size to ensure that the longest piece of the string fits within the image. The approach considers the image's width and the length of the text to find a size that balances visibility and fit.
>
>    ![Get Font Size](./imgs/get_font_size.png)
>    </details>


# Example Workflows
## Lora Tester
Note: Uses [ImagesGrid](https://github.com/LEv145/images-grid-comfy-plugin) for making the actual grid from the image output.

![Lora Tester](./imgs/lora_tester_workflow.png)