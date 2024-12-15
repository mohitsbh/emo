import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import random
import cv2
import pygame

# Emotion-to-genre mapping
EMOTION_TO_GENRE = {
    'Happy': ['pop', 'dance', 'hip-hop'],
    'Sad': ['blues', 'classical', 'acoustic'],
    'Angry': ['rock', 'metal', 'punk'],
    'Surprise': ['electronic', 'dance', 'trap'],
    'Neutral': ['ambient', 'chillout', 'lo-fi']
}

# Music recommendations
MUSIC_RECOMMENDATIONS = {
    'pop': ['songs/_Khoya_Khoya__FULL_VIDEO_Song___Sooraj_Pancholi,_Athiya_Shetty___Hero___T_Se.mp3', 'songs/song2.mp3'],
    'dance': ['songs/(webmusic.in)_Jashn-E-Baharaa.mp3', 'songs/song4.mp3'],
    'hip-hop': ['songs/01 _ Zindagi Zindagi _ MarathiMp3.mp3.mp3', 'songs/song6.mp3'],
    'blues': ['songs/01 - Baarish (320 Kbps) - DownloadMing.SE.mp3', 'songs/song8.mp3'],
    'classical': ['songs/01 - Sanam Re (Title Song) [Songspk.LINK].mp3', 'songs/song10.mp3'],
    'acoustic': ['songs/01_-_Ajab_Si_-_K._K.mp3', 'songs/song12.mp3'],
    'rock': ['songs/02%20Aadhir%20Maan%20Jhale(FunMarathi.Com).mp3', 'songs/song14.mp3'],
    'metal': ['songs/03_Tum_Saath_Ho_-_Tamasha_(Arijit_Singh)_320Kbps.mp3', 'songs/song16.mp3'],
    'punk': ['songs/03._Maula_Maula.mp3', 'songs/song18.mp3'],
    'electronic': ['songs/03.Sanam_Re-Hua_Hain_Aaj_Pehli_Baar.mp3', 'songs/song20.mp3'],
    'trap': ['songs/04_-_Main_Agar_Kahoon_-_Sonu_Nigam_Shreya_Ghoshal.mp3', 'songs/song22.mp3'],
    'ambient': ['songs/05 Sunya Sunya(MixMarathi.Com) (1).mp3', 'songs/song24.mp3'],
    'chillout': ['songs/05_-_Tere_Hone_Laga_Hoon_(Feel_Me)_[www.PagalWorld.Com].mp3', 'songs/song26.mp3'],
    'lo-fi': ['songs/Aap_Se_Milkar.mp3', 'songs/song28.mp3']
}

class EmotionMusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Emotion-Based Music Player")
        self.root.geometry("1000x800")
        self.root.configure(bg="#F5F5F5")

        self.emotion = tk.StringVar()
        self.emotion.set("Detecting...")
        self.song = tk.StringVar()
        self.song.set("")

        # Initialize Pygame mixer for playing music
        pygame.init()
        pygame.mixer.init()

        # Load classifiers
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

        # Create a scrollable frame
        self.create_scrollable_frame()

        # OpenCV camera initialization (check if cap can open before starting)
        self.start_camera_feed()

    def create_scrollable_frame(self):
        # Create a canvas for the scrollable area
        canvas = tk.Canvas(self.root, bg="#F5F5F5", bd=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas
        self.scrollable_frame = tk.Frame(canvas, bg="#FFFFFF", relief=tk.FLAT, bd=0)
        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Add widgets to the scrollable frame
        self.create_widgets()

    def create_widgets(self):
        # Emotion Display with better styling
        tk.Label(self.scrollable_frame, text="Detected Emotion:", font=("Helvetica", 18), bg="#FFFFFF", fg="#333333").pack(pady=10)
        self.emotion_label = tk.Label(self.scrollable_frame, textvariable=self.emotion, font=("Helvetica", 20, "bold"), fg="#0078D7", bg="#FFFFFF")
        self.emotion_label.pack(pady=20)

        # Camera feed display with transparent background
        self.video_frame = tk.Label(self.scrollable_frame, bg="#000000", bd=0)
        self.video_frame.pack(pady=20, padx=10, ipadx=10, ipady=10)

        # Capture Button with rounded edges and no borders
        capture_button = tk.Button(
            self.scrollable_frame,
            text="Capture & Recommend Songs",
            command=self.capture_and_recommend,
            font=("Helvetica", 14),
            bg="#28A745",
            fg="white",
            relief=tk.FLAT,
            activebackground="#1E7E34",
            pady=5, padx=20
        )
        capture_button.pack(pady=15)

        # Recommended Emotion Label
        self.recommended_emotion_label = tk.Label(
            self.scrollable_frame, text="Recommended Songs for Emotion:", font=("Helvetica", 16), bg="#FFFFFF", fg="#333333")
        self.recommended_emotion_label.pack(pady=10)

        tk.Label(self.scrollable_frame, text="Recommended Songs:", font=("Helvetica", 16), bg="#FFFFFF", fg="#333333").pack(pady=10)

        # Adding custom listbox with improved design
        self.song_listbox = tk.Listbox(
            self.scrollable_frame, height=10, selectmode=tk.SINGLE, font=("Helvetica", 12), bg="#E8F5E9", fg="#212121", bd=0, relief="flat"
        )
        self.song_listbox.pack(pady=20, ipadx=5, ipady=5)

        self.apply_listbox_styles()

        song_scrollbar = tk.Scrollbar(self.scrollable_frame, orient=tk.VERTICAL, command=self.song_listbox.yview)
        song_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.song_listbox.configure(yscrollcommand=song_scrollbar.set)

        # Play Button with better design
        play_button = tk.Button(
            self.scrollable_frame,
            text="Play Song",
            command=self.play_song,
            font=("Helvetica", 14),
            bg="#007BFF",
            fg="white",
            relief=tk.FLAT,
            activebackground="#0056b3",
            pady=5, padx=20
        )
        play_button.pack(pady=20)

    def apply_listbox_styles(self):
        def on_hover(event):
            """Apply hover effect."""
            widget = event.widget
            widget.config(bg="#A5D6A7")  # Light Green on hover

        def on_leave(event):
            """Remove hover effect."""
            widget = event.widget
            widget.config(bg="#E8F5E9")  # Original background color

        # Highlight the selected song
        self.song_listbox.bind("<Enter>", on_hover)
        self.song_listbox.bind("<Leave>", on_leave)

    def start_camera_feed(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Camera Error", "Unable to access camera.")
        else:
            self.update_camera_feed()

    def update_camera_feed(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            detected_emotion = self.detect_emotion(frame)
            self.emotion.set(detected_emotion)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)

        self.root.after(10, self.update_camera_feed)

    def detect_emotion(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        smiles = []  # Ensure smiles and eyes are initialized
        eyes = []

        for (x, y, w, h) in faces:
            face = gray[y:y + h, x:x + w]

            smiles = self.smile_cascade.detectMultiScale(face, scaleFactor=1.8, minNeighbors=20)
            if len(smiles) > 0:
                return "Happy"

            eyes = self.eye_cascade.detectMultiScale(face, scaleFactor=1.1, minNeighbors=5)
            if len(eyes) > 1:
                return "Surprise"

            if w > 150:
                return "Angry"
        
        # If there are no smiles or eyes detected, assume 'Sad'
        if len(smiles) == 0 and len(eyes) == 0:
            return "Sad"

        return "Neutral"

    def capture_and_recommend(self):
        ret, frame = self.cap.read()
        if ret:
            cv2.imwrite("captured_image.jpg", frame)
            detected_emotion = self.emotion.get()
            if detected_emotion:
                self.get_music_recommendations(detected_emotion)

    def get_music_recommendations(self, emotion):
        genres = EMOTION_TO_GENRE.get(emotion, ['pop'])
        recommendations = [song for genre in genres for song in MUSIC_RECOMMENDATIONS.get(genre, [])]
        random.shuffle(recommendations)

        self.song_listbox.delete(0, tk.END)
        self.recommended_emotion_label.config(text=f"Detected Emotion: {emotion}")
        for song in recommendations[:10]:
            self.song_listbox.insert(tk.END, song)

    def play_song(self):
        selected_song_index = self.song_listbox.curselection()
        if selected_song_index:
            song = self.song_listbox.get(selected_song_index)
            try:
                pygame.mixer.music.load(song)
                pygame.mixer.music.play()
                messagebox.showinfo("Playing Song", f"Now playing: {song}")
            except Exception as e:
                messagebox.showerror("Error", f"Unable to play song: {str(e)}")
        else:
            messagebox.showwarning("No Song Selected", "Please select a song.")

    def __del__(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            pygame.mixer.quit()

if __name__ == "__main__":
    root = tk.Tk()
    player = EmotionMusicPlayer(root)
    root.mainloop()
