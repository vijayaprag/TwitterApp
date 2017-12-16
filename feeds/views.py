import json
#import os

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden)
from django.shortcuts import get_object_or_404, render
from django.template.context_processors import csrf
from django.template.loader import render_to_string

from bootcamp.activities.models import Activity
from bootcamp.decorators import ajax_required
from bootcamp.feeds.models import Feed

from django.contrib.auth.models import  User
#from bootcamp.articles.forms import ArticleForm
#from bootcamp.articles.models import Article

from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy

FEEDS_NUM_PAGES = 20
#from django.conf import settings as django_settings
#from PIL import Image

#from django.contrib.auth.decorators import login_required
#from django.db.models.loading import cache
#from django.http import HttpResponse, HttpResponseRedirect, \
 #   HttpResponseServerError, HttpResponseBadRequest
#from follow.utils import follow as _follow, unfollow as _unfollow, toggle as _toggle




@login_required
def feeds(request):
    all_feeds = Feed.get_feeds()
    paginator = Paginator(all_feeds, FEEDS_NUM_PAGES)
    feeds = paginator.page(1)
    from_feed = -1
    if feeds:
        from_feed = feeds[0].id



    users_list = User.objects.filter(is_active=True).order_by('username')
    #User.following.all() # all users this user is following
    #User.followed_by.all() # all users who follow this user
    paginator = Paginator(users_list, 15)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)

    except PageNotAnInteger:
        users = paginator.page(1)

    except EmptyPage:  # pragma: no cover
        users = paginator.page(paginator.num_pages)



 #all_articles = Feed.get_published()
  #  paginator = Paginator(articles, 10)
   # try:
   #     articles = paginator.page(page)

   # except PageNotAnInteger:
    #    articles = paginator.page(1)

    #except EmptyPage:   # pragma: no cover
    #    articles = paginator.page(paginator.num_pages)

   # popular_tags = Article.get_counted_tags()


    return render(request, 'feeds/feeds.html', {
        'feeds': feeds,
        'from_feed': from_feed,
        'page': 1,
        'users': users,
        #'all_articles': all_articles,
        #'popular_tags': popular_tags,
        })




def feed(request, pk):
    feed = get_object_or_404(Feed, pk=pk)
    return render(request, 'feeds/feed.html', {'feed': feed})


@login_required
@ajax_required
def load(request):
    from_feed = request.GET.get('from_feed')
    page = request.GET.get('page')
    feed_source = request.GET.get('feed_source')
    all_feeds = Feed.get_feeds(from_feed)
    if feed_source != 'all':
        all_feeds = all_feeds.filter(user__id=feed_source)
    paginator = Paginator(all_feeds, FEEDS_NUM_PAGES)
    try:
        feeds = paginator.page(page)
    except PageNotAnInteger:
        return HttpResponseBadRequest()
    except EmptyPage:
        feeds = []
    html = ''
    csrf_token = (csrf(request)['csrf_token'])
    for feed in feeds:
        html = '{0}{1}'.format(html,
                               render_to_string('feeds/partial_feed.html',
                                                {
                                                    'feed': feed,
                                                    'user': request.user,
                                                    'csrf_token': csrf_token
                                                    }))

    return HttpResponse(html)


def _html_feeds(last_feed, user, csrf_token, feed_source='all'):
    feeds = Feed.get_feeds_after(last_feed)
    if feed_source != 'all':
        feeds = feeds.filter(user__id=feed_source)
    html = ''
    for feed in feeds:
        html = '{0}{1}'.format(html,
                               render_to_string('feeds/partial_feed.html',
                                                {
                                                    'feed': feed,
                                                    'user': user,
                                                    'csrf_token': csrf_token
                                                    }))

    return html


@login_required
@ajax_required
def load_new(request):
    last_feed = request.GET.get('last_feed')
    user = request.user
    csrf_token = (csrf(request)['csrf_token'])
    html = _html_feeds(last_feed, user, csrf_token)
    return HttpResponse(html)


@login_required
@ajax_required
def check(request):
    last_feed = request.GET.get('last_feed')
    feed_source = request.GET.get('feed_source')
    feeds = Feed.get_feeds_after(last_feed)
    if feed_source != 'all':
        feeds = feeds.filter(user__id=feed_source)

    count = feeds.count()
    return HttpResponse(count)


@login_required
@ajax_required
def post(request):
    last_feed = request.POST.get('last_feed')
    user = request.user
    csrf_token = (csrf(request)['csrf_token'])
    feed = Feed()
    feed.user = user
    post = request.POST['post']
    post = post.strip()
    if len(post) > 0:
        feed.post = post[:4000]
        feed.save()
    html = _html_feeds(last_feed, user, csrf_token)
    return HttpResponse(html)


@login_required
@ajax_required
def like(request):
    feed_id = request.POST['feed']
    feed = Feed.objects.get(pk=feed_id)
    user = request.user
    like = Activity.objects.filter(activity_type=Activity.LIKE, feed=feed_id,
                                   user=user)
    if like:
        user.profile.unotify_liked(feed)
        like.delete()

    else:
        like = Activity(activity_type=Activity.LIKE, feed=feed_id, user=user)
        like.save()
        user.profile.notify_liked(feed)

    return HttpResponse(feed.calculate_likes())


