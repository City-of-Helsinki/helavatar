Helavatar - API for fetching Exchange & Gravatar avatars
========================================================
[![Requirements](https://requires.io/github/City-of-Helsinki/helavatar/requirements.svg?branch=master)](https://requires.io/github/City-of-Helsinki/helavatar/requirements/?branch=master)


Helavatar is a service and API returning avatar images based on e-mail
address. Its initial purpose was to provide mugshots for galleries such as
the one on digi.hel.fi.

Helavatar requires access credentials to an instance of Exchange EWS. In
addition to Exchange, helavatar also looks at Gravatar for images. If no
image is found, Gravatar is used to generate a placeholder.

Using the API
-------------
The API is dead simple. Just fetch an avatar using an email-address:
```
http://$YOUR_SERVER/$EMAIL_ADDRESS?s=$AVATAR_SIZE
```
or [Gravatar hash](https://fi.gravatar.com/site/implement/hash/)
```
http://$YOUR_SERVER/$GRAVATAR_HASH?s=$AVATAR_SIZE
```
example:
```
https://api.hel.fi/avatar/67d8070f51677c5e43033edee846fd24?s=240
```

$AVATAR_SIZE is the width & heigth of the wanted image, they are always
square. Helavatar will scale the image for you. Results depend on the
source image.

About the project
-----------------
Helavatar is (as of 22.09.2017) maintained by Open Software Group at City of
Helsinki. See https://dev.hel.fi/ for current contact information.

Helavatar is maintained on best effort basis, depending if any budgeted
projects need avatar services.

Installation
------------

These instructions assume an $INSTALL_BASE, like so:
```bash
INSTALL_BASE=$HOME/helavatar
```
If you've already cloned this repository, just move repository root into
$INSTALL_BASE. Otherwise just clone the repository, like so:
```bash
git clone https://github.com/City-of-Helsinki/helavatar.git $INSTALL_BASE
```
Prepare Python 3.x virtualenv using your favorite tools and activate it. Plain virtualenv is like so:
```bash
virtualenv -p python3 $HOME/venv
source $HOME/venv/bin/activate
```
Install required Python packages into the virtualenv
```bash
cd $INSTALL_BASE
pip install -r requirements.txt
```
Create the database, like so: (we run PostGRESQL usually)
```bash
cd $INSTALL_BASE/helavatar
sudo -u postgres createuser -R -S helavatar
# Following is for US locale, helavatar should not behave differently
# depending on locale
#sudo -u postgres createdb -Ohelavatar helavatar
# This is is for Finnish locale
sudo -u postgres createdb -Ohelavatar -Ttemplate0 -lfi_FI.UTF-8 helavatar
# This fills the database with a basic skeleton
python manage.py migrate
```
Configure the location of your Exchange EWS and user credentials for access
in local_settings.py:
```
EXCHANGE_USERNAME = 'DOMAIN\\USER'
EXCHANGE_PASSWORD = 'password'
EXCHANGE_URL = 'https://your.domain/ews'
```

For cleanliness we recommend moving Django media directory out from the
source tree (again in local_settings.py):
```
MEDIA_ROOT = '$HOME/media'
MEDIA_URL = '/media/'
```
Replace $HOME with the actual path

Afterwards you can run the Django development server for testing:
```
python manage.py runserver
```
Connect using the address shown on your terminal


Running in production
---------------------
Development installation above will give you quite a serviceable production
installation for lightish usage. You can serve out the application using your
favorite WSGI-capable application server. The WSGI-entrypoint for Helavatar
is ```helavatar.wsgi``` or in file ```helavatar/wsgi.py```. Former is
used by gunicorn, latter by uwsgi. The callable is ```application``` as per
WSGI standard.
