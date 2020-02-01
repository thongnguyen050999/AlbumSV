from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes,force_text
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from django.urls import reverse
from .forms import UserSignUpForm,UserLogInForm
from .token_generator import account_activation_token
from .models import Accounts
import random
import numpy as np

# Create your views here.
def index(request):
    username=None
    if 'username' in request.session: 
        username=request.session['username']
    context={
        'username': username
    }
    return render(request,'pages/index.html',context)

def logIn(request):
    next=request.GET.get('next')
    form=UserLogInForm(request.POST)
    if form.is_valid():
        username=form.cleaned_data.get('username')
        password=form.cleaned_data.get('password')
        account=authenticate(username=username,password=password)

        if account is not None:
            if account.is_active:
                login(request,account)
                request.session['username']=username
                return redirect('/')
        else:
            messages.error(request,'username or password not correct')
    context={
        'form': form
    }
    return render(request,'accounts/logIn.html',context)


def signUp(request):
    if request.method=='POST':
        form=UserSignUpForm(request.POST)
        if form.is_valid():
            account=form.save(commit=False)
            email=form.cleaned_data.get('email')
            account.is_active=False
            account.save()
            current_site=get_current_site(request)
            email_subject='Activate Your Account'
            message=render_to_string('accounts/activateAccount.html',{
                'user': account,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(account.pk)),
                'token': account_activation_token.make_token(account),
            })
            to_email=form.cleaned_data.get('email')
            email=EmailMessage(email_subject,message,to=[to_email])
            email.send()
            return render(request,'accounts/emailActivation.html')
    else:
        form=UserSignUpForm()
    return render(request,'accounts/signUp.html',{'form': form})


def activate_account(request,uidb64,token):
    try:
        uid=force_bytes(urlsafe_base64_decode(uidb64))
        account=Accounts.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Accounts.DoesNotExist):
        account=None
    if account is not None and account_activation_token.check_token(account,token):
        account.is_active=True
        account.save()
        account.backend='django.contrib.auth.backends.ModelBackend'
        login(request,account)
        return render(request,'accounts/verified.html')
    else:
        return HttpResponse('Activation link is invalid')

def logOut(request):
    request.session.flush()
    logout(request)
    return redirect('/')

def profile(request,username):
    account=get_object_or_404(Accounts,username=username)
    if 'username' in request.session: 
        username=request.session['username']
    context={
        'username': username,
        'account': account
    }

    return render(request,'accounts/profile.html',context)

def edit(request,username):
    account=get_object_or_404(Accounts,username=username)
    if 'username' in request.session: 
        username=request.session['username']
    context={
        'username': username,
        'account': account
    }
    return render(request,'accounts/edit.html',context)

def store(request,username):
    account=get_object_or_404(Accounts,username=username)
    if 'username' in request.session: 
        username=request.session['username']
    context={
        'username': username,
        'account': account
    }

    fbLink=request.POST['fbLink']
    instLink=request.POST['instLink']
    img=request.POST['img']

    account.fbLink=fbLink
    account.instLink=instLink
    account.image=img
    if img=='': account.image='default.png'
    account.save()

    return redirect('/')


##################################################################################

def explore(request):
    username=None
    if 'username' in request.session: username=request.session['username']
    accounts=Accounts.objects.order_by('-elo')[:44]

    context={
        'accounts': accounts,
        'username': username 
    }

    return render(request,'accounts/index.html',context)

def detail(request,id):
    account=Accounts.objects.get(pk=id)
    username=None
    if 'username' in request.session: username=request.session['username']

    context={
        'account': account,
        'username': username
    }

    return render(request,'accounts/detail.html',context)

