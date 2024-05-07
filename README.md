# whisper-websocket
Transcribe audio in real-time using OpenAI's Whisper model on a server and send audio using a websocket.

Run the server.py on the device that you intend to transcribe the audio and client.py on the device that you intend to record the audio. Adjust the IP addresses as necessary.

Whisper takes the numpy array of the audio as input. The client converts the audio into a numpy array and sends the result to the server. The server transcribes the given audio and sends the output back.
