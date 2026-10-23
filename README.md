# 🚀 ISS Tracker

This is a full-stack Python application that calculates the exact position of the **International Space Station (ISS)** in real time using orbital math. It runs a web server locally and shows the space station live on an interactive map.

## 🪐 How it Works
- **Orbital Calculations:** Uses the `skyfield` library to calculate the ISS path using real space tracking data.
- **Interactive Map:** Uses `folium` to generate a live minimal world map.
- **Auto Update:** The map automatically moves and updates the coordinates every 3 seconds.

## 💻 How to Run It on Your Computer

### 1. Download the code
Download both `iss-tracker-code.py` and `requirements.txt` into the same folder on your computer.

### 2. Install the libraries
Open your computer's terminal or open your coding platform, navigate to your folder, and type this command to install the required libraries:
```bash
pip install -r requirements.txt
```

### 3. Launch the tracker
Run the Python script by typing:
```bash
python iss-tracker-code.py
```
A browser window will automatically open at `http://localhost:8000` showing your live space tracker.