def vote(request):
    username=None
    if 'username' in request.session: username=request.session['username']
    idList=[]
    for g in Accounts.objects.all(): idList.append(g.id)
    
    valid0=valid1=False

    while not valid0:
        idx0=random.randint(0,len(idList)-1)
        id0=idList[idx0]
        account0=Accounts.objects.get(pk=id0)
        if account0.valid: valid0=True

    idx1=idx0
    while not valid1: 
        while idx1==idx0: idx1=random.randint(0,len(idList)-1)
        id1=idList[idx1]
        account1=Accounts.objects.get(pk=id1)
        if account1.valid: valid1=True
        
    username=None
    if 'username' in request.session: 
        username=request.session['username']

    context={
        'account0': account0,
        'account1': account1,
        'username': username
    }
    return render(request,'accounts/vote.html',context)

def storeElo(request):
    
    id_winner=int(request.POST['id-button'])
    id0=int(request.POST['id-account0'])
    id1=int(request.POST['id-account1'])
    elo0=float(request.POST['elo-account0'])
    elo1=float(request.POST['elo-account1'])

    e1=1/(1+10**((elo0-elo1)/400))
    e0=1/(1+10**((elo1-elo0)/400))
    K=30

    if id_winner==id0:
        elo0=elo0+K*(1-e0)
        elo1=elo1+K*(0-e1)
    else:
        elo0=elo0+K*(0-e0)
        elo1=elo1+K*(1-e1)

    account0=Accounts.objects.get(pk=id0)
    account1=Accounts.objects.get(pk=id1)
    account0.elo=elo0
    account1.elo=elo1
    account0.save()
    account1.save()

    return HttpResponseRedirect(reverse('accounts:vote'))

def getEditDistance(s0,s1):
    size0=len(s0)+1
    size1=len(s1)+1
    matrix=np.zeros((size0,size1))

    for x in range(size0): matrix[x,0]=x
    for y in range(size1): matrix[0,y]=y

    for x in range(1,size0):
        for y in range(1,size1):
            if s0[x-1]==s1[y-1]: matrix[x,y]=min(matrix[x-1,y]+1,matrix[x-1,y-1],matrix[x,y-1]+1)
            else: matrix[x,y]=1+min(matrix[x-1,y],matrix[x-1,y-1],matrix[x,y-1])

    return matrix[x-1,y-1]



def findAccounts(info,fbList,instList):
    result=[]
    disList=[]
    tmp=[]
    for fb in fbList: disList.append((fb,getEditDistance(info,fb)))
    disList.sort(key=lambda x: x[1])
    for ele in disList[:3]: tmp.append(ele[0])

    for i in tmp: 
        mid=Accounts.objects.filter(fbLink=i)
        result+=[x for x in mid]

    result=[]
    disList=[]
    tmp=[]
    for inst in instList: disList.append((inst,getEditDistance(info,inst)))
    disList.sort(key=lambda x: x[1])
    for ele in disList[:3]: tmp.append(ele[0])

    for i in tmp: 
        mid=Accounts.objects.filter(instLink=i)
        result+=[x for x in mid if x not in result]
    return result


def search(request):
    username=None
    if 'username' in request.session: username=request.session['username']
    info=request.POST['search-info']
    accounts=Accounts.objects.all()

    nameList=[x.username for x in accounts]
    fbList=[x.fbLink for x in accounts]
    instList=[x.instLink for x in accounts]

    result=[]

    similarTerms=['facebook','fb','instagram','com','www','http','://']
    for word in similarTerms:
        if word in info:
            result=findAccounts(info,fbList,instList)
            context={
                'result': result,
                'username': username
            }
            return render(request,'accounts/search.html',context)

    
    result=[]
    disList=[]
    tmp=[]
    for name in nameList: disList.append((name,getEditDistance(info,name)))
    disList.sort(key=lambda x: x[1])
    for ele in disList[:3]: tmp.append(ele[0])

    for i in tmp: 
        mid=Accounts.objects.filter(username=i)
        result+=[x for x in mid if x not in result]
    context={
        'result': result,
        'username': username
    }
    return render(request,'accounts/search.html',context)

