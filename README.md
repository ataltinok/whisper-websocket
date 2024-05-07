# whisper-websocket
Transcribe audio in real-time using OpenAI's Whisper model on a server and send audio using a websocket.

Adjust the IP addresses as necessary. Run Receiver.py (server) on the device that you intend to transcribe the audio and Speaker.py (client) on the device that you intend to record the audio. Then you are ready to go.

Whisper takes the numpy array of the audio as input. The client converts the audio into a numpy array, encodes it for the websocket and sends the result to the server. The server decodes the input back to the numpy array and feeds the array to Whisper. The server then sends back the trascription result.
