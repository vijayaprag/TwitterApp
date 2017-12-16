from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from autoslug import AutoSlugField
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count

import markdown
from taggit.managers import TaggableManager

#from django.db.models import Count
#from bootcamp.activities.models import Activity

CATEGORY= [
    ('news', 'News'),
    ('politics', 'Politics'),
    ('sports', 'Sports'),
    ('technology', 'Technology'),
    ('art', 'Art'),
    ('entertainmnet', 'Entertainmnet'),
    ('science', 'Science'),
    ('music', 'Music'),
    ('nature', 'Nature'),
    ]

@python_2_unicode_compatible
class Article(models.Model):
    DRAFT = 'D'
    PUBLISHED = 'P'
    STATUS = (
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
    )


    #category = models.ForeignKey('Category', null=True, blank=True)
    #category = models.CharField(max_length=3, choices=CATEGORY)
    title = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='title')
    tags = TaggableManager()
    content = models.TextField(max_length=4000)
    status = models.CharField(max_length=1, choices=STATUS, default=DRAFT)
    create_user = models.ForeignKey(User)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    update_user = models.ForeignKey(User, null=True, blank=True,
                                    related_name="+")

    #likes = models.IntegerField(default=0)
    #likes = models.ManyToManyField(User, related_name="likes")
    #comment = models.CharField(max_length=500)

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ("-create_date",)
        #ordering = ("-title",)
        #ordering = ("-comment_count",)
        #ordering = ['-create_date', '-title']
        #ordering = ['-title','-create_date']
        #ordering = ['create_date', 'title', 'create_user']

    def __str__(self):
        return self.title

    def get_content_as_markdown(self):
        return markdown.markdown(self.content, safe_mode='escape')

    @staticmethod
    def get_published():
       articles = Article.objects.filter(status=Article.PUBLISHED)
       #articles = Article.objects.annotate(comment_count=Count('comments')).filter(status=Article.PUBLISHED).filter(comment_count__gt=0).order_by('-comment_count')
       #articles = Article.objects.filter(status=Article.PUBLISHED).order_by('-comment_count')
       # articles = Article.objects.annotate(num_comments=Count('comment')).order_by('-num_comments')
       return articles

    @staticmethod
    def get_counted_tags():
        tag_dict = {}
        query = Article.objects.filter(status='P').annotate(tagged=Count(
            'tags')).filter(tags__gt=0)
        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1

                else:  # pragma: no cover
                    tag_dict[tag] += 1

        return tag_dict.items()

    def get_summary(self):
        if len(self.content) > 255:
            return '{0}...'.format(self.content[:255])
        else:
            return self.content

    def get_summary_as_markdown(self):
        return markdown.markdown(self.get_summary(), safe_mode='escape')

    def get_comments(self):
        return ArticleComment.objects.filter(article=self)

    #def calculate_likes(self):
     #   likes = Activity.objects.filter(activity_type=Activity.LIKE,
      #                                  article=self.pk).count()
      #  self.likes = likes
      #  self.save()
      #  return self.likes

   # def get_likes(self):
       # likes = Activity.objects.filter(activity_type=Activity.LIKE,
      ###                                  article=self.pk)
      #  return likes

    #def get_likers(self):
     #   likes = self.get_likes()
      #  likers = []
      #  for like in likes:
      #      likers.append(like.user)
      #  return likers


    #def get_cat_list(self):           #for now ignore this instance method,
       # k = self.category
       # breadcrumb = ["dummy"]
       # while k is not None:
       #     breadcrumb.append(k.slug)
       #     k = k.parent

      #  for i in range(len(breadcrumb)-1):
       #     breadcrumb[i] = '/'.join(breadcrumb[-1:i-1:-1])
       # return breadcrumb[-1:0:-1]


@python_2_unicode_compatible
class ArticleComment(models.Model):
    article = models.ForeignKey(Article)
    comment = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)

    class Meta:
        verbose_name = _("Article Comment")
        verbose_name_plural = _("Article Comments")
        ordering = ("date",)
        #ordering = ("comment",)

    def __str__(self):
        return '{0} - {1}'.format(self.user.username, self.article.title)

    def get_comment_as_markdown(self):
        return markdown.markdown(self.comment, safe_mode='escape')






#class Category(models.Model):
 #   name = models.CharField(max_length=200)
  #  slug = models.SlugField()
   # parent = models.ForeignKey('self',blank=True, null=True ,related_name='children')

    #class Meta:
    #    unique_together = ('slug', 'parent',)    #enforcing that there can not be two
      #  verbose_name_plural = "categories"       #categories with same slug of a parent
                                                 #category

    #def __str__(self):                           # __str__ method elaborate later in post
     #   full_path = [self.name]                  #use __unicode__ instead of __str__ in
      #  k = self.parent                          #if you using python2

        #while k is not None:
         #   full_path.append(k.name)
         #   k = k.parent

        #return ' -> '.join(full_path[::-1])