@login_required
@ajax_required
def comment(request):
    if request.method == 'POST':
        feed_id = request.POST['feed']
        feed = Feed.objects.get(pk=feed_id)
        post = request.POST['post']
        post = post.strip()
        if len(post) > 0:
            post = post[:1000]
            user = request.user
            feed.comment(user=user, post=post)
            user.profile.notify_commented(feed)
            user.profile.notify_also_commented(feed)
        return render(request, 'feeds/partial_feed_comments.html',
                      {'feed': feed})

    else:
        feed_id = request.GET.get('feed')
        feed = Feed.objects.get(pk=feed_id)
        return render(request, 'feeds/partial_feed_comments.html',
                      {'feed': feed})


@login_required
@ajax_required
def update(request):
    first_feed = request.GET.get('first_feed')
    last_feed = request.GET.get('last_feed')
    feed_source = request.GET.get('feed_source')
    feeds = Feed.get_feeds().filter(id__range=(last_feed, first_feed))
    if feed_source != 'all':
        feeds = feeds.filter(user__id=feed_source)
    dump = {}
    for feed in feeds:
        dump[feed.pk] = {'likes': feed.likes, 'comments': feed.comments}
    data = json.dumps(dump)
    return HttpResponse(data, content_type='application/json')


@login_required
@ajax_required
def track_comments(request):
    feed_id = request.GET.get('feed')
    feed = Feed.objects.get(pk=feed_id)
    return render(request, 'feeds/partial_feed_comments.html', {'feed': feed})


@login_required
@ajax_required
def remove(request):
    try:
        feed_id = request.POST.get('feed')
        feed = Feed.objects.get(pk=feed_id)
        if feed.user == request.user:
            likes = feed.get_likes()
            parent = feed.parent
            for like in likes:
                like.delete()
            feed.delete()
            if parent:
                parent.calculate_comments()
            return HttpResponse()
        else:
            return HttpResponseForbidden()
    except Exception:
        return HttpResponseBadRequest()


@login_required
def network(request):
    users_list = User.objects.filter(is_active=True).order_by('username')
    paginator = Paginator(users_list, 100)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)

    except PageNotAnInteger:
        users = paginator.page(1)

    except EmptyPage:  # pragma: no cover
        users = paginator.page(paginator.num_pages)

    return render(request, 'feeds/feeds.html', {'users': users})

#extracode
@login_required
def blog(request):
   # return render(request, "feeds/blog.html")
    all_feeds = Feed.get_feeds()
    paginator = Paginator(all_feeds, FEEDS_NUM_PAGES)
    feeds = paginator.page(1)
    from_feed = -1
    if feeds:
        from_feed = feeds[0].id
    users_list = User.objects.filter(is_active=True).order_by('username')
    paginator = Paginator(users_list, 15)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)

    except EmptyPage:  # pragma: no cover
        users = paginator.page(paginator.num_pages)

    return render(request, 'feeds/blog.html', {
        'blog': blog,
        'from_feed': from_feed,
        'page': 1,
        'users': users,
        })

#class EditComments(LoginRequiredMixin, UpdateView):
   # template_name = 'feeds/edit.html'
    #model = Feed
    #form_class = ArticleForm
    #success_url = reverse_lazy('feeds')


#def checking(func):
    """
    Check the permissions, http method and login state.
    """
   # def iCheck(request, *args, **kwargs):
      #  if not request.method == "POST":
          #  return HttpResponseBadRequest("Must be POST request.")
       # follow = func(request, *args, **kwargs)
       # if request.is_ajax():
        #    return HttpResponse('ok')
        #try:
         #   if 'next' in request.GET:
          #      return HttpResponseRedirect(request.GET.get('next'))
          #  if 'next' in request.POST:
          #      return HttpResponseRedirect(request.POST.get('next'))
          ##  return HttpResponseRedirect(follow.target.get_absolute_url())
        #except (AttributeError, TypeError):
           # if 'HTTP_REFERER' in request.META:
            #    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            #if follow:
             #   return HttpResponseServerError('"%s" object of type ``%s`` has no method ``get_absolute_url()``.' % (
              #      unicode(follow.target), follow.target.__class__))
           # return HttpResponseServerError('No follow object and `next` parameter found.')
   # return iCheck

#@login_required
#@check
#def follow(request, app, model, id):
  #  model = cache.get_model(app, model)
   # obj = model.objects.get(pk=id)
   # return _follow(request.user, obj)

#@login_required
#@check
#def unfollow(request, app, model, id):
   # model = cache.get_model(app, model)
   # obj = model.objects.get(pk=id)
    #return _unfollow(request.user, obj)


#@login_required
#@check
#def toggle(request, app, model, id):
   # model = cache.get_model(app, model)
    #obj = model.objects.get(pk=id)
    #return _toggle(request.user, obj)

