@echo off
REM Download SDXL Inpainting UNet weights
mkdir "resources\models\sdxl\inpainting\unet" 2>nul
curl -L -o "resources\models\sdxl\inpainting\unet\diffusion_pytorch_model.fp16.safetensors" https://huggingface.co/diffusers/stable-diffusion-xl-1.0-inpainting-0.1/resolve/main/unet/diffusion_pytorch_model.fp16.safetensors

REM Download SDXL VAE weights
mkdir "resources\models\sdxl\vae\sdxl-vae-fp16-fix" 2>nul
curl -L -o "resources\models\sdxl\vae\sdxl-vae-fp16-fix\diffusion_pytorch_model.safetensors" https://huggingface.co/madebyollin/sdxl-vae-fp16-fix/resolve/main/sdxl.vae.safetensors

REM (Optional) Download SDXL base model (user should add their preferred base model)
REM Example:
REM mkdir "resources\models\sdxl\main\Juggernaut XL v9" 2>nul
REM curl -L -o "resources\models\sdxl\main\Juggernaut XL v9\model_index.json" <YOUR_BASE_MODEL_JSON_URL>
REM curl -L -o "resources\models\sdxl\main\Juggernaut XL v9\unet\diffusion_pytorch_model.fp16.safetensors" <YOUR_BASE_MODEL_UNET_URL>

@echo Models download script complete. 