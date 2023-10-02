from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout

from .models import KeyMessage
from .forms import PostForm

from .config import DEFAULT_PASSWORDS


@csrf_exempt
def user_login(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        # Validating credentials with the database
        user = authenticate(request, username=username, password=password)
        if user:
            if password in DEFAULT_PASSWORDS:
                '''
                    if user password matches with default passwords
                    render the user to password management page
                '''
                return HttpResponseRedirect(reverse("home"))

            if list(user.groups.all()):
                '''
                    if user not tagged to the any project render error message to UI
                    else render to the respective home page 
                '''
                project = user.groups.all()[0].name
            else:
                context['error'] = f"Please tag the project : {username}"
                return render(request, "intel_app/login.html", context)

            # redirecting to home screen
            login(request, user)
            request.session['meta_data'] = {'user_id': username, 'project': project}
            return HttpResponseRedirect(reverse("home"))
        else:
            context['error'] = "provide valid credentials"
            return render(request, "intel_app/login.html", context)
    else:
        return render(request, "intel_app/login.html")


def user_logout(request):
    logout(request)
    try:
        del request.session['meta_data']
    except KeyError:
        pass
    return HttpResponseRedirect(reverse('login'))


def forgot_password(request):
    return render(request, 'intel_app/forgot_password.html')


def home(request):
    # print(request.session['meta_data'])
    return render(request, 'intel_app/index.html')


@csrf_exempt
def key_message(request):
    if request.method == "POST":
        message = request.POST['hiddenInput']
        ''' storing data into database'''
        key_message_table = KeyMessage.objects.create(
            message=message
        )
        key_message_table.save()
        return HttpResponseRedirect(reverse("key_message"))
    else:
        key_mess_data = KeyMessage.objects.all()
        print(key_mess_data)
        return render(request, 'intel_app/key_message.html', {'data': key_mess_data})


@csrf_exempt
def key_message_test(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('New Forum Successfully Added')
    else:
        form = PostForm()
        context = {
            'form': form
        }

    return render(request, 'intel_app/key_message_test.html', context)

def post_list(request):
    post_view = KeyMessage.objects.all()
    for i in post_view:
        print(i.body)
    return render(request, 'intel_app/post_list.html', {'post': post_view})


