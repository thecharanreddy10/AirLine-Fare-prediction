from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator

# Create your models here.
class UserDetails(models.Model):
    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$', message="Enter a valid 10-digit phone number.")]
    )
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, validators=[MinLengthValidator(8)])  # Consider hashing
    age = models.PositiveIntegerField()
    address = models.TextField()
    user_image = models.ImageField(upload_to='media/', null=True, blank=True)
    otp_status = models.CharField(max_length=10, default="pending")
    otp_num = models.CharField(max_length=4, blank=True)  # Assuming OTP is numeric and of fixed length
    user_status = models.CharField(max_length=10, default="pending")
    date_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_details"
