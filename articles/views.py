from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse_lazy

import markdown
from bootcamp.articles.forms import ArticleForm
from bootcamp.articles.models import Article, ArticleComment
from bootcamp.decorators import ajax_required

#from django.db.models import DateTimeField
#from django.db.models.functions import Trunc
from bootcamp.activities.models import Activity
#from django.db.models import Count

from datetime import datetime
from django.shortcuts import render_to_response

#from django.core.mail import EmailMessage

#email = EmailMessage('title', 'test', to=['xxxx@gmail.com'])
#email.send()
#from django.core.mail import send_mail
#send_mail('Your Email subject', 'Your Email message.', 'xxxx@gmail.com', ['xxxxx@gmail.com'], fail_silently=False)
#send_mail('Your Email subject', 'Your Email message.', 'sender_email@example.com', ['recipient_email@example.com'], fail_silently=False)



def _articles(request, articles):
    paginator = Paginator(articles, 15)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)

    except PageNotAnInteger:
        articles = paginator.page(1)

    except EmptyPage:   # pragma: no cover
        articles = paginator.page(paginator.num_pages)

    popular_tags = Article.get_counted_tags()

    return render(request, 'articles/articles.html', {
        'articles': articles,
        'popular_tags': popular_tags,
       # 'months': mkmonth_lst(),
    })


#def mkmonth_lst():
  #  if not Article.objects.count(): return []
# set up vars
  #  year, month = time.localtime()[:2]
#first = Article.objects.order_by("created")[0]
   # fyear = first.created.year
   # fmonth = first.created.month
   # months = []
   # for y in range(year, fyear-1, -1):
    #    start, end = 12, 0
     #   if y == year: start = month
       # if y == fyear: end = fmonth-1

    #for m in range(start, end, -1):
      #  months.append((y, m, month_name[m]))
#return months


class CreateArticle(LoginRequiredMixin, CreateView):
    """
    """
    template_name = 'articles/write.html'
    form_class = ArticleForm
    success_url = reverse_lazy('articles')

    def form_valid(self, form):
        form.instance.create_user = self.request.user
        return super(CreateArticle, self).form_valid(form)


class EditArticle(LoginRequiredMixin, UpdateView):
    template_name = 'articles/edit.html'
    model = Article
    form_class = ArticleForm
    success_url = reverse_lazy('articles')


@login_required
def articles(request):
    all_articles = Article.get_published()
    return _articles(request, all_articles)


@login_required
def article(request, slug):
    article = get_object_or_404(Article, slug=slug, status=Article.PUBLISHED)
    return render(request, 'articles/article.html', {'article': article})


@login_required
def tag(request, tag_name):
    articles = Article.objects.filter(tags__name=tag_name).filter(status='P')
    return _articles(request, articles)


@login_required
def category(request, category_name):
    articles = Article.objects.filter(tags__name=category_name).filter(status='P')
    return _articles(request, articles)





@login_required
def drafts(request):
    drafts = Article.objects.filter(create_user=request.user,
                                    status=Article.DRAFT)
    return render(request, 'articles/drafts.html', {'drafts': drafts})


@login_required
@ajax_required
def preview(request):
    try:
        if request.method == 'POST':
            content = request.POST.get('content')
            html = 'Nothing to display :('
            if len(content.strip()) > 0:
                html = markdown.markdown(content, safe_mode='escape')

            return HttpResponse(html)

        else:
            return HttpResponseBadRequest()

    except Exception:
        return HttpResponseBadRequest()


@login_required
@ajax_required
def comment(request):
    try:
        if request.method == 'POST':
            article_id = request.POST.get('article')
            article = Article.objects.get(pk=article_id)
            comment = request.POST.get('comment')
            comment = comment.strip()
            if len(comment) > 0:
                article_comment = ArticleComment(user=request.user,
                                                 article=article,
                                                 comment=comment)
                article_comment.save()
            html = ''
            for comment in article.get_comments():
                html = '{0}{1}'.format(html, render_to_string(
                    'articles/partial_article_comment.html',
                    {'comment': comment}))

            return HttpResponse(html)

        else:
            return HttpResponseBadRequest()

    except Exception:
        return HttpResponseBadRequest()


#from django.contrib.comments.view.moderate import perform_delete
#def delete_own_comment(request, comment_id):
 #   comment = get_object_or_404(comment, id=comment_id)
 #   if comment.user.id != request.user.id:
  #      raise Http404
  #  perform_delete(request, comment)

#extra
##@login_required
#@ajax_required
#def like(request):
  #  article_id = request.POST.get('article')
  #  article = Article.objects.get(pk=article_id)
   # user = request.user
    # like = Activity.objects.filter(activity_type=Activity.LIKE, article=article_id,
    #                                user=user)
    # if like:
    #     user.profile.unotify_liked(article)
    #     like.delete()

    # # else:
     #    like = Activity(activity_type=Activity.LIKE, article=article_id, user=user)
      #   like.save()
      #   user.profile.notify_liked(article)

     #return HttpResponse(article.calculate_likes())


#def article_ordered_by_likes(request):
   # context = {'article': Article.objects.annotate(like_count=Count('likes')).order_by('-like_count')}
    #return render(request, 'articles/partial_article.html', context)

##def like_button(request):
   # if request.method == 'POST':
    #    user = request.user
     #   id = request.POST.get('pk', None)

     #  article = get_object_or_404(Article, pk=id)

      #  if article.likes.filter(id=user.id).exists():
       #     article.likes.remove(user)
      #  else:
        #    article.likes.add(user)

      #  context = {'likes_count': article.total_likes}
    #return HttpResponse(json.dumps(context), content_type='application/json')

rom_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']

def article_archive_year(request):
    arch = Article.objects.dates('data', 'month', order='DESC')
    archives = {}
    for i in arch:
        year = i.year
        month = i.month
        try:
           archives[year][month-1][1] = True
        except KeyError:

            archives[year]=[[datetime.date(year,k+1,1),False,rom] for k, rom in enumerate(rom_months)]
            archives[year][month-1][1] = True

    return render_to_response('articles/article_archive_year.html', {'archives':sorted(archives.items(),reverse=True)})


from django.views.generic.dates import YearArchiveView
class ArticleYearArchiveView(YearArchiveView):
    queryset = Article.objects.all()
    date_field = "create_date"
    make_object_list = True
    allow_future = True
#return render('articles/article_archive_year.html')


import datetime
from django import template
register = template.Library()

def sidebar_date_list():
            articles = Article.objects.filter(status='P')
            for article in articles:
                article.month = str(article.created_at.year)+'-'+str(article.created_at.month).rjust(2, '0')
            return {'articles': articles}
register.inclusion_tag('articles/articles.html')(sidebar_date_list)

