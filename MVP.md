# MouthStudio Backend - MVP Execution Guide

## 🎯 Objective
Membangun backend MVP untuk aplikasi MouthStudio menggunakan FastAPI. 
Fokus utama: Menerima file audio (senandung), mengirimkannya ke Hugging Face API (Spotify Basic Pitch), dan merakit responsnya menjadi file `.mid` menggunakan Python.

## 🛠️ Tech Stack
- Framework: FastAPI
- Server: Uvicorn
- AI Integration: `requests` (Hugging Face API)
- MIDI Generation: `mido`, `pretty_midi`
- Auth: OAuth2 with JWT (via `python-jose`, `passlib`) - *To be implemented after core magic.*

---

## 🚀 Copilot Execution Steps (Vibe Coding Prompts)

Ikuti langkah-langkah di bawah ini secara berurutan. Gunakan teks yang dicetak tebal sebagai prompt untuk GitHub Copilot.

### Phase 1: Environment & Setup
1. Buat file `requirements.txt`.
2. Gunakan prompt Copilot berikut:
   **"Generate a requirements.txt file for a FastAPI project that includes uvicorn, python-multipart for file uploads, requests, mido, pretty_midi, python-jose[cryptography], and passlib[bcrypt]."**
3. Jalankan `pip install -r requirements.txt` di terminal.

### Phase 2: Core Application Setup
1. Buat file `main.py`.
2. Gunakan prompt Copilot berikut di baris pertama:
   **"Create a basic FastAPI application instance. Add a root GET endpoint '/' that returns a JSON welcome message for the MouthStudio API. Include CORS middleware allowing all origins for local development."**

### Phase 3: AI Service Module (Hugging Face)
1. Buat folder `services/` dan buat file `services/ai_service.py`.
2. Gunakan prompt Copilot berikut:
   **"Write an async Python function named `extract_pitch_from_audio(file_path: str) -> dict`. This function should read a local audio file and send a POST request to the Hugging Face Inference API for the model 'spotify/basic-pitch'. Use an environment variable 'HF_API_KEY' for the Authorization header. Handle request timeouts and return the JSON response."**

### Phase 4: MIDI Builder Module
1. Buat file `services/midi_builder.py`.
2. Gunakan prompt Copilot berikut:
   **"Write a Python function named `generate_midi_from_pitch(pitch_data: dict, output_filename: str) -> str`. Use the 'mido' library to create a new MIDI file with a single track. Assume 'pitch_data' contains a list of notes with start time, end time, and pitch/frequency. Convert these to 'note_on' and 'note_off' MIDI messages. Save the file to a local 'temp_midi' directory and return the absolute file path."**
   *(Note: Kita akan melakukan penyesuaian logika parsing JSON di sini nanti setelah melihat struktur asli dari Basic Pitch).*

### Phase 5: The Upload Endpoint (Connecting the Dots)
1. Buka kembali `main.py` (atau buat `routers/audio.py` jika ingin rapi).
2. Gunakan prompt Copilot berikut:
   **"Create a POST endpoint '/api/v1/studio/process-audio/'. It should accept an UploadFile (audio/wav or audio/m4a). Implement the following logic: 1) Save the UploadFile temporarily to a 'temp_audio' folder using a UUID for the filename. 2) Call the `extract_pitch_from_audio` service. 3) Pass the result to `generate_midi_from_pitch`. 4) Delete the temporary audio file. 5) Return a FileResponse of the generated .mid file so the client can download it directly."**

### Phase 6: Run & Test
1. Pastikan struktur folder `temp_audio` dan `temp_midi` sudah dibuat atau ditangani secara dinamis oleh kode.
2. Jalankan server lokal: `uvicorn main:app --reload`
3. Gunakan Postman, cURL, atau Swagger UI bawaan FastAPI (`http://127.0.0.1:8000/docs`) untuk menguji endpoint upload dengan merekam suaramu sendiri.