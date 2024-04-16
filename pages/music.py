from PIL import Image
import os 
import streamlit as st
import webbrowser
import av
import cv2 
import numpy as np 
import mediapipe as mp 
from keras.models import load_model
from streamlit_webrtc import webrtc_streamer
from zmq import NULL

im = Image.open("C:\laukik\python_projects\EmotionBasedMusic\media\songicon.jpg")
st.set_page_config(
	page_title="Emotion based music", page_icon = im,
	layout = "wide",
	initial_sidebar_state= "collapsed"
)
st.markdown("""
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
model_dir = os.path.join("C:\laukik\python_projects\EmotionBasedMusic\models")
model  = load_model(os.path.join(model_dir,"model.keras"))
label = np.load(os.path.join(model_dir,"labels.npy"))
holistic = mp.solutions.holistic
hands = mp.solutions.hands
holis = holistic.Holistic()
drawing = mp.solutions.drawing_utils

st.write("hi")
background_image = """
<style>
[data-testid="stAppViewContainer"] > .main {
    background-image: 
	url("https://i.postimg.cc/tgzrbkPG/background-m-H05-EMpiq-transformed.jpg");]
    background-size: 100vw 100vh;
    background-position: fit to page;  
    background-repeat: no-repeat;
}
</style>
"""
st.markdown(background_image, unsafe_allow_html=True)

st.header(r"$\textsf{\large Welcome to Emotion Based Music Recommender}$", anchor=False)
if "run" not in st.session_state:
	st.session_state["run"] = "true"
try:
	emotion = np.load(os.path.join(model_dir,"emotion.npy"))[0]
except:
	emotion=""

if not(emotion):
	st.session_state["run"] = "true"
else:
	st.session_state["run"] = "false"

class EmotionProcessor:
	def recv(self, frame):
		frm = frame.to_ndarray(format="bgr24")
		frm = cv2.flip(frm, 1)
		res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))
		lst = []
		if res.face_landmarks:
			for i in res.face_landmarks.landmark:
				lst.append(i.x - res.face_landmarks.landmark[1].x)
				lst.append(i.y - res.face_landmarks.landmark[1].y)

			if res.left_hand_landmarks:
				for i in res.left_hand_landmarks.landmark:
					lst.append(i.x - res.left_hand_landmarks.landmark[8].x)
					lst.append(i.y - res.left_hand_landmarks.landmark[8].y)
			else:
				for i in range(42):
					lst.append(0.0)

			if res.right_hand_landmarks:
				for i in res.right_hand_landmarks.landmark:
					lst.append(i.x - res.right_hand_landmarks.landmark[8].x)
					lst.append(i.y - res.right_hand_landmarks.landmark[8].y)
			else:
				for i in range(42):
					lst.append(0.0)

			lst = np.array(lst).reshape(1,-1)
			pred = label[np.argmax(model.predict(lst))]
			print(pred)
			cv2.putText(frm, pred, (20,20),cv2.FONT_ITALIC, 1, (255,0,0),2)
			np.save(os.path.join(model_dir,"emotion.npy"), np.array([pred]))

		drawing.draw_landmarks(frm, res.face_landmarks, holistic.FACEMESH_TESSELATION,
								landmark_drawing_spec=drawing.DrawingSpec(color=(0,0,255), thickness=-1, circle_radius=1),
								connection_drawing_spec=drawing.DrawingSpec(thickness=1))
		drawing.draw_landmarks(frm, res.left_hand_landmarks, hands.HAND_CONNECTIONS)
		drawing.draw_landmarks(frm, res.right_hand_landmarks, hands.HAND_CONNECTIONS)

		return av.VideoFrame.from_ndarray(frm, format="bgr24")

lang = st.text_input(r"$\textsf{\LARGE Enter the language of the music}$")
singer = st.text_input(r"$\textsf{\LARGE Enter the name of the singer}$")
dec = st.text_input(r"$\textsf{\LARGE Enter the decade in which the song was released}$")

if lang == NULL:
	emotion = False
elif lang and st.session_state["run"] != "false":
	webrtc_streamer(key="key", desired_playing_state=True,
				video_processor_factory=EmotionProcessor)

btn = st.button("Recommend the songs")

if btn:
	if not(emotion):
		st.warning("Language cannot be empty")
		st.session_state["run"] = "true"
	else:
		webbrowser.open(f"https://www.youtube.com/results?search_query={lang}+{emotion}+song+{singer}+{dec}")
		np.save(os.path.join(model_dir,"emotion.npy"), np.array([""]))
		st.session_state["run"] = "false"

st.page_link("home.py", label="Home", icon="🏠")
st.page_link("pages/login.py", label="Back", icon="🔓")
st.page_link("pages/delete_acc.py", label="Delete Account", icon="🔓")