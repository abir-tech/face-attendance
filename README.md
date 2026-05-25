# AI One-Shot Facial Attendance System

A plug-and-play facial recognition and attendance tracking module built with **Django REST Framework (DRF)**, **DeepFace (VGG-Face)**, and a vanilla JS dashboard. 

This system uses **One-Shot learning**, meaning users only need to register a single photograph. The system instantly extracts their biometric feature vectors and evaluates real-time webcam frames against the database using cosine similarity metrics.

---

## 🏗️ System Architecture & Data Flow

1. **Registration Flow:** User uploads/takes a snapshot ➡️ Image matrix processed via `DeepFace.represent()` with alignment checks bypassed (`detector_backend="skip"`) ➡️ 128-dimensional facial embedding array stringified into JSON ➡️ Saved to `UserProfile` model.
2. **Verification Flow:** Live webcam frame passed to `ScanFaceView` ➡️ Current facial embedding generated ➡️ NumPy computes the cosine distance against all database records ➡️ Smallest vector distance below `0.35` triggers an automated write into the `AttendanceLog` model.

---

## 🛠️ How to Merge this Module into Your App

To integrate this module into an existing Django application, follow these integration touchpoints:

### 1. Database Dependencies (`attendance/models.py`)
Ensure your application incorporates or links to these two tables:
* `UserProfile`: Stores the `name` and a `TextField` containing the serialized `json.dumps()` embedding array.
* `AttendanceLog`: Handles timestamps and binds to user records via a Foreign Key relation or direct name assignment.

### 2. Core Facial Logic (`attendance/views.py`)
Copy the view modules into your views layout. Note that the endpoints are intentionally split for decoupled microservices operations:
* `RegisterFaceView`: High-tolerance registration parser.
* `ScanFaceView`: Optimized array vector comparison loop utilizing NumPy vector dot products for speed.
* `AttendanceHistoryView`: Flattens querysets into a direct array for synchronous UI rendering.

### 3. Setting up Dependencies
Your team must install the core computational frameworks before booting:
```bash
pip install djangorestframework deepface opencv-python numpy
