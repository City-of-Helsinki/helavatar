import hashlib
import requests
import pytz
from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.core.files.base import ContentFile
from requests_ntlm import HttpNtlmAuth
from versatileimagefield.fields import VersatileImageField
from .storage import FileOverwriteStorage

GRAVATAR_SIZE = 400


def avatar_image_path(instance, filename):
    s = instance.email_hash
    parts = (s[0:2], s[2:4], s)
    return 'avatars/{}/{}/{}.jpg'.format(*parts)


class Avatar(models.Model):
    email = models.EmailField(db_index=True, unique=True)
    email_hash = models.CharField(max_length=128, db_index=True, unique=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    image = VersatileImageField(upload_to=avatar_image_path, null=True, blank=True,
                                storage=FileOverwriteStorage())

    def __str__(self):
        return "Avatar for {} ({})".format(self.email, self.email_hash)

    def set_email(self, email):
        self.email = email.strip().lower()

    def set_hash(self):
        self.email_hash = hashlib.md5(self.email.encode('utf8')).hexdigest()

    def fetch_exchange_image(self):
        auth = HttpNtlmAuth(settings.EXCHANGE_USERNAME, settings.EXCHANGE_PASSWORD)
        url = '{base}/Exchange.asmx/s/GetUserPhoto'.format(base=settings.EXCHANGE_URL)
        ret = requests.get('{url}?email={email}&size=HR360x360'.format(url=url, email=self.email),
                           auth=auth)
        if ret.status_code != 200:
            return None

        return ret.content

    def fetch_gravatar_image(self):
        ret = requests.get('https://www.gravatar.com/avatar/{hash}?d=404&s={size}'.format(
            hash=self.email_hash, size=GRAVATAR_SIZE))
        if ret.status_code != 200:
            return None

        return ret.content

    def should_update(self):
        if not self.last_updated:
            return True
        # Try to update avatars without images more frequently
        if not self.image:
            max_age = 24
        else:
            max_age = 5 * 24
        now = datetime.now(pytz.utc)
        if now - self.last_updated > timedelta(hours=max_age):
            return True
        return False

    def update_image(self):
        content = self.fetch_exchange_image()
        if not content:
            content = self.fetch_gravatar_image()
        self.last_updated = datetime.now(pytz.utc)
        if content:
            self.image.save('', ContentFile(content), save=False)
        else:
            if self.image != None:
                self.image.delete_all_created_images()
                self.image.delete()
            self.image = None
        self.save()
