
##############################
# IMPORTS
##############################
from gpiozero import Motor, Button
from picamera2 import Picamera2
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont, Image, ImageDraw, ImageOps
from threading import Thread
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Tuple, Optional

import os
import time
import cv2 as cv
import numpy as np

import speech_processing as sp


##############################
# CONSTANTS
##############################

btn_forward_pin = 9
btn_backward_pin = 10
btn_gemini_pin = 11

motor_forward_pin = 12
motor_backward_pin = 13

bitmap_data = bytearray([0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xfc, 0x3f, 0xff, 0xff,
        0xff, 0xff, 0xff, 0xff, 0xfc, 0x07, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xfc, 0x00, 0xff, 0xff,
        0xff, 0x8f, 0xff, 0xff, 0xfc, 0x00, 0x3f, 0xff, 0xff, 0x87, 0xff, 0xff, 0xfc, 0x60, 0x07, 0xff,
        0xff, 0x87, 0xff, 0xff, 0xfc, 0x78, 0x03, 0xff, 0xff, 0x83, 0xff, 0xff, 0xf8, 0x7f, 0x00, 0x7f,
        0xff, 0x81, 0xff, 0xff, 0xc0, 0x7f, 0xc0, 0x1f, 0xff, 0x00, 0xff, 0xff, 0x00, 0x78, 0x30, 0x07,
        0xff, 0x00, 0xff, 0xf8, 0x01, 0xf0, 0x1c, 0x03, 0xff, 0x10, 0x7f, 0xc0, 0x07, 0xc0, 0x07, 0x03,
        0xff, 0x18, 0x3f, 0x00, 0x1f, 0x80, 0x03, 0xc3, 0xff, 0x1c, 0x10, 0x00, 0xff, 0x00, 0x03, 0xff,
        0xff, 0x1e, 0x00, 0x0f, 0xfe, 0x00, 0x03, 0xff, 0xff, 0x1e, 0x00, 0x3f, 0xfe, 0x00, 0x03, 0xff,
        0xfe, 0x1f, 0x83, 0xff, 0xe0, 0x00, 0x03, 0xff, 0xfe, 0x1f, 0xff, 0xff, 0xc0, 0x00, 0x03, 0xff,
        0xfe, 0x3f, 0xff, 0xff, 0xc0, 0x00, 0x07, 0xff, 0xfe, 0x3f, 0xff, 0xff, 0xc0, 0x00, 0x07, 0xff,
        0xfe, 0x3f, 0xff, 0xfc, 0x03, 0x00, 0x07, 0xff, 0xfe, 0x3f, 0xff, 0xe0, 0x03, 0x80, 0x0f, 0xff,
        0xfe, 0x3f, 0xfc, 0x00, 0x03, 0xf8, 0x1f, 0xff, 0xfc, 0x3f, 0xfc, 0x00, 0x03, 0xff, 0xff, 0xff,
        0xfc, 0x3f, 0xfc, 0x00, 0x03, 0xff, 0xff, 0xff, 0xfc, 0x7f, 0xf8, 0x00, 0x03, 0xff, 0xff, 0xff,
        0xfc, 0x7f, 0xf8, 0x00, 0x03, 0xff, 0x8f, 0xff, 0xfc, 0x7f, 0xf8, 0x00, 0x03, 0xff, 0x8f, 0xff,
        0xfc, 0x7f, 0xf8, 0x00, 0x03, 0xff, 0x8f, 0xff, 0xfc, 0x7f, 0xf8, 0x00, 0x03, 0xff, 0x8f, 0xff,
        0xfc, 0x7f, 0xf8, 0x00, 0x03, 0xff, 0x8f, 0xff, 0xfc, 0x7f, 0xf8, 0x00, 0x07, 0xf0, 0x0f, 0xff,
        0xf8, 0x7f, 0xf8, 0x00, 0x07, 0xf0, 0x0f, 0xff, 0xf8, 0xff, 0xf8, 0x00, 0x07, 0xf0, 0x0f, 0xff,
        0xf8, 0xff, 0xf8, 0x00, 0x0f, 0xff, 0xff, 0xff, 0xf8, 0xff, 0xf8, 0x00, 0x1f, 0xff, 0xff, 0xff,
        0xf8, 0xff, 0xfc, 0x00, 0x3f, 0xff, 0xff, 0xff, 0xf8, 0xff, 0xfc, 0x01, 0xff, 0xff, 0xff, 0xff,
        0xf8, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xf0, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
        0xf0, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xf1, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
        0xf1, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xf1, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
        0xf1, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xf1, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])


canvas_img = Image.new('1', (128, 64), color=0)
icon_size = (64, 55)
icon_img = Image.frombytes('1', icon_size, bytes(bitmap_data[0:440]))
inverted_icon = ImageOps.invert(icon_img.convert('L')).convert('1')
x = (128 - icon_size[0]) // 2
y = (64 - icon_size[1]) // 2 + 10
canvas_img.paste(inverted_icon, (x, y))


##############################
# FUNCTIONS
##############################

class BBoxes(BaseModel):
        name: str = Field(description="Type of object being bounded")
        bboxes: List[Tuple[Tuple[int, int], Tuple[int, int]]]

