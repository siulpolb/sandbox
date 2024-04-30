# Summary 
This is a sample Django application that has some failing tests.  It's built off the example project in
[Writing your first Django app](https://docs.djangoproject.com/en/dev/intro/tutorial01/).

As a programming exercise do the following:
* Create a fork of this repo.
* Make a pull request that fixes the broken tests.

## Instructions for Running
* Create a new virtual environment

      python -m venv sandbox-env
* Switch to the new environment
  
      source sandbox-env/bin/activate 
* Install requirements

      pip install --requirement=requirements.txt
* Run tests

      python manage.py test
* Run the site (user is `admin` and password is `asdfASDF1234`)

      python manage.py runserver 
