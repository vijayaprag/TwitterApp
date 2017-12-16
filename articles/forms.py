from django import forms

from bootcamp.articles.models import Article

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

class ArticleForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=255)
    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        max_length=4000)

    #category= forms.CharField(label='Select categroy', widget=forms.Select(choices=CATEGORY))
    #category = forms.ChoiceField(choices=CATEGORY, required=True )

    class Meta:
        model = Article
        #fields = ['title', 'content', 'category', 'tags', 'status']
        fields = ['title', 'content', 'tags', 'status']
