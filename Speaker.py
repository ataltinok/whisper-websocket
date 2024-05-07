import websockets
import asyncio
import base64
import json
import numpy as np
from scipy.signal import resample

import pyaudio

p = pyaudio.PyAudio()
FRAMES_PER_BUFFER = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = int(p.get_device_info_by_index(0)["defaultSampleRate"])

class Speaker:
		
	def __init__(self, URL, CHUNK_DURATION):
		# the endpoint we're going to hit
		self.URL = URL
		self.transcription = list()
		self.num_iterations = int(RATE / FRAMES_PER_BUFFER * CHUNK_DURATION) # Sends CHUNK_SECONDS second chunks, i.e. the audio is transcribed every CHUNK_SECONDS seconds.

	def add_line(self, text):
		self.transcription.append(text)

	def close(self):
		self.stream.stop_stream()
		self.stream.close()
		p.terminate()
	
	async def send_receive(self):

		print(f'Connecting websocket to url {self.URL}')

		async with websockets.connect(
			self.URL,
			ping_interval=1100,
			ping_timeout=1000
		) as _ws:

			# starts recording
			self.stream = p.open(
			format=FORMAT,
			channels=CHANNELS,
			rate=RATE,
			input=True,
			frames_per_buffer=FRAMES_PER_BUFFER)

			# Send audio as np array encoded to a format suitable for websocket
			async def send():
				try:
					while True:
						#audio_data = [self.stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)]
						audio_data = list()

						for _ in range(self.num_iterations):
							# Read data from the stream for CHUNK_DURATION seconds.
							data = self.stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
							audio_data.append(data)
						# Converting to Whisper format 
						np_audio_data = np.frombuffer(b''.join(audio_data), dtype=np.int16).astype(np.float32) / 32768.0
						np_audio_data.setflags(write=True)
						audio_data_16k = resample(np_audio_data, int(len(np_audio_data) * 16000 / 48000))

						#print("Numpy length:", len(audio_data_16k))
						#print("Data range:", np.min(audio_data_16k), np.max(audio_data_16k))
						#print(np.any(np.isnan(audio_data_16k)))  # Should be False
						#print(np.any(np.isinf(audio_data_16k)))  # Should be False
						
						# Encoding for websocket suitability. Should be decoded on the server side.
						audio_bytes = audio_data_16k.tobytes()
						#print("Bytes length:", len(audio_bytes))

						b64_bytes = base64.b64encode(audio_bytes)
						#print("B64 length:", len(b64_bytes))

						ws_data = b64_bytes.decode("utf-8")
						#print("Transmitted data length:", len(ws_data))

						print("Sending audio")
						await _ws.send(ws_data)
				except websockets.exceptions.ConnectionClosedOK:
					print("Connection terminated while sending")

			# Receive transcribed audio
			async def receive():
				try:
					while True:
						result_str = await _ws.recv()
						print(result_str)
						self.transcription.append(result_str)
				except websockets.exceptions.ConnectionClosedOK:
					print("Connection Terminated while receiving")

			send_task = asyncio.create_task(send())
			receive_task = asyncio.create_task(receive())

			await asyncio.gather(send_task, receive_task)


async def main():
	server_uri = "ws://XXX.XXX.XXX.XXX:3389" # Port 3389 is commonly used for ws connections
    client = Speaker(server_uri, 5)
    try:
        await client.send_receive()
    except KeyboardInterrupt:
        print("Interrupted by user")
		
    finally:
        client.close()
        print("\nComplete Transcription:")
        for line in client.transcription:
            print(line)



if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		print("\nUser interrupted")
