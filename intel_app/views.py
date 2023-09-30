from django.shortcuts import render

# Create your views here.

def index(request):
    print('test')
    return render(request, 'intel_app/index2.html')
