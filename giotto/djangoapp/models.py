import datetime
import pickle
import re
import bcrypt

from giotto import get_config
from giotto.exceptions import InvalidInput

from django.db import models

class DBKeyValueManager(models.Manager):
    def cache_set(self, key, obj, expire):
        p = pickle.dumps(obj)
        when_expire = datetime.datetime.now() + datetime.timedelta(seconds=expire)
        exists = self.filter(key=key, expires__lt=datetime.datetime.now()).exists()
        if exists:
            self.filter(key=key).update(value=p, expires=when_expire)
        else:
            self.create(key=key, value=p, expires=when_expire)

    def cache_get(self, key):
        try:
            hit = DBKeyValue.objects.get(key=key, expires__gt=datetime.datetime.now())
            return pickle.loads(str(hit.value))
        except DBKeyValue.DoesNotExist:
            return None

class DBKeyValue(models.Model):
    key = models.TextField(primary_key=True)
    value = models.TextField()
    expires = models.DateTimeField()

    objects = DBKeyValueManager()

class UserManager(models.Manager):
    def get_user_by_password(self, username, password):
        """
        Given a username and a raw, unhashed password, get the corresponding
        user, retuns None if no match is found.
        """
        try:
            user = self.get(username=username)
        except User.DoesNotExist:
            return None
        
        if bcrypt.hashpw(password, user.pass_hash) == user.pass_hash:
            return user
        else:
            return None

    def get_user_by_hash(self, username, hash):
        return self.get(username=username, pass_hash=hash)

    def create_user(self, username, password):
        if password == '':
            # skip hashing process if the password field is left blank
            # helpful for creating mock user objects without slowing things down.
            pass_hash = ''
        else:
            pass_hash = bcrypt.hashpw(password, bcrypt.gensalt())
        r = get_config('auth_regex', r'^[\d\w]{4,30}$')
        errors = {}
        if not re.match(r, username):
            errors['username'] = {'message': 'Username not valid', 'value': username}
        if len(password) < 4:
            errors['password'] = {'message': 'Password much be at least 4 characters'}
        if User.objects.filter(username=username).exists():
            errors['username'] = {'message': 'Username already exists', 'value': username}

        if errors:
            raise InvalidInput("User data not valid", **errors)

        return User.objects.create(username=username, pass_hash=pass_hash)


class User(models.Model):
    username = models.TextField(primary_key=True)
    pass_hash = models.TextField()

    objects = UserManager()

    def __unicode__(self):
        return "%s, %s" % (self.username, self.pass_hash)