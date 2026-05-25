from django.db import models

class UserProfile(models.Model):
    # This stores the employee's name
    name = models.CharField(max_length=100, unique=True)
    
    # This stores the 128 face math numbers as a text list (JSON)
    face_encoding = models.JSONField() 

    def __str__(self):
        return self.name

class AttendanceLog(models.Model):
    # This connects the log directly to a specific user from the profile table
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    
    # This automatically records the exact date and time they scan their face
    timestamp = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(max_length=10, default="Present")

    def __str__(self):
        return f"{self.user.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"