from nodes import KSampler, KSamplerAdvanced, VAEDecode, VAEEncode, EmptyLatentImage, LoraLoader, ImageScaleBy, CLIPTextEncode
from ..sn0w import Utility
from comfy_extras.nodes_upscale_model import ImageUpscaleWithModel
import comfy.samplers
import folder_paths

class LoraTestNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"model": ("MODEL",),
                    "clip": ("CLIP", ),
                    "vae": ("VAE", ),
                    "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                    "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                    "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step":0.1, "round": 0.01}),
                    "width": ("INT", {"default": 0, "min": 0}),
                    "height": ("INT", {"default": 0, "min": 0}),
                    "sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
                    "scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
                    "positive": ("STRING", {"default": ""}),
                    "negative": ("STRING", {"default": ""}),
                    "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                    "lora_info": ("STRING", {"default": ""}),
                    "hires": ("BOOLEAN", {"default": False},),
                    "upscale_model": ("UPSCALE_MODEL",),
                     }
                }

    RETURN_TYPES = ("IMAGE","INT",)
    RETURN_NAMES = ("IMAGES","TOTAL IMAGES",)
    FUNCTION = "sample"

    CATEGORY = "sampling"

    def sample(self, model, clip, vae, seed, steps, cfg, width, height, sampler_name, scheduler, positive, negative, denoise, lora_info, hires, upscale_model):
        k_sampler_node = KSampler()
        k_sampleradvanced_node = KSamplerAdvanced()
        vae_decode = VAEDecode()
        vae_encode = VAEEncode()
        text_encode = CLIPTextEncode()
        lora_loader = LoraLoader()
        upscaler = ImageUpscaleWithModel()
        scale_image = ImageScaleBy()

        latent_image = EmptyLatentImage().generate(width, height)[0]

        full_loras_list = folder_paths.get_filename_list("loras")

        loras = lora_info.split(";")
        images = []

        for lora in loras:
            # Skip empty or improperly formatted lora strings
            modified = False
            if lora.startswith("<lora:"):
                modified = True
                trimmed_string = lora[6:-1]
                parts = trimmed_string.split(':')

                if len(parts) < 2 or not parts[1]:
                    continue  # Skip if lora string is incomplete or strength is missing

                lora_name_suffix = parts[0] + ".safetensors"
                lora_strength = float(parts[1])

                # Find the full path of the lora
                full_lora_path = next((full_path for full_path in full_loras_list if lora_name_suffix in full_path), None)

                if full_lora_path:
                    modified_model, modified_clip = lora_loader.load_lora(model, clip, full_lora_path, lora_strength, lora_strength)

                positive_prompt = text_encode.encode(modified_clip, width, height, 0, 0, width, height, positive, positive)[0]
                negative_prompt = text_encode.encode(modified_clip, width, height, 0, 0, width, height, negative, negative)[0]

                # Sampling
                samples = k_sampler_node.sample(modified_model, seed, steps, cfg, sampler_name, scheduler, positive_prompt, negative_prompt, latent_image, denoise)[0]
            else:
                positive_prompt = text_encode.encode(clip, width, height, 0, 0, width, height, positive, positive)[0]
                negative_prompt = text_encode.encode(clip, width, height, 0, 0, width, height, negative, negative)[0]

                # Sampling
                samples = k_sampler_node.sample(model, seed, steps, cfg, sampler_name, scheduler, positive_prompt, negative_prompt, latent_image, denoise)[0]

            if (hires):
                # Decode the samples
                image = vae_decode.decode(vae, samples)[0]
                
                upscaled_image = upscaler.upscale(upscale_model, image)[0]
                upscaled_image = scale_image.upscale(upscaled_image, "nearest-exact", 0.5)[0]
                upscaled_latent = vae_encode.encode(vae, upscaled_image)[0]
                if modified:
                    upscaled_samples = k_sampleradvanced_node.sample(modified_model, "enable", seed, 25, cfg, sampler_name, scheduler, positive_prompt, negative_prompt, upscaled_latent, 20, 1000, "disable")[0]
                else:
                    upscaled_samples = k_sampleradvanced_node.sample(model, "enable", seed, 25, cfg, sampler_name, scheduler, positive_prompt, negative_prompt, upscaled_latent, 20, 1000, "disable")[0]
                image = vae_decode.decode(vae, upscaled_samples)[0]
            else:
                image = vae_decode.decode(vae, samples)[0]

            images.append(image)

        # Dynamically construct kwargs for image_batch
        image_batch_kwargs = {f"images_{chr(97 + i)}": image for i, image in enumerate(images)}

        # Batch the images together
        batched_images = Utility.image_batch(**image_batch_kwargs)

        return (batched_images, len(images))