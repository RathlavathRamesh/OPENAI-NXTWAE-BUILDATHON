import google.generativeai as genai
from IPython.display import Markdown
import time
import os
import ffmpeg  # Correctly importing the ffmpeg-python library
from moviepy.editor import VideoFileClip
import os
# Configure the Google API Key
GOOGLE_API_KEY = ""
genai.configure(api_key=GOOGLE_API_KEY)
 
# Function to split the video into smaller chunks

def load_prompt_template(file_path=os.path.join(os.getcwd(),'prompts/video_analysis_prompt.txt')):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    
def split_video_moviepy(input_video, segment_time=600):
    output_dir = "video_chunks"
    os.makedirs(output_dir, exist_ok=True)

    video = VideoFileClip(input_video)
    duration = int(video.duration)  # total length in seconds
    chunks = []

    for i, start in enumerate(range(0, duration, segment_time)):
        end = min(start + segment_time, duration)
        chunk_path = os.path.join(output_dir, f"chunk{i:03d}.mp4")
        video.subclip(start, end).write_videofile(chunk_path, codec="libx264")
        chunks.append(chunk_path)

    return sorted(chunks)


def split_video(input_video, segment_time=600):
    output_dir = "video_chunks"
    os.makedirs(output_dir, exist_ok=True)
    
    # Splitting video into chunks using ffmpeg
    (
        ffmpeg
        .input(input_video)
        .output(f'{output_dir}/chunk%03d.mp4', f='segment', segment_time=segment_time)
        .run()
    )
    
    return sorted([f'{output_dir}/{f}' for f in os.listdir(output_dir)])
 
# Function to upload video file to Gemini
def upload_video_chunk(chunk_file):
    print(f"Uploading file: {chunk_file}")
    video_file = genai.upload_file(path=chunk_file)
    print(f"Completed upload: {video_file.uri}")
    return video_file

 
# Function to process each chunk with Gemini AI
def process_chunk_with_gemini(video_file, start_time, end_time, previous_context="", prompt_template=""):
    # Check if file is ready
    while video_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(10)
        video_file = genai.get_file(video_file.name)
    
    if video_file.state.name == "FAILED":
        raise ValueError(f"File processing failed: {video_file.state.name}")
    
    # Create the prompt for analysis and transcription
    prompt = prompt_template.format(
        previous_context=previous_context,
        start_time=start_time,
        end_time=end_time
    )
    print(f"Prompt for Gemini video analysis: {prompt}")

    # Choose the Gemini model
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")
    
    # Make the LLM request
    print("Making LLM inference request...")
    response = model.generate_content([video_file, prompt], request_options={"timeout": 600})
    
    # Print the response, rendering any Markdown
    print(Markdown(response.text))
    
    return response.text
 
# Main Function to process the entire video
def process_entire_video(video_file_name):
    # Split video into chunks
    video_chunks = split_video_moviepy(video_file_name, segment_time=600)  # 10-minute segments
    prompt_template = load_prompt_template()
    all_reports = []
    
    # Process each chunk
    for i, chunk in enumerate(video_chunks):
        start_time = i * 10  # Approx start time in minutes
        end_time = start_time + 10  # Approx end time in minutes
        
        # Upload video chunk
        video_file = upload_video_chunk(chunk)
        previous_context = "\n".join(all_reports) if all_reports else "No previous context, this is the first chunk."
        
        # Process video chunk with Gemini
        report = process_chunk_with_gemini(video_file, start_time, end_time, previous_context, prompt_template)
        all_reports.append(report)
    
    # Combine reports for the final output
    final_report = "\n\n".join(all_reports)

    os.makedirs("video_analysis_result", exist_ok=True)
    base_name = os.path.splitext(os.path.basename(video_file_name))[0]
    output_path = os.path.join("video_analysis_result", f"{base_name}.txt")
    
    # Save the final report to a file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_report)

    print(f"Final report saved as '{output_path}'")

# Call the main function to process the video


video_file_path = os.path.join(os.getcwd(),'ai_core/sample_video.mp4')
print("Looking for file at:", video_file_path)
print("Exists?", os.path.exists(video_file_path))
process_entire_video(video_file_path)