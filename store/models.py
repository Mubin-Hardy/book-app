from django.db import models
from django.contrib.auth.models import User
from matplotlib.style import context
# Create your views here.
import pandas as pd
import random
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import *
df = pd.read_csv('C:\\Users\\mubin\\django_19_07_2022\\Book\\book-app\\dataset\\db2.csv',
                 header=0,
                 names=['Questions', 'Answers'])

InputTraffic = []
welcomeResponse = []
class Category(models.Model):
	name = models.CharField(max_length = 100)
	slug = models.SlugField(max_length = 150, unique=True ,db_index=True)
	icon = models.FileField(upload_to = "category/")
	create_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return self.name

class Writer(models.Model):
	name = models.CharField(max_length = 100)
	slug = models.SlugField(max_length=150, unique=True ,db_index=True)
	bio = models.TextField()
	pic = models.FileField(upload_to = "writer/")
	create_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return self.name

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
            if(cResponse=="Sorry, we do not understand your requirement"):
                histo.objects.create(message=x)
                
            
            print("user query is",user_response)
            #print("chat bot response is",cResponse)
            context = {'welcomeTrafficResp':welcomeTrafficResponse} 
            return render(request,'portal/student_signup.html',context) 

    return render(request,'portal/student_signup.html')  
class Book(models.Model):
	writer = models.ForeignKey(Writer, on_delete = models.CASCADE)
	category = models.ForeignKey(Category, on_delete = models.CASCADE)
	name = models.CharField(max_length = 100)
	slug = models.SlugField(max_length=100, db_index=True)
	price = models.IntegerField()
	stock = models.IntegerField()
	coverpage = models.FileField(upload_to = "coverpage/")
	bookpage = models.FileField(upload_to = "bookpage/")
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	totalreview = models.IntegerField(default=1)
	totalrating = models.IntegerField(default=5)
	status = models.IntegerField(default=0)
	description = models.TextField()
	status=models.TextField()


	def __str__(self):
	    return self.name

class Review(models.Model):
	customer = models.ForeignKey(User, on_delete = models.CASCADE)
	book = models.ForeignKey(Book, on_delete = models.CASCADE)
	review_star = models.IntegerField()
	review_text = models.TextField()
	created = models.DateTimeField(auto_now_add=True)

class Slider(models.Model):
	title = models.CharField(max_length=150)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	slideimg = models.FileField(upload_to = "slide/")

	def __str__(self):
		return self.title

