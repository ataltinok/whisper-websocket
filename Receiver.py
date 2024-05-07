#from pydub import AudioSegment
#import argparse
#import os
import numpy as np
#import speech_recognition as sr
#from faster_whisper import WhisperModel
import whisper
#import torch
#import json
import base64

#from datetime import datetime, timedelta, UTC
from queue import Queue
from time import sleep, time
from sys import platform

import websockets
import asyncio


class TranscriptionServer:
    
    def __init__(self, model):
        
        # The last time a recording was retrieved from the queue.
        self.phrase_time = None
        
        # Thread safe Queue for passing data from the threaded recording callback.
        self.data_queue = Queue()

        # Transcription model
        print("Downloading whisper model:", model)
        #self.audio_model = WhisperModel(model, device="cpu", compute_type="int8")
        self.audio_model = whisper.load_model(model)
        print("Model ready.")

        # Variable to store the result as it is transcribed.
        self.transcription = ['']


    async def message_recv(self, websocket):
        print("Server is running.")
        try:
            while True:
                t = time()

                ws_data = await websocket.recv()
                #print("Received data length:", len(ws_data))

                base64_bytes = ws_data.encode("utf-8")
                #print("B64 data length:", len(base64_bytes))

                audio_bytes = base64.b64decode(base64_bytes)
                #print("Bytes length:", len(audio_bytes))

                np_audio_data = np.frombuffer(audio_bytes, dtype=np.float32)
                #print("Numpy length:", len(np_audio_data))
                #print("Data range:", np.min(np_audio_data), np.max(np_audio_data))
                #print(np.any(np.isnan(np_audio_data)))  # Should be False
                #print(np.any(np.isinf(np_audio_data)))  # Should be False

                start = time()
                print("Starting transcription at", start-t)

                # TODO: Faster-whisper implementation 
                """options = dict(language="en", beam_size=5, best_of=5)
                transcribe_options = dict(task="transcribe", **options)
                segments, info = self.audio_model.transcribe(np_audio_data, **transcribe_options)
                clean_segments = list()
                for segment in segments:
                    clean_segments.append(f"{segment.start} -> {segment.end} || {segment.text}")
                print("Segment Count:",len(clean_segments))

                print("Result:\n","\n".join(clean_segments))
                print("Transcription done in", time()-start, "seconds.")
                
                await websocket.send("\n".join(clean_segments))
                """

                # Vanilla Whisper implementation
                result = self.audio_model.transcribe(np_audio_data, fp16=False, initial_prompt="".join(self.transcription))
                text = result["text"]
                self.transcription.append(text)
                print("Text:", text)
                print("Finished transcription in", time()-start)
                await websocket.send(text)
        except websockets.exceptions.ConnectionClosedOK:
            print("Connection terminated")




async def main():
    try:
        server = TranscriptionServer("medium")
        print("\nReady to operate. Deploying server...")

        ws = await websockets.serve(server.message_recv, "10.128.0.4", 3389)
        print("Ready for connections.")

        await ws.wait_closed()
    except websockets.exceptions.ConnectionClosedOK:
            print("Connection Terminated")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nUser interrupted")
