from django.shortcuts import render,redirect
from django.contrib import messages
import random
import urllib.parse
import urllib.request
import ssl
from mainapp.models import *

# Create your views here
def sendSMS(user, otp, mobile):
    print('sendSMS Called')
    data = urllib.parse.urlencode({
        'username': 'Codebook',
        'apikey': '56dbbdc9cea86b276f6c',
        'mobile': mobile,
        'message': f'Hello {user}, your OTP for account activation is {otp}. This message is generated from https://www.codebook.in server. Thank you',
        'senderid': 'CODEBK'
    })
    data = data.encode('utf-8')
    
    # Disable SSL certificate verification
    context = ssl._create_unverified_context()
    request = urllib.request.Request("https://smslogin.co/v3/api.php?", data=data, method='POST')
    
    try:
        with urllib.request.urlopen(request, context=context) as response:
            result = response.read()
            print(result)
            return result
    except Exception as e:
        print(f"Error sending SMS: {e}")

def generate_andSend_Otp(name,phone_number, email):
    # Generate OTP
    phone = phone_number
    otp_Number = random.randint(1000,9999)
    sendSMS(name, otp_Number, phone)
    print(otp_Number)
    return otp_Number

# Create your views here.
def home(request):
    return render(request, 'main/home.html')

def about(request):
    return render(request, 'main/about.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            dbUser = UserDetails.objects.get(email = email)
            if dbUser.email == email and dbUser.password == password:
                if dbUser.otp_status == 'verified' and dbUser.user_status == 'accepted':
                    request.session['user_id'] = dbUser.user_id
                    messages.success(request, "Login Successful")
                    return redirect('user_dashboard')
                elif dbUser.otp_status == 'verified' and dbUser.user_status == 'pending':
                    messages.warning(request, "Your account is pending for admin approval")
                elif dbUser.otp_status == 'verified' and dbUser.user_status == 'rejected':
                    messages.warning(request, "Your account is rejected by the admin")
                else:
                    messages.error(request, "Your OTP is not verified")
                    return redirect('/otp')
            else:
                messages.error(request, 'Invalid Credentials')
        except:
            messages.error(request, "User does not exist")
            return redirect('user_register')
    return render(request, 'main/user-login.html')

def user_register(request):
    if request.method=='POST':
        full_name = request.POST.get('username')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        age = request.POST.get('age')
        address = request.POST.get('address')
        profilepic = request.FILES['profilepic']

        try:
            dbuser = UserDetails.objects.get(email=email)
            if dbuser.email == email:
                messages.error(request, 'Email already exists')
                return redirect('user_login')
        except UserDetails.DoesNotExist:
            otp_number = generate_andSend_Otp(full_name, phone, email)

            request.session['user-name'] = full_name
            request.session['user-email'] = email
            request.session['user-phone'] = phone
            request.session['user-password'] = password
            request.session['user-otp'] = otp_number

            UserDetails.objects.create(full_name = full_name, phone_number = phone, email = email, password = password, age = age,  address = address, otp_num = otp_number,  user_image = profilepic)
            messages.info(request, 'OTP has been sent to your registered mobile number')
            return redirect('otp')
    return render(request, 'main/user-register.html')

def admin_login(request):
    valid_credentials = {
        'username': 'admin',
        'password': 'admin'
    }
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == valid_credentials['username'] and password == valid_credentials['password']:
            messages.success(request,'Login Successfull')
            return redirect('admin_dashboard')
        else:
            messages.error(request,"Invalid Credentials")
            return redirect('admin_login')
    return render(request, 'main/admin-login.html')

def otp(request):
    email = request.session['user-email']
    try:
        dbUser = UserDetails.objects.get(email=email)
        generate_Otp = dbUser.otp_num
        if request.method == "POST":
            otp1 = request.POST.get('otp1')
            otp2 = request.POST.get('otp2')
            otp3 = request.POST.get('otp3')
            otp4 = request.POST.get('otp4')

            user_otp = otp1 + otp2 + otp3 + otp4
            if int(user_otp) == int(generate_Otp):
                dbUser.otp_status = 'verified'
                dbUser.save()
                messages.success(request, "registration successful")
                return redirect('user_login')
            else:
                messages.error(request, 'Invalid OTP')
    except UserDetails.DoesNotExist:
        print('User does not exist')
        messages.error(request, 'User Does Not Exists')

    return render(request, 'main/otp.html')

def resendOtp(request):
    full_name = request.session['user-name']
    phone = request.session['user-phone']
    email = request.session['user-email']

    otp_number = generate_andSend_Otp(full_name, phone, email)
    request.session['user-otp'] = otp_number

    dbuser = UserDetails.objects.get(email=email)
    dbuser.otp_num = otp_number
    dbuser.save()
    messages.info(request, 'OTP has been sent to your registered mobile number')
    return redirect('/otp')
