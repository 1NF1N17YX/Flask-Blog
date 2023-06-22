# Flask-Blog

# Environment
pip install -r requirements.txt
## OR
./build.sh

# Run the server
flask run

# Screenshots

![blog](https://github.com/1NF1N17YX/Flask-Blog/assets/131818684/dcdea76f-7bd4-4024-a382-0429dde46957)

![dashboard](https://github.com/1NF1N17YX/Flask-Blog/assets/131818684/4353aa00-a13f-4989-ae54-b2bc4aa973b2)

# setting up version control

```bash
$ git config --global user.name "Your Name"
$ git config --global user.email "you@youraddress.com"
$ git config --global push.default matching
$ git config --global alias.co checkout
$ git init
```

# Flask migration

`pip install Flask-Migrate`

## It's creating a directory to hold all migration files
`flask --app app db init`

# Make initial migration
`flask --app app db migrate -m 'Initial Migration'`

# Push the migration to the database
`flask --app app db upgrade`

# WTF Resources:
URLs <br />
https://flask-wtf.readthedocs.io/en/1.0.x/ <br />
https://wtforms.readthedocs.io/en/3.0.x/
