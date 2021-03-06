from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Room, Topic
from .forms import RoomForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User 
from django.contrib.auth.decorators import login_required   
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
# rooms = [
#     {'id':1, 'name':'Python'},
#     {'id':2, 'name':'Java'},
#     {'id':3, 'name':'Go'}
# ]
def home(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    rooms = Room.objects.filter(topic__name__contains=q)
    topics = Topic.objects.all()
    room_count = rooms.count()
    return render(request, 'base/home.html', {'rooms':rooms, 'topics':topics, 'room_count':room_count})

def room(request, pk):
    room = Room.objects.get(id=pk)
    context = {'room': room}
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})

def user_login(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        print('post')
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password does not exist')
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def user_logout(request):
    logout(request)
    return redirect('home')

def user_register(request):
    page='register'
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')
    context = {'form':form}
    return render(request, 'base/login_register.html', context)