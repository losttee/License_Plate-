# 🚗 Vehicle Management System with License Plate Recognition (Django + YOLOv8)

This is a web-based vehicle management system developed using **Django** and **XAMPP (MySQL)**. The system uses **YOLOv8** for automatic license plate and character recognition, allowing vehicles to be identified and logged efficiently.

---

## 🔧 Features

- ✅ Admin login & authentication  
- 📸 Upload vehicle images for automatic recognition  
- 🧠 License plate detection using **YOLOv8**  
- 🔡 Character recognition from detected plates  
- 💾 Store vehicle entries in MySQL database  
- 🕒 View vehicle entry/exit history  
- 📂 Organize uploaded images via Django `media/`  

---

## 🛠 Technologies Used

- **Backend:** Django (Python)  
- **Frontend:** Django Templates (HTML, Bootstrap)  
- **Database:** MySQL (via XAMPP)  
- **Machine Learning:**  
  - `YOLOv8` for plate detection  
  - OCR for character recognition (e.g. `pytesseract` or a custom model)  
- **Others:** OpenCV, NumPy, Matplotlib  

---

## 📁 Project Structure

\`\`\`
vehicle_management/
├── media/                  # Uploaded images  
├── plates/                 # Django app for plate handling  
├── saved_models/           # Trained YOLOv8 and OCR models  
├── vehicle_management/     # Django settings and URLs  
├── manage.py  
├── requirements.txt  
├── Plate_Detection.ipynb   # Notebook for detection and OCR  
\`\`\`

---

## ⚙️ Installation Guide

### 1. Clone the repository

\`\`\`bash
git clone https://github.com/yourusername/License_Plate--master.git
cd License_Plate--master/vehicle_management
\`\`\`

### 2. Set up Python environment

\`\`\`bash
pip install -r requirements.txt
\`\`\`

Install YOLOv8 dependency:

\`\`\`bash
pip install ultralytics
\`\`\`

### 3. Configure XAMPP + MySQL

- Start **Apache** and **MySQL** from XAMPP  
- Create a new database in **phpMyAdmin** (e.g. `vehicle_db`)  
- Update your Django `settings.py`:

\`\`\`python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vehicle_db',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
\`\`\`

### 4. Run migrations

\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

### 5. Create superuser (optional)

\`\`\`bash
python manage.py createsuperuser
\`\`\`

### 6. Run the development server

\`\`\`bash
python manage.py runserver
\`\`\`

Open your browser: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🤖 YOLOv8 Integration

Detection is implemented in `Plate_Detection.ipynb`:

- Load YOLOv8 model from `saved_models/`  
- Detect license plates in uploaded images  
- Recognize characters via OCR  
- Store plate numbers in database  

### YOLOv8 Sample Code

\`\`\`python
from ultralytics import YOLO

model = YOLO('saved_models/yolov8_plate.pt')
results = model('media/test_car.jpg')
results[0].show()
\`\`\`

---

## ✅ To-Do

- [ ] Add live webcam or video stream detection  
- [ ] Improve OCR with CNN/CRNN  
- [ ] Add export logs to CSV/Excel  
- [ ] Add user roles and permissions  

---

## 📸 Demo

View test images and results in the `media/` folder.

---

## 👤 Author

- **Name:** Vũ Ngọc Hà  
- **Role:** Full-stack Developer & AI Integration  
- **Email:** your-email@example.com  

---

## 📜 License

This project is for educational and personal use. For commercial applications, please contact the author.
