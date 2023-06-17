from django.shortcuts import render
from .models import Room , Topic
from .forms import RoomForm 
from django.shortcuts import redirect
from django.db.models import Q 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate

# Create your views here.


# rooms = [
#     {"id":1,"name":"Let's learn Python"},
#     {"id":2,"name":"lets the scream"},
#     {"id":3,"name":"lets learn the js"},
# ]



def loginPage(request):
    if request.method == "POST":
        username = request.POST.get("username") 
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
            return redirect("login")


         
    context = {}
    return render(request,"base/login_register.html",context)


def logoutUser(request):
    logout(request)
    return redirect("login")





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
    context = {"room":room}
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


def updateRoom(reguest,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    
    if reguest.method == "POST":
        print("Printing POST:",reguest.POST)
        form = RoomForm(reguest.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect("/")

    context = {"form":form}
    return render(reguest,"base/room_form.html",context)



def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()
        return redirect("/")

    return render(request,"base/delete.html",{"obj":"room"})
