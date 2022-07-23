from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Category, Writer, Book, Review, Slider
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .forms import RegistrationForm, ReviewForm
import pandas as pd
import random
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import *
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate,login
from matplotlib.style import context
# Create your views here.
import pandas as pd
import random
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import *
from .forms import *


df = pd.read_csv('C:\\Users\\mubin\\django_19_07_2022\\Book\\book-app\\dataset\\db2.csv',
                 header=0,
                 names=['Questions', 'Answers'])

InputTraffic = []
welcomeResponse = []

def index(request):
    newpublished = Book.objects.order_by('-created')[:15]
    slide = Slider.objects.order_by('-created')[:3]
    context = {
        "newbooks":newpublished,
        "slide": slide
    }
    return render(request, 'store/index.html', context)

def student_signup(request):
    if request.method == "POST":
        x = request.POST['message']
        welcome = "Chatbot : You are welcome.."
        bye = "Chatbot : Bye!!! "
       
        if x:
            vectorizer = CountVectorizer()
            count_vec = vectorizer.fit_transform(df['Questions']).toarray()
            welcome_input = ("hello", "hi", "greetings", "sup", "what's up","hey",)
            welcome_response = ["Hiiiiiii", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]

            def bot(user_response):
                text = vectorizer.transform([user_response]).toarray()
                df['similarity'] = cosine_similarity(count_vec, text)
                return df.sort_values(['similarity'], ascending=False).iloc[0]['Answers']
            
            def welcome(user_response):
                for word in user_response.split():
                    if word.lower() in welcome_input:
                        return random.choice(welcome_response)

            user_response = x
            user_response = user_response.lower()
            InputTraffic.append(user_response)
            if(user_response not in ['bye','shutdown','exit', 'quit']):
                    if(welcome(user_response)!=None):
                        wResponse  = welcome(user_response)
                        welcomeResponse.append(wResponse)
                        # print('welcomeResponse',welcomeResponse)
                    else:
                        # print("Chatbot : ",end="")
                        cResponse = bot(user_response)
                        welcomeResponse.append(cResponse)
                        # print('welcomeResponse',welcomeResponse)

            welcomeTrafficResponse = zip(InputTraffic,welcomeResponse)
            #if(cResponse=="Sorry, we do not understand your requirement"):
                #histo.objects.create(message=x)
                
            
            print("user query is",user_response)
            #print("chat bot response is",cResponse)
            context = {'welcomeTrafficResp':welcomeTrafficResponse} 
            return render(request,'store/student_signup.html',context) 

    return render(request,'store/student_signup.html')  
def signin(request):
    if request.user.is_authenticated:
        return redirect('store:index')
    else:
        if request.method == "POST":
            user = request.POST.get('user')
            password = request.POST.get('pass')
            auth = authenticate(request, username=user, password=password)
            if auth is not None:
                login(request, auth)
                return redirect('store:index')
            else:
            	messages.error(request, 'username and password doesn\'t match')

    return render(request, "store/login.html")	


def signout(request):
    logout(request)
    return redirect('store:index')	


def registration(request):
	form = RegistrationForm(request.POST or None)
	if form.is_valid():
		form.save()
		return redirect('store:signin')

	return render(request, 'store/signup.html', {"form": form})

def payment(request):
    return render(request, 'store/payment.html')


def get_book(request, id):
    form = ReviewForm(request.POST or None)
    book = get_object_or_404(Book, id=id)
    rbooks = Book.objects.filter(category_id=book.category.id)
    r_review = Review.objects.filter(book_id=id).order_by('-created')

    paginator = Paginator(r_review, 4)
    page = request.GET.get('page')
    rreview = paginator.get_page(page)

    if request.method == 'POST':
        if request.user.is_authenticated:
            if form.is_valid():
                temp = form.save(commit=False)
                temp.customer = User.objects.get(id=request.user.id)
                temp.book = book          
                temp = Book.objects.get(id=id)
                temp.totalreview += 1
                temp.totalrating += int(request.POST.get('review_star'))
                form.save()  
                temp.save()

                messages.success(request, "Review Added Successfully")
                form = ReviewForm()
        else:
            messages.error(request, "You need login first.")
    context = {
        "book":book,
        "rbooks": rbooks,
        "form": form,
        "rreview": rreview
    }
    return render(request, "store/book.html", context)


def get_books(request):
    books_ = Book.objects.all().order_by('-created')
    paginator = Paginator(books_, 10)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    return render(request, "store/category.html", {"book":books})

def get_book_category(request, id):
    book_ = Book.objects.filter(category_id=id)
    paginator = Paginator(book_, 10)
    page = request.GET.get('page')
    book = paginator.get_page(page)
    return render(request, "store/category.html", {"book":book})
    
def get_book_category2(request, id):
    book_ = Book.objects.all.order_by('price')
    paginator = Paginator(book_, 10)
    page = request.GET.get('page')
    book = paginator.get_page(page)
    return render(request, "store/sort.html", {"book":book})

def get_writer(request, id):
    wrt = get_object_or_404(Writer, id=id)
    book = Book.objects.filter(writer_id=wrt.id)
    context = {
        "wrt": wrt,
        "book": book
    }
    return render(request, "store/writer.html", context)

