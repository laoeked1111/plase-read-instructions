from flask import Flask, request, jsonify
from threading import Thread
from queue import Queue

app = Flask(__name__)

ACTIVE = False
transcript_queue = Queue()

@app.route('/')
def index():
    return """
<html>
    <head></head>
    <body>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background-color: #8ACE00; transform: scaleX(0.8); }
            h2 { font-size: 40px; color: #333; }
            p { font-size: 24px; color: #555; }
        </style>
        <h2>offloaded voice recognition server</h2>

        <h2 id="stat"></h2>
        <p id="res"></p>
        <script>
            let recording = false;
            let mediaRecorder;
            let audioChunks = [];
            let recognition;

            // Initialize Speech Recognition
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = false;

                recognition.onresult = (event) => {
                    const transcript = Array.from(event.results)
                        .map(result => result[0].transcript)
                        .join(' ');
                    document.getElementById('res').innerText = 'Transcript: ' + transcript;
                    fetch('/process', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ transcript: transcript })
                    })
                    .then(res => res.json())
                    .then(data => console.log('Processed:', data))
                    .catch(err => console.error('Error processing:', err));
                };

                recognition.onerror = (event) => {
                    console.error('Speech recognition error:', event.error);
                    // Handle network errors by restarting recognition
                    if (event.error === 'network' && recording) {
                        console.log('Network error, restarting recognition...');
                        setTimeout(() => {
                            if (recording && recognition) {
                                try {
                                    recognition.start();
                                } catch (e) {
                                    console.error('Failed to restart recognition:', e);
                                }
                            }
                        }, 1000);
                    }
                };

                recognition.onend = () => {
                    // Automatically restart if still recording
                    if (recording) {
                        try {
                            recognition.start();
                        } catch (e) {
                            console.error('Failed to restart recognition:', e);
                        }
                    }
                };
            }

            async function startRecording() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };
                    mediaRecorder.onstop = () => {
                        stream.getTracks().forEach(track => track.stop());
                    };
                    mediaRecorder.start();
                    if (recognition) {
                        recognition.start();
                    }
                    recording = true;
                    console.log('Recording started');
                } catch (err) {
                    console.error('Error starting recording:', err);
                }
            }

            function stopRecording() {
                if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                    mediaRecorder.stop();
                }
                if (recognition) {
                    recognition.stop();
                }
                recording = false;
                console.log('Recording stopped');
            }

            setInterval(() => {
                fetch('/status')
                    .then(res => res.json())
                    .then(stat => {
                        document.getElementById('stat').innerText = 'recording: ' + stat.active;
                        if (stat.active && !recording) {
                            startRecording();
                        }
                        else if (!stat.active && recording) {
                            stopRecording();
                        }
                    })
                    .catch(err => {
                        console.error('Error fetching status:', err);
                        document.getElementById('stat').innerText = 'Error: Cannot connect to server';
                    });
            }, 500);
        </script>
    </body>
</html>
"""

@app.route('/status')
def status():
    return jsonify({'active': ACTIVE})

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    if data and 'transcript' in data:
        text = data['transcript']
        print(f"Flask received transcript: {text}")
        transcript_queue.put(text)
    return jsonify({"status":"success"})

def get_latest_transcript():
    if not transcript_queue.empty():
        return transcript_queue.get()
    return None

def run_server():
    app.run(host='0.0.0.0', port=5000, threaded=True)

if __name__ == '__main__':
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    while True:
        ACTIVE = input("activate server? (y/n): ").lower() == 'y'
