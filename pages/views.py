from django.shortcuts import render
from accounts.models import Accounts

# Create your views here.
def index(request):
    username=None
    if 'username' in request.session: username=request.session['username']

    accounts=Accounts.objects.order_by('-elo')[:4]
    context={
        'accounts': accounts,
        'username': username
    }

    return render(request,'pages/index.html',context)


