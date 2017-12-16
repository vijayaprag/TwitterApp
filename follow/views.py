from django.contrib.auth.models import User
from bootcamp.follow.models import Contact

def user_detail(request, username):

    user = get_object_or_404(User, username=username,is_active=True)

    context = {

        'section': 'people',

        'user': user

    }

    template = 'follow/details.html'

    return render(request, template, context)