def get_roi(prompt, frame):
        print("Getting ROI")

        success, buffer = cv.imencode('.jpg', frame)
        if not success:
                return (0,0,639,479)
        img_bytes = buffer.tobytes()

        response = client.models.generate_content(
                model = "gemini-3-flash-preview",
                contents=[
                        types.Part.from_bytes(
                        data=img_bytes,
                        mime_type = "image/jpeg"
                ), prompt],
                config=responseconfig,
        )

        try:
                data = BBoxes.model_validate_json(response.text)
                if not data.bboxes:
                        return (0,0,639,479)

                print(data.bboxes)

                # scale from 0-1000 to actual pixels
                (y1, x1), (y2, x2) = data.bboxes[0]

                real_x1 = int(x1 * 640 / 1000)
                real_y1 = int(y1 * 480 / 1000)
                real_x2 = int(x2 * 640 / 1000)
                real_y2 = int(y2 * 480 / 1000)

                return (
                        max(0, real_x1), max(0, real_y1),
                        min(639, real_x2), min(479, real_y2)
                )

        except Exception as e:
                print(f"ROI Parsing Error: {e}")
                return (0,0,639,479)


def update_oled(addr, text, pos):
        with canvas(addr) as draw:
                draw.text(pos, f"{text}", fill="white")

def compute_sharpness(image):
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)  # Convert to grayscale

        sobel_x = cv.Sobel(gray, cv.CV_64F, 1, 0, ksize=3)  # Sobel filter in X direction
        sobel_y = cv.Sobel(gray, cv.CV_64F, 0, 1, ksize=3)  # Sobel filter in Y direction

        tenengrad = np.sqrt(sobel_x**2 + sobel_y**2)  # Compute gradient magnitude
        raw_score = np.mean(tenengrad)
        mean_intensity = np.mean(gray)

        return raw_score / (mean_intensity + 1e-6)

def crop_and_get_sharpness(roi):
        frame = picam2.capture_array()
        x, y, x2, y2 = roi
        frame_cropped = frame[y:y2, x:x2]

        if frame_cropped.size == 0:
                return compute_sharpness(frame)

        return compute_sharpness(frame_cropped)

def perform_focusing(roi):
        og_sharpness = crop_and_get_sharpness(roi)

        motor.forward(0.5)
        forward_sharpness = crop_and_get_sharpness(roi)

        motor.backward(0.5)
        backward_sharpness = crop_and_get_sharpness(roi)

        if og_sharpness > forward_sharpness and og_sharpness > backward_sharpness: return

        dir = "forward" if forward_sharpness > backward_sharpness else "backward"
        last_sharpness = forward_sharpness if dir == "forward" else backward_sharpness

        while True:
                if dir == "forward":
                        motor.forward(0.5)
                else:
                        motor.backward(0.5)

                new_sharpness = crop_and_get_sharpness(roi)
                if new_sharpness < og_sharpness:
                        break

        if dir == "forward":
                motor.backward(0.5)
        else:
                motor.forward(0.5)


##############################
# MAIN
##############################


if __name__ == "__main__":

        ###############################
        # SETUP
        ###############################

        # initialize buttons
        print("Initializing buttons")
        btn_forward = Button(btn_forward_pin, pull_up=True, bounce_time=0.05)
        btn_backward = Button(btn_backward_pin, pull_up=True, bounce_time=0.05)
        btn_gemini = Button(btn_gemini_pin, pull_up=True, bounce_time=0.05)

        # initialize motor
        print("Initializing motor")
        motor = Motor(forward=motor_forward_pin, backward=motor_backward_pin)

        # server for processing speech
        print("Starting server thread")
        server_thread = Thread(target=sp.run_server)
        server_thread.daemon = True
        server_thread.start()

        # gemini setup
        print("Gemini setup")
        api_key = os.getenv('GEMINI_API_KEY')
        client = genai.Client(api_key=api_key)

        responseconfig = types.GenerateContentConfig(
            thinking_config = types.ThinkingConfig(thinking_level="minimal"),
            response_mime_type = "application/json",
            response_json_schema = BBoxes.model_json_schema()
        )

        # oled displays
        #print("Preparing OLED")
        #hud_oled = 0x3C
        #status_oled = 0x3D

        #serial_hud = i2c(port=1, address=hud_oled)
        #serial_status = i2c(port=1, address=status_oled)
        #device_hud = ssd1306(serial_hud)
        #device_status = ssd1306(serial_status)

        #device_status.display(canvas_img)

        #with canvas(device_hud) as draw:
        #    draw.rectangle([(10, 30), (100, 64)], outline="white", fill=None)


        ##############################
        # LOOP
        ##############################

        while True:

                if btn_gemini.is_pressed:
                        # get prompt for Gemini
                        sp.ACTIVE = True

                        speech = None
                        timeout = 10
                        start_time = time.time()

                        while speech is None and (time.time() - start_time) < timeout:
                                speech = sp.get_latest_transcript()
                                time.sleep(0.1)

                        sp.ACTIVE = False
                        if speech:
                                print(f"Speech Processed: {speech}")

                                # start the camera
                                picam2 = Picamera2()
                                config = picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)})
                                picam2.configure(config)
                                picam2.start()

                                picam2.set_controls({
                                        "AeEnable": False,
                                        "ExposureTime": 20000,
                                        "AnalogueGain": 1.0,
                                        "AwbEnable": False
                                })

                                frame = picam2.capture_array()
                                frame_bgr = cv.cvtColor(frame, cv.COLOR_RGB2BGR)

                                roi = get_roi(speech, frame)
                                perform_focusing(roi)

                                picam2.stop()
                                picam2.close()
                                cv.destroyAllWindows()


                        else:
                                print("Timed out: No speech received.")


                elif btn_forward.is_pressed:
                        motor.forward(0.3)
                elif btn_backward.is_pressed:
                        motor.backward(0.3)
                else:
                        motor.stop()