import os
import json

from django.shortcuts import get_object_or_404
from django.conf import settings as django_settings
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import redirect, render

from bootcamp.core.forms import ChangePasswordForm, ProfileForm, ContactForm,ContactFormEmail
from bootcamp.feeds.views import FEEDS_NUM_PAGES, feeds
from bootcamp.feeds.models import Feed
from bootcamp.articles.models import Article, ArticleComment
from bootcamp.questions.models import Question, Answer
from bootcamp.activities.models import Activity
from bootcamp.messenger.models import Message

#from django.contrib.auth.models import Group
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template

from django.shortcuts import render_to_response
from django.views.decorators.http import condition
from forms import SearchForm
from django.template import RequestContext
from utils import stream_response

from PIL import Image
import requests

#from pusher import Pusher
#pusher = Pusher(app_id=u'295876', key=u'4b34c484eeb9fe4f4142', secret=u'6b17e2a894fc39296783')
#from django.views.decorators.csrf import csrf_exempt


def home(request):
    if request.user.is_authenticated():
        return feeds(request)
    else:
        return render(request, 'core/cover.html')


@login_required
def network(request):
    users_list = User.objects.filter(is_active=True).order_by('username')
    paginator = Paginator(users_list, 15)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)

    except PageNotAnInteger:
        users = paginator.page(1)

    except EmptyPage:  # pragma: no cover
        users = paginator.page(paginator.num_pages)

    return render(request, 'core/network.html', {'users': users})


@login_required
def profile(request, username):
    page_user = get_object_or_404(User, username=username)
    all_feeds = Feed.get_feeds().filter(user=page_user)
    paginator = Paginator(all_feeds, FEEDS_NUM_PAGES)
    feeds = paginator.page(1)
    from_feed = -1
    if feeds:  # pragma: no cover
        from_feed = feeds[0].id

    feeds_count = Feed.objects.filter(user=page_user).count()
    article_count = Article.objects.filter(create_user=page_user).count()
    article_comment_count = ArticleComment.objects.filter(
        user=page_user).count()
    question_count = Question.objects.filter(user=page_user).count()
    answer_count = Answer.objects.filter(user=page_user).count()
    activity_count = Activity.objects.filter(user=page_user).count()
    messages_count = Message.objects.filter(
        Q(from_user=page_user) | Q(user=page_user)).count()
    data, datepoints = Activity.daily_activity(page_user)
    data = {
        'page_user': page_user,
        'feeds_count': feeds_count,
        'article_count': article_count,
        'article_comment_count': article_comment_count,
        'question_count': question_count,
        'global_interactions': activity_count + article_comment_count + answer_count + messages_count,  # noqa: E501
        'answer_count': answer_count,
        'bar_data': [
            feeds_count, article_count, article_comment_count, question_count,
            answer_count, activity_count],
        'bar_labels': json.dumps('["Feeds", "Articles", "Comments", "Questions", "Answers", "Activities"]'),  # noqa: E501
        'line_labels': datepoints,
        'line_data': data,
        'feeds': feeds,
        'from_feed': from_feed,
        'page': 1
        }

    return render(request, 'core/profile.html', data)

