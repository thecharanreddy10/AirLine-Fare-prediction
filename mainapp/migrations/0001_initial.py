# Generated by Django 5.1.3 on 2024-11-23 11:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UserDetails",
            fields=[
                ("user_id", models.AutoField(primary_key=True, serialize=False)),
                ("full_name", models.CharField(max_length=255)),
                (
                    "phone_number",
                    models.CharField(
                        max_length=10,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid 10-digit phone number.",
                                regex="^\\d{10}$",
                            )
                        ],
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "password",
                    models.CharField(
                        max_length=128,
                        validators=[django.core.validators.MinLengthValidator(8)],
                    ),
                ),
                ("age", models.PositiveIntegerField()),
                ("address", models.TextField()),
                (
                    "user_image",
                    models.ImageField(blank=True, null=True, upload_to="media/"),
                ),
                ("otp_status", models.CharField(default="pending", max_length=10)),
                ("otp_num", models.CharField(blank=True, max_length=4)),
                ("user_status", models.CharField(default="pending", max_length=10)),
                ("date_time", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "user_details",
            },
        ),
    ]
