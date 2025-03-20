from crewai import Agent
import json
import os
from crewai import LLM
from config.settings import MEDIA_LLM_API_KEY, MEDIA_SUBDIR, JSON_SUBDIR, ENABLE_MEDIA_LLM
from utils import save_json, log_debug

def create_media_agent(llm):
    """Create a media agent to generate images from JSON placeholders."""
    return Agent(
        role="Media Specialist",
        goal="Generate images for journaling content based on placeholders",
        backstory="""I’m a creative specialist tasked with turning text prompts into visual assets for journaling guides, 
        ensuring every image enhances the user’s experience.""",
        tools=[],
        verbose=True,
        memory=True,
        llm=llm,  # Main LLM for non-image tasks
        allow_delegation=False
    )

def _generate_placeholder(image_id, output_path):
    """Generate a placeholder image file."""
    with open(output_path, "w") as f:
        f.write(f"Placeholder image for {image_id}")
    log_debug(f"Generated placeholder for {image_id} at {output_path}")

def generate_media(self, run_dir: str, skip_generation: bool = False):
    """Generate images for placeholders listed in image_requirements JSON."""
    json_dir = os.path.join(run_dir, JSON_SUBDIR)
    media_dir = os.path.join(run_dir, MEDIA_SUBDIR)
    os.makedirs(media_dir, exist_ok=True)
    
    # Find the image_requirements file
    image_req_file = None
    for f in os.listdir(json_dir):
        if f.startswith("image_requirements_"):
            image_req_file = os.path.join(json_dir, f)
            break
    if not image_req_file or not os.path.exists(image_req_file):
        log_debug(f"No image_requirements file found in {json_dir}")
        print("No image requirements found, skipping media generation.")
        return
    
    try:
        with open(image_req_file, "r") as f:
            image_requirements = json.load(f)
        log_debug(f"Loaded image requirements from {image_req_file}")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        log_debug(f"Failed to load image_requirements: {e}")
        print("Error loading image requirements, skipping media generation.")
        return
    
    if skip_generation or not ENABLE_MEDIA_LLM:
        log_debug("Media generation skipped as per settings or request.")
        print("Media generation skipped, using placeholders.")
        for req in image_requirements:
            image_id = req["image_id"]
            output_path = os.path.join(media_dir, f"{image_id}.png")
            _generate_placeholder(image_id, output_path)
        return
    
    # Initialize separate media LLM if enabled
    try:
        media_llm = LLM(
            model="media_model_name",  # Replace with actual model when implemented
            api_key=MEDIA_LLM_API_KEY,
            base_url="https://media.api.example.com/v1",  # Replace with actual URL
            temperature=0.7
        )
        log_debug("Initialized separate media LLM for image generation.")
    except Exception as e:
        log_debug(f"Failed to initialize media LLM: {e}, falling back to placeholders.")
        print("Media LLM unavailable, using placeholders.")
        for req in image_requirements:
            image_id = req["image_id"]
            output_path = os.path.join(media_dir, f"{image_id}.png")
            _generate_placeholder(image_id, output_path)
        return
    
    # Generate images with media LLM
    for req in image_requirements:
        image_id = req["image_id"]
        prompt = req["prompt"]
        output_path = os.path.join(media_dir, f"{image_id}.png")
        
        try:
            # Uncomment and adjust when real media LLM is implemented
            # image_response = media_llm.call(prompt)
            # with open(output_path, "wb") as f:
            #     f.write(image_response)
            with open(output_path, "w") as f:  # Placeholder until real implementation
                f.write(f"Simulated image for {image_id} via media LLM")
            log_debug(f"Generated image for {image_id} at {output_path}")
        except Exception as e:
            log_debug(f"Failed to generate image for {image_id}: {e}")
            print(f"Warning: Failed to generate image {image_id}, using placeholder.")
            _generate_placeholder(image_id, output_path)
    
    log_debug(f"Media generation completed for run: {run_dir}")
    print("Media generation completed.")