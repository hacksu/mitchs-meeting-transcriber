import json
from timeit import default_timer as timer

print("importing pytorch")
import torch
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

print("importing pyannote")
from pyannote.audio import Pipeline

print("importing huggingface stuff")
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import Dataset, Audio
from speechbox import ASRDiarizationPipeline

print("creating diarization pipeline")
auth = json.load(open("secrets.json"))["hf_token"]
diarization_pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1", use_auth_token=auth
)

print("loading distil-whisper model")
model_id = "distil-whisper/distil-medium.en"
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)
processor = AutoProcessor.from_pretrained(model_id)

print("creating whisper pipeline")
asr_pipeline = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=15,
    batch_size=16,
    torch_dtype=torch_dtype,
    device=device,
)

print("loading audio data")
audio_file = "test.mp3"
dataset = Dataset.from_dict({"audio": [audio_file]}).cast_column("audio", Audio())
sample = dataset[0]["audio"]

print("performing transcription!")
start = timer()
pipeline = ASRDiarizationPipeline(
    asr_pipeline=asr_pipeline, diarization_pipeline=diarization_pipeline
)
result = pipeline(sample.copy())
print(result)
json.dump(result, open("transcript_"+audio_file+".json", "w+", encoding="utf-8"))
print("took", timer()-start, "seconds")
