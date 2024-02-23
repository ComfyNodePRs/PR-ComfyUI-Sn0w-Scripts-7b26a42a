from nodes import KSampler, KSamplerAdvanced, VAEDecode, VAEEncode, EmptyLatentImage, CLIPTextEncode
from custom_nodes.comfyui_lora_tag_loader.nodes import LoraTagLoader
from .sn0w import Utility
from comfy_extras.nodes_upscale_model import ImageUpscaleWithModel
import comfy.samplers

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

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGES",)
    FUNCTION = "sample"

    CATEGORY = "sampling"

    def sample(self, model, clip, vae, seed, steps, cfg, width, height, sampler_name, scheduler, positive, negative, denoise, lora_info, hires, upscale_model):
        k_sampler_node = KSampler()
        k_sampleradvanced_node = KSamplerAdvanced()
        vae_decode = VAEDecode()
        vae_encode = VAEEncode()
        text_encode = CLIPTextEncode()
        lora_loader = LoraTagLoader()
        utility = Utility()
        upscaler = ImageUpscaleWithModel()

        latent_image = EmptyLatentImage().generate(width, height)[0]

        loras = lora_info.split(";")
        images = []

        for lora in loras:
            modified_model, modified_clip, lora_text = lora_loader.load_lora(model, clip, lora)

            positive_prompt = text_encode.encode(modified_clip, positive)[0]
            negative_prompt = text_encode.encode(modified_clip, negative)[0]

            # Sampling
            samples = k_sampler_node.sample(modified_model, seed, steps, cfg, sampler_name, scheduler, positive_prompt, negative_prompt, latent_image, denoise)[0]

            if (hires):
                # Decode the samples
                image = vae_decode.decode(vae, samples)[0] 

                upscaled_image = upscaler.upscale(upscale_model, image)[0]
                upscaled_latent = vae_encode.encode(vae, upscaled_image)[0]
                upscaled_samples = k_sampleradvanced_node.sample(modified_model, "enable", seed, 30, cfg, sampler_name, scheduler, positive_prompt, negative_prompt, upscaled_latent, 17, 1000, "disable")[0]
                image = vae_decode.decode(vae, upscaled_samples)[0]
            else:
                image = vae_decode.decode(vae, samples)[0]

            images.append(image)

        # Dynamically construct kwargs for image_batch
        image_batch_kwargs = {f"images_{chr(97 + i)}": image for i, image in enumerate(images)}

        # Using WAS_Image_Batch to batch the images together
        batched_images = utility.image_batch(**image_batch_kwargs)
        
        return batched_images