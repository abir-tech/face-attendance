import cv2
import numpy as np
import json # <-- Added to convert math lists into text strings for SQLite
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from deepface import DeepFace # <-- Our brand new One-Shot AI engine
from .models import UserProfile, AttendanceLog

class RegisterFaceView(APIView):
    def post(self, request):
        # 1. Check if name and image are both sent
        if 'name' not in request.data or 'image' not in request.FILES:
            return Response({"error": "Both 'name' and 'image' are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        name = request.data['name']
        uploaded_file = request.FILES['image']
        
        # 2. Convert uploaded file into an OpenCV image
        file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is None:
            return Response({"error": "Invalid image format or unreadable file"}, status=status.HTTP_400_BAD_REQUEST)
            
        # 3. UPGRADED: Extract 128-d facial feature vector without strict alignment enforcement
        try:
            # We explicitly add enforce_detection=False and skip backend to force processing on static files!
            embeddings_data = DeepFace.represent(
                img_path=image, 
                model_name="VGG-Face", 
                enforce_detection=False, 
                detector_backend="skip"
            )
            face_embedding = embeddings_data[0]["embedding"]
            
            # 4. Save the user profile to the SQLite database
            profile, created = UserProfile.objects.update_or_create(
                name=name,
                defaults={'face_encoding': json.dumps(face_embedding)}
            )
            return Response({
                "status": "success",
                "message": f"Successfully registered true One-Shot profile for {name}!"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": f"AI Registration Failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
class ScanFaceView(APIView):
    def post(self, request):
        # 1. Check if an image file was sent
        if 'image' not in request.FILES:
            return Response({"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['image']
        
        # 2. Convert uploaded file directly into an OpenCV image matrix
        file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is None:
            return Response({"error": "Invalid image format"}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Generate mathematical facial vector for the live scanning person
        try:
            # Added enforce_detection=False to handle poor lighting/angles gracefully
            live_embeddings = DeepFace.represent(img_path=image, model_name="VGG-Face", enforce_detection=False)
            live_embedding = live_embeddings[0]["embedding"]
            
            # 4. Pull our database profiles to find a match
            profiles = UserProfile.objects.all()
            if not profiles.exists():
                return Response({"status": "no_profiles", "message": "No registered profiles found in the system database."}, status=status.HTTP_404_NOT_FOUND)

            best_match = None
            lowest_distance = 0.35 # Balanced Cosine threshold sweet-spot
            
            for profile in profiles:
                try:
                    # Load the stored math text string back into a structural Python list
                    stored_embedding = json.loads(profile.face_encoding)
                    
                    # Compute vector distance between live snapshot and database profile
                   # Convert embeddings to math arrays
                    v1 = np.array(live_embedding)
                    v2 = np.array(stored_embedding)
                    
                    # Calculate similarity distance
                    distance = 1 - (np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
                    
                    # 🔥 DEBUG PRINT: Watch your server terminal to see the exact score!
                    print(f"--- AI MATCH DEBUG --- Profile: {profile.name} | Calculated Distance: {distance:.4f}")
                    
                    if distance < lowest_distance:
                        lowest_distance = distance
                        best_match = profile
                except Exception as loop_err:
                    print(f"Skipping profile due to error: {loop_err}")
                    continue
                    
            # 5. Log Attendance if a mathematical match passes our threshold test
            if best_match:
                try:
                    AttendanceLog.objects.create(user=best_match)
                except TypeError:
                    AttendanceLog.objects.create(name=best_match.name, status="Present")
                    
                return Response({
                    "status": "success",
                    "name": best_match.name,
                    "message": f"Welcome back, {best_match.name}! Attendance logged via One-Shot AI."
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "unknown", 
                    "message": "Face not recognized. Access denied."
                }, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({"error": f"AI Scanning Analysis Failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
class AttendanceHistoryView(APIView):
    def get(self, request):
        # Fetch the latest 50 logs sorted by newest entries first
        logs = AttendanceLog.objects.all().order_by('-timestamp')[:50]
        
        log_data = []
        for log in logs:
            # Handle both Foreign Key relationship logic or raw name strings safely
            name = log.user.name if hasattr(log, 'user') and log.user else getattr(log, 'name', 'Unknown Student')
            
            # CRITICAL UI ALIGNMENT UPDATE: Frontend expects JSON-compatible ISO format strings!
            timestamp = log.timestamp.isoformat() if hasattr(log, 'timestamp') and log.timestamp else "N/A"
            status_text = getattr(log, 'status', 'Present')

            log_data.append({
                "id": log.id,
                "user_name": name, # Maps perfectly with frontend log.user_name matching template literal
                "timestamp": timestamp,
                "status": status_text
            })
            
        # RETURN LOG_DATA DIRECTLY AS A FLAT LIST Array Object package payload!
        return Response(log_data, status=status.HTTP_200_OK)