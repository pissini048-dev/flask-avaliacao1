# flask-avaliacao1

The basic blog app built in the Flask [tutorial](https://flask.palletsprojects.com/tutorial/).

## Install

Be sure to use the same version of the code as the version of the docs you're reading. You probably want the latest tagged version, but the default Git version is the main branch.

```bash
# clone the repository
$ git clone https://github.com/pissini048-dev/flask-avaliacao1
$ cd flask-avaliacao1
```

Create a virtualenv and activate it:

```bash
$ python3 -m venv .venv
$ . .venv/bin/activate
```

Or on Windows cmd:

```bash
$ py -3 -m venv .venv
$ .venv\Scripts\activate.bat
```

Install the dependencies:

```bash
$ pip install -e .
```

## Run

```bash
$ flask --app flaskr init-db
$ flask --app flaskr run --debug
```

Open http://127.0.0.1:5000 in a browser.

## Test

```bash
$ pip install '.[test]'
$ pytest
```

Run with coverage report:

```bash
$ coverage run -m pytest
$ coverage report
$ coverage html  # open htmlcov/index.html in a browser
```
