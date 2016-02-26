from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def signup(request):
	return render(request, 'projman/signup.html', None)

def submitsignup(request): #POST data is inside request
	username=request.POST.get("username", None)
	email=request.POST.get("email", None)
	password=request.POST.get("password", None)
	if username and email and password:
		User.objects.create_user(username=username, email=email, password=password)
		#newuser=ProjmanUser(user=User.objects.create_user(username=username, email=email, password=password))
		#newuser.save()
	return HttpResponse('OK')

def signin(request):
	return render(request, 'projman/signin.html', None)

def submitsignin(request):
	username=request.POST.get("username", None)
	password=request.POST.get("password", None)
	lgduser=authenticate(username=username, password=password)
	if lgduser:
		if lgduser.is_active:
			login(request, lgduser)
			print('user is authenticated and active')
			return HttpResponse('OK')
		else:
			print("The password is valid, but the account has been disabled!") #how can this happen??
	else:
		print('user does not exists') #shouldnt be happening
		return HttpResponse('401')

def signout(request):
	if request:
		logout(request)
	return index(None)

def submitnewproj(request):
	name=request.POST.get("name")
	desc=request.POST.get("description")
	if request and not request.user.is_anonymous() and name:
		user=get_object_or_404(ProjmanUser, user=request.user)
		proj=Project(name=name, description=desc, author=user)
		proj.save()
		part=Participation(user=user, project=proj)
		part.save()
	return HttpResponse('200')

def updateavatar(request):
	print(request.POST)
	#pic=request.POST.get("")
	return HttpResponse('200')

def index(request):
	if request and not request.user.is_anonymous():
		puser=get_object_or_404(ProjmanUser, user=request.user)
		partlist=Participation.objects.filter(user=puser)
		projlist= []
		for i in partlist:
			projlist.append(i.project)
		userpic=puser.avatar
		context= {'projlist': projlist, 'userpic': userpic, 'userindex': True}

		return render(request, 'projman/app.html', context)
	else:
		#TODO: separate welcome view?
		return render(request, 'projman/index.html', None)

def toggletododone(request, todoid):
	puser=get_object_or_404(ProjmanUser, user=request.user)
	todo=get_object_or_404(To_do, id=todoid)
	particip=Participation.objects.filter(project=todo.parent_project, user=puser)
	if request and not request.user.is_anonymous() and particip:
		print(type(request.POST.get("todoCheckbox")))
		print(request.POST.get("todoCheckbox"))
		#IGNOREME inverted booleans, the checkbox returns its state BEFORE it was pressed.
		if not request.POST.get("todoCheckbox") and not request.POST.get("todoCheckbox")=="":
			todo.done=False
		else:
			todo.done=True
		todo.save()

	return HttpResponse("200")

def submitnewtodo(request):
	title=request.POST.get("title")
	details=request.POST.get("details")
	proj= get_object_or_404(Project, id= request.POST.get("parentproj"))
	if request and not request.user.is_anonymous() and title:
		user=get_object_or_404(ProjmanUser, user=request.user)
		todo=To_do(title=title, details=details, author=user, parent_project=proj)
		todo.save()
		#TODO: designation
		#des=Participation(user=user, project=proj)
		#part.save()
	return HttpResponse('200')

def projview(request, projid):
	if request and not request.user.is_anonymous():
		puser=get_object_or_404(ProjmanUser, user=request.user)
		project=get_object_or_404(Project, id=projid)
		todolist=To_do.objects.filter(parent_project=project).order_by('done')
		"""partlist=Participation.objects.filter(user=puser)
		projlist= []
		for i in partlist:
			projlist.append(i.project)"""
		designations=[]
		for i in todolist:
			d=Designation.objects.filter(todo=i)
			for j in d:
				designations.append(j)

		userpic=puser.avatar
		context= {'project': project, 'todolist': todolist, 'userpic': puser.avatar, 'designations': designations}

		return render(request, 'projman/app.html', context)
	else:
		#TODO: separate welcome view?
		return render(request, 'projman/index.html', None)