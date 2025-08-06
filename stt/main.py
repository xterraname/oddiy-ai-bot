import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import torchaudio
import tempfile
from typing import Dict
import uvicorn

# === Logging ===
os.makedirs("logs", exist_ok=True)

file_handler = logging.FileHandler("logs/stt.log", encoding="utf-8")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
)

# Root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.handlers = [file_handler]


logger = logging.getLogger(__name__)

# Uvicorn logger
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.setLevel(logging.INFO)
uvicorn_logger.handlers = [file_handler]
uvicorn_logger.propagate = False


def initialize_model():
    """Loading and configuring the model"""
    global model, processor, device

    model_name = "sarahai/uzbek-stt-3"
    logger.info("Loading model...")

    try:
        model = Wav2Vec2ForCTC.from_pretrained(model_name)
        processor = Wav2Vec2Processor.from_pretrained(model_name)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        logger.info(f"The model was successfully loaded. Device: {device}")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_model()
    yield
    logger.info("Closing the application...")


# FastAPI ilovasini yaratish
app = FastAPI(
    title="Speech-to-Text API",
    description="API for converting audio files to text in Uzbek",
    version="1.0.0",
    lifespan=lifespan,
)

# Global o'zgaruvchilar
model = None
processor = None
device = None


def load_and_preprocess_audio(file_path: str):
    """Upload and process an audio file"""
    try:
        speech_array, sampling_rate = torchaudio.load(file_path)
        if sampling_rate != 16000:
            resampler = torchaudio.transforms.Resample(
                orig_freq=sampling_rate, new_freq=16000
            )
            speech_array = resampler(speech_array)
        return speech_array.squeeze().numpy()
    except Exception as e:
        logger.error(f"Audio file not processed: {e}")
        raise HTTPException(
            status_code=400, detail=f"Audio file not processed: {str(e)}"
        )


def replace_unk(transcription: str) -> str:
    """[UNK] token exchange"""
    return transcription.replace("[UNK]", "ʼ")


def transcribe_audio(audio_array) -> str:
    """Convert audio array to text"""
    try:
        input_values = processor(
            audio_array, sampling_rate=16000, return_tensors="pt"
        ).input_values.to(device)

        with torch.no_grad():
            logits = model(input_values).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)

        return replace_unk(transcription[0])
    except Exception as e:
        logger.error(f"Error during transcription process: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error during transcription process: {str(e)}"
        )


@app.get("/")
async def root():
    """Asosiy sahifa"""
    return {
        "message": "Uzbek Speech-to-Text API",
        "version": "1.0.0",
        "endpoints": {
            "/transcribe": "POST - Convert audio file to text",
            "/health": "GET - Check service status",
        },
    }


@app.get("/health")
async def health_check():
    """Check service status"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": str(device) if device else "unknown",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/transcribe")
async def transcribe_speech(file: UploadFile = File(...)) -> Dict:
    """
    Convert audio file to text
    """
    if model is None or processor is None:
        raise HTTPException(
            status_code=503, detail="The model has not been loaded yet."
        )

    allowed_formats = [".wav", ".mp3", ".ogg", ".flac", ".m4a", ".oga"]
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_formats:
        logger.warning(f"Unsupported file format: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed formats: {', '.join(allowed_formats)}",
        )

    start_time = datetime.now()
    logger.info(f"File received: {file.filename}")

    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=file_extension
        ) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            speech_array = load_and_preprocess_audio(temp_file_path)

            transcription_text = transcribe_audio(speech_array)

            processing_time = datetime.now() - start_time
            logger.info(
                f"Transcription completed in {processing_time.total_seconds()}s"
            )

            return JSONResponse(
                content={
                    "success": True,
                    "transcription": transcription_text,
                    "filename": file.filename,
                    "processing_time_seconds": processing_time.total_seconds(),
                    "timestamp": datetime.now().isoformat(),
                }
            )

        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Kutilmagan xato: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8585, reload=False, log_config=None)
