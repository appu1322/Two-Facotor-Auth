from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from home.models import newUser
from random import randint
from os import chdir,getcwd
import pyqrcode
import cv2
import pyzbar.pyzbar as pyzbar
import time

# Create your views here.

def home(request):
    user = request.user
    if user.username == 'user1':
        return redirect(login)
    if user.username!='':
        newuser = newUser.objects.get(user__username=user.username)
        if newuser.verify_active == 1:
            generate_verification_code = randint(100000,999999)
            newuser.verification_code = generate_verification_code

            #get current working directory path
            get_current_working_dir_path = getcwd()

            # verification code which represents the QR code
            s = str(generate_verification_code)

            # Generate QR code
            url = pyqrcode.create(s)

            # Create and save the png file naming "myqr.png"
            chdir(r'C:\Users\Mac\web dev\Authentication\auth\media\qr_code_images')
            url.png('myqr.png', scale=6)
            chdir(get_current_working_dir_path)

            newuser.verify_active = 0
            newuser.save()
            params = {'verifcation_active':True, 'verification_code':generate_verification_code}
            return render(request, 'home/home.html', params)
        else:
            newuser.verification_code = 0
            newuser.save()
            return render(request, 'home/home.html')
    else:
        return redirect(login)

def login(request):
    return render(request, 'home/login.html')

def verify_two_fa(request):
    if request.method == 'POST':
        input_string = request.POST.get('input_string')

        # get username auth information using query
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password) 
        newuser = newUser.objects.get(user__username=user.username)      

        # verify verification code type manually
        if input_string == 'verify_code':
            verification_code = request.POST.get('verify_code')
            if verification_code == str(newuser.verification_code):
                newuser.noOfLogs += 1
                auth_login(request, user)
                newuser.save()

        # verify verification code using QR code
        elif input_string == 'scan_code':
            cap = cv2.VideoCapture(0)
            font = cv2.FONT_HERSHEY_PLAIN

            # here calclate current time and add 30 sec more and store result into end_time
            current_time = str(time.asctime( time.localtime(time.time()) ))[17:19]
            end_time = int(current_time) + 30
            if end_time >= 60:
                end_time = end_time - 60
            if len(str(end_time)) == 1:
                end_time = int('0' + str(end_time))

            while True:
                _, frame = cap.read()
                i=0
                decodedObjects = pyzbar.decode(frame)
                for obj in decodedObjects:
                    print(obj.data)
                    cv2.putText(frame, str(obj.data), (50, 50), font, 2,
                                (255, 0, 0), 3)
                    # verifying code
                    if obj.data.decode() == str(newuser.verification_code):
                        newuser.noOfLogs += 1
                        auth_login(request, user)
                        newuser.save()
                        i=1

                cv2.imshow("Frame", frame)

                # here check end_time is equal to current_time or not
                current_time = str(time.asctime(time.localtime(time.time())))[17:19]
                if current_time == str(end_time):
                    i=1

                cv2.waitKey(1)
                if(i==1):
                    cap = cv2.VideoCapture()
                    cv2.destroyAllWindows()
                    break 
    return redirect(home)

def two_fa(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            newuser = newUser.objects.get(user__username=username)
            if newuser.noOfLogs == 0:
                newuser.noOfLogs = 1
                newuser.save()
                auth_login(request, user)
                return redirect(home)
            else:
                newuser.verify_active = 1
                cap = cv2.VideoCapture(0)
                _, frame = cap.read()
                if frame is None:
                    cam = False
                else:
                    cam = True
                params = {"camera":cam, 'username':username, 'password':password}
                newuser.save()
                return render(request, 'home/two_fa.html', params)
    return redirect(login)

def logout(request):
    user = request.user
    newuser = newUser.objects.get(user__username=user.username)
    newuser.noOfLogs-=1
    newuser.save()
    auth_logout(request)
    return redirect(login)


