import os
from flask import Flask, request, jsonify, send_file, render_template
from PIL import Image
import torch
from diffusers import StableDiffusionPipeline
from clip_interrogator import Config, Interrogator
from transformers import pipeline
from pyngrok import ngrok 

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


device = "cuda" if torch.cuda.is_available() else "cpu"

torch_dtype = torch.float16 if device == "cuda" else torch.float32

print(f"Using device: {device}, torch_dtype: {torch_dtype}")


ci = Interrogator(Config(
    clip_model_name="ViT-L-14/openai",
    device=device
))


model_file = "custom_model.safetensors"
if os.path.exists(model_file):
    pipe = StableDiffusionPipeline.from_single_file(
        model_file,
        torch_dtype=torch_dtype,
        safety_checker=None
    ).to(device)
else:
    print(f"WARNING: Model file '{model_file}' not found. Loading default pretrained model.")
    pipe = StableDiffusionPipeline.from_pretrained(
        "CompVis/stable-diffusion-v1-4",
        torch_dtype=torch_dtype,
        safety_checker=None
    ).to(device)


summarizer = pipeline("summarization", model="t5-base")

@app.route("/generate", methods=["POST"])
def generate():
    files = request.files.getlist("images")
    if not files:
        return jsonify({"error": "No images provided."}), 400
    if len(files) > 5:
        return jsonify({"error": "Maximum 5 images allowed."}), 400

    
    image_paths = []
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        image_paths.append(file_path)

   
    prompts = []
    for path in image_paths:
        image = Image.open(path).convert("RGB")
        prompt = ci.interrogate(image)
        prompts.append(prompt)

    
    additional_prompt = request.form.get("additional_prompt", "").strip()
    combined_prompt = "Combine into a Stable Diffusion prompt: " + ", ".join(prompts)
    if additional_prompt:
        combined_prompt += ", " + additional_prompt

    
    summary_text = summarizer(combined_prompt, max_length=70, min_length=30, do_sample=False)[0]['summary_text']
    summary_text += ", best quality, high resolution"

    
    result = pipe(
        summary_text,
        negative_prompt="(deformed iris, deformed pupils, extra fingers), text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck",
        num_inference_steps=50,
        guidance_scale=7.5,
        width=512,
        height=512,
        generator=torch.Generator(device=device).manual_seed(42)
    ).images[0]

   
    output_path = os.path.join(OUTPUT_FOLDER, "output.png")
    result.save(output_path)
    return send_file(output_path, mimetype="image/png")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    
    port = 5000

    
    public_url = ngrok.connect(port)
    print("Public URL:", public_url.public_url)
    
    
    app.run(port=port)


