# Please Read Instructions Carefully Before Use

This is a pair of smart, voice-controlled glasses that automatically adjust focus and zoom based on what you want to look at and your personal eye prescription. It is designed to reduce eye strain and help professionals—like surgeons or electricians—see fine details without needing to use their hands.

Instead of you leaning in or squinting to see something, you simply tell the glasses what to look at. The system then physically moves the lenses to bring that specific object into sharp focus. 

## Hardware & Software

*   **Hardware:** The system runs on a Raspberry Pi Zero 2 and a Pi Pico. A small motor turns a screw to physically move the lenses back and forth for focus. It runs off a single 9V battery and uses mechanical keyboard switches for physical buttons.
*   **Software:** When you speak a command, the glasses use Google Gemini to identify and track the object you want to look at. Custom math and control loops then automatically adjust the camera until that specific area is in perfect focus.
*   **Feedback:** The glasses talk back to you using ElevenLabs voice software. They also feature small OLED screens on the sides that display status information and small animations.
