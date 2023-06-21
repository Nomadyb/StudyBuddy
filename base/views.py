from django.shortcuts import render
from .models import Room , Topic , Message
from .forms import RoomForm 
from django.shortcuts import redirect
from django.db.models import Q 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


# rooms = [
#     {"id":1,"name":"Let's learn Python"},
#     {"id":2,"name":"lets the scream"},
#     {"id":3,"name":"lets learn the js"},
# ]



def loginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("/")
    else:
        pass



    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")


        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,"Username does not exist")
            # return redirect("login")

        user = authenticate(request,username=username,password=password)

        if user is not None:
              login(request,user)
              return redirect("/")
        else:
            messages.error(request,"Username OR password is incorrect")
            #return redirect("login")


         
    context = {"page":page}
    return render(request,"base/login_register.html",context)


def logoutUser(request):
    logout(request)
    return redirect("login")

@csrf_exempt
def registerPage(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect("/")
        else:
            form = UserCreationForm(request.POST)
            messages.error(request,"An error occured during registration")


    context = {"form":form}
    return render(request,"base/login_register.html",context)



def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)  ) if q != '' else Room.objects.all()

    topic = Topic.objects.all()
    room_count = rooms.count()

    context = {"rooms":rooms,"topics":topic,"room_count":room_count,"search":q}
    return render(request,"base/home.html",context)




def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by("-created") 

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get("body")
        )        
        return redirect("room",pk=room.id)


    context = {"room":room,"room_messages":room_messages}
    return render(request,"base/room.html",context)


@login_required(login_url="login")
def createRoom(reguest):
    form = RoomForm()
    
    if reguest.method == "POST":
        print("Printing POST:",reguest.POST)
        form = RoomForm(reguest.POST)
        if form.is_valid():
            form.save()
            return redirect("/")

    context = {"form":form}
    return render(reguest,"base/room_form.html",context)   

@login_required(login_url="login")
def updateRoom(reguest,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if reguest.user != room.host:
        return HttpResponse("You are not allowed here")

    
    if reguest.method == "POST":
        print("Printing POST:",reguest.POST)
        form = RoomForm(reguest.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect("/")

    context = {"form":form}
    return render(reguest,"base/room_form.html",context)


@login_required(login_url="login")
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()
        return redirect("/")

    return render(request,"base/delete.html",{"obj":"room"})
