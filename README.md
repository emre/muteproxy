<center><img src="https://cdn.steemitimages.com/DQmd1xzRmz9zMzvrK65TPG4Tpx4b1i9X9PNKstsCDLSYrZK/Screen%20Shot%202018-10-04%20at%201.02.53%20PM.png"></center>

mutingproxy is a simple STEEM based app where you can subscribe the trusted
accounts' mute lists and follow their future mutings.

#### installation

```
$ python3 -m venv muting-proxy-env
$ tmp source muting-proxy-env/bin/activate
$ git clone https://github.com/emre/muteproxy.git
$ cd muteproxy
$ pip install -r requirements.txt
$ touch base/settings.py base/local_settings.py
$ python manage.py migrate
```

If you want to use the admin:

```
$ python manage.py createsuperuser
```

local_settings.py example:

```
SC_CLIENT_ID = "your.app"
SC_CLIENT_SECRET = "your_app_secret"
SC_REDIRECT_URI = "http://localhost:8000/login/"
```

#### Running

```
$ python manage.py runserver
```

#### Credits

[Freelancer](https://startbootstrap.com/template-overviews/freelancer/) template
is in use for the frontend.