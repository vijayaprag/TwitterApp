from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

class Contact(models.Model):

    """docstring for Contact."""

    user_from = models.ForeignKey(User, related_name='rel_from_set')

    user_to = models.ForeignKey(User, related_name='rel_to_set')

    created = models.DateTimeField(auto_now_add=True, db_index=True)



    class Meta:

        ordering = ('-created',)



    def __str__(self):

        return    '{} follows {}'.format(self.user_from, self.user_to)



models.ManyToManyField('self', through=Contact,related_name='followers', symmetrical=False)