@login_required
def settings(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.profile.job_title = form.cleaned_data.get('job_title')
            user.email = form.cleaned_data.get('email')
            user.profile.url = form.cleaned_data.get('url')
            user.profile.location = form.cleaned_data.get('location')
            user.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Your profile was successfully edited.')

    else:
        form = ProfileForm(instance=user, initial={
            'job_title': user.profile.job_title,
            'url': user.profile.url,
            'location': user.profile.location
            })

    return render(request, 'core/settings.html', {'form': form})


@login_required
def picture(request):
    uploaded_picture = False
    try:
        if request.GET.get('upload_picture') == 'uploaded':
            uploaded_picture = True

    except Exception:  # pragma: no cover
        pass

    return render(request, 'core/picture.html',
                  {'uploaded_picture': uploaded_picture})


@login_required
def coverpicture(request):

    uploaded_cover_picture = False

    try:
        if request.GET.get('cover_upload_picture') == 'uploadedcover':
            uploaded_cover_picture = True

    except Exception:  # pragma: no cover
        pass

    return render(request, 'core/coverpicture.html',
                  {'uploaded_cover_picture': uploaded_cover_picture,
                  })



@login_required
def password(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.add_message(request, messages.SUCCESS,
                                 'Your password was successfully changed.')
            return redirect('password')

    else:
        form = ChangePasswordForm(instance=user)

    return render(request, 'core/password.html', {'form': form})


@login_required
def upload_picture(request):
    try:
        profile_pictures = django_settings.MEDIA_ROOT + '/profile_pictures/'
        if not os.path.exists(profile_pictures):
            os.makedirs(profile_pictures)
        f = request.FILES['picture']
        filename = profile_pictures + request.user.username + '_tmp.jpg'
        with open(filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        im = Image.open(filename)
        width, height = im.size
        if width > 350:
            new_width = 350
            new_height = (height * 350) / width
            new_size = new_width, new_height
            im.thumbnail(new_size, Image.ANTIALIAS)
            im.save(filename)

        return redirect('/settings/picture/?upload_picture=uploaded')

    except Exception as e:
        return redirect('/settings/picture/')


@login_required
def save_uploaded_picture(request):
    try:
        x = int(request.POST.get('x'))
        y = int(request.POST.get('y'))
        w = int(request.POST.get('w'))
        h = int(request.POST.get('h'))
        tmp_filename = django_settings.MEDIA_ROOT + '/profile_pictures/' +\
            request.user.username + '_tmp.jpg'
        filename = django_settings.MEDIA_ROOT + '/profile_pictures/' +\
            request.user.username + '.jpg'
        im = Image.open(tmp_filename)
        cropped_im = im.crop((x, y, w+x, h+y))
        cropped_im.thumbnail((200, 200), Image.ANTIALIAS)
        cropped_im.save(filename)
        os.remove(tmp_filename)

    except Exception:
        pass

    return redirect('/settings/picture/')





@login_required
def cover_upload_picture(request):
    try:
        cover_pictures = django_settings.MEDIA_ROOT + '/cover_pictures/'
        if not os.path.exists(cover_pictures):
            os.makedirs(cover_pictures)
        f = request.FILES['coverpicture']
        filename = cover_pictures + request.user.username + '_tmp.jpg'
        with open(filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        im = Image.open(filename)
        width, height = im.size
        if width > 1000:
            new_width = 1000
            new_height = (height * 1000) / width
            new_size = new_width, new_height
            im.thumbnail(new_size, Image.ANTIALIAS)
            im.save(filename)

        return redirect('/settings/coverpicture/?cover_upload_picture=uploadedcover')

    except Exception as e:
        return redirect('/settings/coverpicture/')


@login_required
def save_cover_uploaded_picture(request):
    try:
       # x = int(request.POST.get('x'))
       # y = int(request.POST.get('y'))
        #w = int(request.POST.get('w'))
       # h = int(request.POST.get('h'))
        tmp_filename = django_settings.MEDIA_ROOT + '/cover_pictures/' +\
            request.user.username + '_tmp.jpg'
        filename = django_settings.MEDIA_ROOT + '/cover_pictures/' +\
            request.user.username + '.jpg'
        im = Image.open(tmp_filename)
        #cropped_im = im.crop((x, y, w+x, h+y))
        #cropped_im.thumbnail((500, 500), Image.ANTIALIAS)
        #cropped_im.save(filename)
        im.save(filename)
        os.remove(tmp_filename)

    except Exception:
        pass

    return redirect('/settings/coverpicture/')

@login_required
def email(request):
    if request.method == 'GET':
        form = ContactFormEmail()
    else:
        form = ContactFormEmail(request.POST)
        if form.is_valid():
            #subject = form.cleaned_data['subject']
            #from_email = form.cleaned_data['from_email']
            #message = form.cleaned_data['message']
            subject = request.POST.get('subject', '')
            message = request.POST.get('message', '')
            from_email = request.POST.get('from_email', '')
            try:
                send_mail(subject, message, from_email, ['djangopychecker@gmail.com','eeeee@gmail.com','xxxx@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            #return redirect('thanks')
            return HttpResponseRedirect('/thankyou/')
    return render(request, "core/email.html", {'form': form})

def thanks(request):
   return HttpResponse('Thank you for your message.')

def thankyou(request):
    #return render(request, "core/thankyou.html", {'form': form})
    #return redirect('core/thankyou.html')
    return render(request, "core/thankyou.html")

@login_required
def contact(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            #subject = form.cleaned_data['subject']
            #from_email = form.cleaned_data['from_email']
            #message = form.cleaned_data['message']
            subject = request.POST.get('subject', '')
            message = request.POST.get('message', '')
            from_email = request.POST.get('from_email', '')
            try:
                send_mail(subject, message, from_email, ['djangopychecker@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            #return redirect('thanks')
            return HttpResponseRedirect('/thankyouinvite/')
    return render(request, "core/contact.html", {'form': form})

    #form_class = ContactForm
    #return render(request, 'core/contact.html', {
       # 'form': form_class,
   # })

    #form_class = ContactForm
    #if request.method == 'POST':
       # form = form_class(data=request.POST)
        #if form.is_valid():
         #   contact_name = request.POST.get('contact_name', '')
          #  contact_email = request.POST.get('contact_email', '')
          #  form_content = request.POST.get('content', '')
          #  template = get_template('contact_template.txt')
          #  context = Context({
             #   'contact_name': contact_name,
             #   'contact_email': contact_email,
              #  'form_content': form_content,
           # })
            #content = template.render(context)
            #email = EmailMessage(
              #  "New contact form submission",
              #  content,
               # "Your website" +'',
               # ['djangopychecker@gmail.com'],
              #  headers = {'Reply-To': contact_email }
            #)
           # email.send()
            #return redirect('contact')
        #return HttpResponseRedirect('/contact/')
    #return render(request, 'core/contact.html', {
       # 'form': form_class,
   # })
def thanksinvite(request):
   return HttpResponse('Thank you for Invite.')

def thankyouinvite(request):
    #return render(request, "core/thankyou.html", {'form': form})
    #return redirect('core/thankyou.html')
    return render(request, "core/thankyouinvite.html")
@login_required
def trending(request):
    return render(request, "core/trending.html")

@login_required
def news(request):
    return render(request, "core/news.html")

@login_required
def newsfeed(request):
    return render(request, "core/newsfeed.html")


@login_required
def postcrawler(request):
     #return render_to_response('core/postcrawler.html', context_instance=RequestContext(request))
    return render(request, "core/postcrawler.html")

   ## if request.method == 'POST':
       # context = RequestContext(request)
       # form = SearchForm(request.POST)
       # if form.is_valid():
        #    return HttpResponse(stream_response(
               # request.POST['url'],
              #  request.POST['depth'],
               # request.POST['search']), mimetype='text/html')
    #return render(request, "core/postcrawler.html",context)


#import urllib
@condition(etag_func=None)
def searchcrawler(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            return HttpResponse(stream_response(
                request.POST['url'],
                request.POST['depth'],
                request.POST['search']), mimetype='text/html')
    else:
        #form = SearchForm(request.POST)
       return render(request, "core/postcrawler.html")

       # response = requests.GET('https://gab.ai/home')
        ##result = do_something_with_response(response)
        #return HttpResponse(result)


    #link = "https://programminghistorian.org/lessons/working-with-web-pages"
   # f = urllib.urlopen(link)
    #myfile = f.read()
    #f = open('test12.html', 'w')
    #f.write(myfile)
    #f.close

from django.http import JsonResponse
def follow_user(request, user_profile_id):
    profile_to_follow = get_object_or_404(profile, pk=user_profile_id)
    user_profile = request.user.userprofile
    data = {}
    if profile_to_follow.follows.filter(id=user_profile.id).exists():
        data['message'] = "You are already following this user."
    else:
        profile_to_follow.follows.add(user_profile)
        data['message'] = "You are now following {}".format(profile_to_follow)
    return JsonResponse(data, safe=False)



#@login_required(login_url='/admin/login/')
@login_required
def chat(request):
    #return render(request,"core/chat.html");
    return render(request, "core/chat.html")


#@csrf_exempt
#def broadcast(request):

  #  pusher.trigger(u'a_channel', u'an_event', {u'name': request.user.username, u'message': request.POST['message']})
   # return HttpResponse("done");