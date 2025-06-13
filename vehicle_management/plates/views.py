from django.shortcuts import render, redirect
from .models import Vehicle, History, UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import datetime
import json

import cv2
import numpy as np
from ultralytics import YOLO
import tempfile, os

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.POST.get('next', reverse_lazy('dashboard'))
                return redirect(next_url)
            else:
                messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
        else:
            messages.error(request, "Có lỗi trong form đăng nhập.")
    else:
        form = AuthenticationForm()
    return render(request, 'login_signup.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Đăng ký thành công! Bạn đã được đăng nhập.")
            return redirect('dashboard')
        else:
            messages.error(request, "Có lỗi trong form đăng ký.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'login_signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def user_statistic_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    profile = UserProfile.objects.get(user=request.user)
    is_manager = profile.role == 'manager'
    
    keyword = request.GET.get('search', '').strip()
    vehicles = Vehicle.objects.all()
    if keyword:
        vehicles = vehicles.filter(
            user_name__icontains=keyword
        ) | vehicles.filter(
            unit__icontains=keyword
        ) | vehicles.filter(
            model__icontains=keyword
        ) | vehicles.filter(
            license_plate__icontains=keyword
        ) | vehicles.filter(
            phone_number__icontains=keyword
        )
    return render(request, 'user_statistic.html', {
        'vehicles': vehicles,
        'search': keyword,
        'is_manager': is_manager
    })

@csrf_exempt
def add_vehicle(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'manager':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        data = request.POST
        avatar_file = request.FILES.get('avatar')
        vehicle = Vehicle.objects.create(
            user_name=data['user_name'],
            unit=data['unit'],
            model=data['model'],
            license_plate=data['license_plate'],
            phone_number=data['phone_number'],
            issued_date=data['issued_date'],
            expired_date=data['expired_date'],
            avatar=avatar_file  # Lưu avatar nếu có
        )
        return JsonResponse({'message': 'Vehicle added successfully'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def delete_vehicle(request, vehicle_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'manager':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        try:
            Vehicle.objects.get(id=vehicle_id).delete()
            return JsonResponse({'success': True})
        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def update_vehicle(request, vehicle_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'manager':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Vehicle not found'})
    
    if request.method == 'POST':
        # Nếu là multipart (có file), cập nhật cả avatar
        if request.content_type.startswith('multipart'):
            data = request.POST
            avatar_file = request.FILES.get('avatar')
            vehicle.user_name = data.get('user_name', vehicle.user_name)
            vehicle.unit = data.get('unit', vehicle.unit)
            vehicle.model = data.get('model', vehicle.model)
            vehicle.license_plate = data.get('license_plate', vehicle.license_plate)
            vehicle.phone_number = data.get('phone_number', vehicle.phone_number)
            vehicle.issued_date = data.get('issued_date', vehicle.issued_date)
            vehicle.expired_date = data.get('expired_date', vehicle.expired_date)
            if avatar_file:
                vehicle.avatar = avatar_file
            vehicle.save()
            return JsonResponse({'success': True})
        else:
            # Nếu là JSON (AJAX cũ), chỉ cập nhật thông tin text
            try:
                data = json.loads(request.body)
                vehicle.user_name = data['user_name']
                vehicle.unit = data['unit']
                vehicle.model = data['model']
                vehicle.license_plate = data['license_plate']
                vehicle.phone_number = data['phone_number']
                vehicle.issued_date = data['issued_date']
                vehicle.expired_date = data['expired_date']
                vehicle.save()
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def recognize_plate_from_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        process_type = request.GET.get('type', 'in')  # Lấy loại xử lý từ query param (in/out)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp:
            for chunk in video_file.chunks():
                temp.write(chunk)
            temp_path = temp.name

        plate_model = YOLO('D:/Project2/vehicle_management/saved_models/plate_detection_best.pt')
        char_model = YOLO('D:/Project2/vehicle_management/saved_models/character_recognition_yolov8s_best.pt')

        cap = cv2.VideoCapture(temp_path)
        detected_vehicles = []
        processed_plates = set()
        frame_count = 0
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        skip_frames = max(1, int(fps / 2))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % skip_frames != 0:
                frame_count += 1
                continue
                
            results = plate_model(frame)
            
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                        plate_img = frame[y1:y2, x1:x2]
                        
                        char_results = char_model(plate_img)
                        chars = []
                        for char_result in char_results:
                            if char_result.boxes is not None:
                                for char_box in char_result.boxes:
                                    x_char = float(char_box.xyxy[0][0])
                                    class_id = int(char_box.cls[0])
                                    char = char_result.names[class_id]
                                    chars.append((x_char, char))
                        
                        chars.sort(key=lambda x: x[0])
                        plate_text = ''.join([c for _, c in chars])
                        
                        if len(plate_text) >= 6 and plate_text not in processed_plates:
                            processed_plates.add(plate_text)
                            
                            import base64
                            _, buffer = cv2.imencode('.jpg', frame)
                            img_b64 = base64.b64encode(buffer).decode()
                            
                            vehicle = Vehicle.objects.filter(license_plate__iexact=plate_text).first()
                            
                            # --- Thêm xử lý cho xe ra ---
                            if process_type == 'out':
                                # Kiểm tra history inlot
                                history = History.objects.filter(
                                    license_plate__iexact=plate_text,
                                    action_type='inlot',
                                    exit_time__isnull=True
                                ).first()
                                if history:
                                    status = 'inlot'
                                else:
                                    status = 'not_in_lot'
                                vehicle_data = {
                                    'plate': plate_text,
                                    'status': status,
                                    'user_info': {
                                        'license_plate': plate_text,
                                        'model': vehicle.model if vehicle else '',
                                        'user_name': vehicle.user_name if vehicle else '',
                                        'unit': vehicle.unit if vehicle else '',
                                        'issued_date': vehicle.issued_date.strftime('%Y-%m-%d') if vehicle else '',
                                        'expired_date': vehicle.expired_date.strftime('%Y-%m-%d') if vehicle else '',
                                        'entry_time': history.entry_time.strftime('%Y-%m-%d %H:%M:%S') if history else '',
                                        'avatar_url': vehicle.avatar.url if vehicle and vehicle.avatar else '',
                                    },
                                    'img_b64': img_b64,
                                    'frame_time': frame_count / fps
                                }
                            else:
                                # Xử lý cho xe vào
                                if vehicle:
                                    vehicle_data = {
                                        'plate': plate_text,
                                        'status': 'registered',
                                        'user_info': {
                                            'user_name': vehicle.user_name,
                                            'unit': vehicle.unit,
                                            'model': vehicle.model,
                                            'license_plate': vehicle.license_plate,
                                            'issued_date': vehicle.issued_date.strftime('%Y-%m-%d'),
                                            'expired_date': vehicle.expired_date.strftime('%Y-%m-%d'),
                                            'phone_number': vehicle.phone_number,
                                            'entry_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                            'avatar_url': vehicle.avatar.url if vehicle.avatar else '',
                                        },
                                        'img_b64': img_b64,
                                        'frame_time': frame_count / fps
                                    }
                                else:
                                    vehicle_data = {
                                        'plate': plate_text,
                                        'status': 'unregistered',
                                        'user_info': {
                                            'license_plate': plate_text,
                                            'model': ''
                                        },
                                        'img_b64': img_b64,
                                        'frame_time': frame_count / fps
                                    }
                            
                            detected_vehicles.append(vehicle_data)
            
            frame_count += 1
        
        cap.release()
        os.remove(temp_path)

        detected_vehicles.sort(key=lambda x: x['frame_time'])
        
        if detected_vehicles:
            return JsonResponse({
                'success': True,
                'total_vehicles': len(detected_vehicles),
                'vehicles': detected_vehicles
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Không phát hiện được biển số nào trong video'
            })
            
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def save_checkin_history(request):
    if request.method == 'POST':
        data = request.POST
        plate = data['license_plate']
        action = data['action']
        status = data['status']
        
        vehicle = Vehicle.objects.filter(license_plate__iexact=plate).first()
        
        if action == 'in':
            history = History.objects.create(
                license_plate=plate,
                status=status,
                action_type='inlot',
                entry_time=datetime.datetime.now(),
                vehicle=vehicle
            )
        else:
            history = History.objects.filter(
                license_plate__iexact=plate,
                action_type='inlot',
                exit_time__isnull=True
            ).first()
            
            if history:
                history.action_type = 'done'
                history.exit_time = datetime.datetime.now()
                history.save()

        return JsonResponse({'success': True, 'message': 'History updated'})
        
    return JsonResponse({'error': 'Invalid request'}, status=400)

def checkin_view(request):
    return render(request, 'checkin.html')

def history_view(request):
    keyword = request.GET.get('search', '').strip()
    histories = History.objects.all().order_by('-entry_time')
    if keyword:
        histories = histories.filter(
            vehicle__user_name__icontains=keyword
        ) | histories.filter(
            vehicle__unit__icontains=keyword
        ) | histories.filter(
            vehicle__model__icontains=keyword
        ) | histories.filter(
            license_plate__icontains=keyword
        )
    return render(request, 'history.html', {'histories': histories, 'search': keyword})

def dashboard_view(request):
    today = datetime.datetime.now().date()
    date_filter = request.GET.get('date', today.strftime('%Y-%m-%d'))
    try:
        filter_date = datetime.datetime.strptime(date_filter, '%Y-%m-%d').date()
    except:
        filter_date = today

    daily_stats = {
        'total_vehicles': History.objects.filter(
            entry_time__date=filter_date
        ).count(),
        
        'current_vehicles': History.objects.filter(
            action_type='inlot'
        ).count(),
        
        'active_users': Vehicle.objects.filter(
            expired_date__gte=today
        ).count(),
    }

    completed_parkings = History.objects.filter(
        entry_time__date=filter_date,
        action_type='done',
        exit_time__isnull=False
    )
    
    if completed_parkings.exists():
        total_duration = datetime.timedelta(0)
        count = 0
        for parking in completed_parkings:
            duration = parking.exit_time - parking.entry_time
            total_duration += duration
            count += 1
        avg_duration = total_duration / count
        hours = int(avg_duration.total_seconds() // 3600)
        minutes = int((avg_duration.total_seconds() % 3600) // 60)
        daily_stats['avg_duration'] = f"{hours:02d}:{minutes:02d}:00"
    else:
        daily_stats['avg_duration'] = "00:00:00"

    hourly_data = []
    for hour in range(24):
        count = History.objects.filter(
            entry_time__date=filter_date,
            entry_time__hour=hour
        ).count()
        hourly_data.append({
            'hour': f"{hour:02d}:00",
            'count': count
        })

    return render(request, 'dashboard.html', {
        'stats': daily_stats,
        'hourly_data': hourly_data,
        'selected_date': filter_date.strftime('%Y-%m-%d'),
        'today_date': today.strftime('%Y-%m-%d')
    })

@csrf_exempt
def check_vehicle(request):
    plate = request.GET.get('plate', '').strip()
    process_type = request.GET.get('type', 'in')
    if not plate:
        return JsonResponse({'error': 'Missing plate number'}, status=400)
    
    vehicle = Vehicle.objects.filter(license_plate__iexact=plate).first()
    
    if process_type == 'out':
        history = History.objects.filter(
            license_plate__iexact=plate,
            action_type='inlot',
            exit_time__isnull=True
        ).first()
        status = 'inlot' if history else 'not_in_lot'
        return JsonResponse({
            'status': status,
            'vehicle': {
                'user_name': vehicle.user_name if vehicle else '',
                'unit': vehicle.unit if vehicle else '',
                'model': vehicle.model if vehicle else '',
                'license_plate': plate,
                'issued_date': vehicle.issued_date.strftime('%Y-%m-%d') if vehicle else '',
                'expired_date': vehicle.expired_date.strftime('%Y-%m-%d') if vehicle else '',
                'entry_time': history.entry_time.strftime('%Y-%m-%d %H:%M:%S') if history else '',
                'avatar_url': vehicle.avatar.url if vehicle and vehicle.avatar else '',
            } if vehicle or history else None
        })
    else:
        return JsonResponse({
            'registered': bool(vehicle),
            'vehicle': {
                'user_name': vehicle.user_name,
                'unit': vehicle.unit,
                'model': vehicle.model,
                'license_plate': vehicle.license_plate,
                'issued_date': vehicle.issued_date.strftime('%Y-%m-%d'),
                'expired_date': vehicle.expired_date.strftime('%Y-%m-%d'),
                'entry_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'avatar_url': vehicle.avatar.url if vehicle and vehicle.avatar else '',
            } if vehicle else None
        })