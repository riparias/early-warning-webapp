# LIFE RIPARIAS early alert web application

<!-- badges: start -->
[![Django CI](https://github.com/riparias/early-warning-webapp/actions/workflows/django_tests.yml/badge.svg)](https://github.com/riparias/early-warning-webapp/actions/workflows/django_tests.yml)
[![Funding](https://img.shields.io/static/v1?label=powered+by&message=LIFE+RIPARIAS&labelColor=323232&color=00a58d)](https://www.riparias.be/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Deployment on dev server](https://github.com/riparias/early-warning-webapp/actions/workflows/deploy_dev_server.yml/badge.svg)](https://github.com/riparias/early-warning-webapp/actions/workflows/deploy_dev_server.yml)
<!-- badges: end -->

This repository contains the source code of the early warning web application for [LIFE RIPARIAS](https://www.riparias.be/) (Action A.1.2).

Development version visible on [dev-alert.riparias.be](http://dev-alert.riparias.be/).

## Development setup and notes

### Backbone
- [Python](https://www.python.org/) 3.8, [(Geo)Django](https://www.djangoproject.com/) 3.2 LTS, [PostgreSQL](https://www.postgresql.org/), [PostGIS](https://postgis.net/) 3.1+, [TypeScript](https://www.typescriptlang.org/) and [Vue.js v3](https://vuejs.org/)
- CSS: [Bootstrap](https://getbootstrap.com/) 5.1  
- [Poetry](https://python-poetry.org/) to manage dependencies (use `poetry add`, `poetry install`, ... instead of pip). PyCharm also has a Poetry plugin available.

### Dev environment
- Python>=3.8, PostGIS>=3.1 and npm are required
- copy `local_settings.template.py` to `local_settings.py`, adjust those settings and point Django to `local_settings.py`
- point Django to `local_settings`

### Testing / typing
This project provides tools to ensure the application and code stays in a decent state:

- Standard Django tests (can be run with `$ ./manage.py test`), including Selenium-based testing for frontend feautres and high-level tests
- Typing: can be checked with `$ mypy .`

### CI-CD

We make use of GitHub Actions when possible.

They're currently used to:
- Run Django tests and `mypy` on push
- Deploy to dev server on push

### Dependencies

We try to frequently update dependencies. Process is:

- Backend: `$ poetry update`
- Frontend: `$ npm-check -u`
- Run unit tests (+ a few manual checks?)
- Commit changes (should include `package.json`, `package-lock.json` and `poetry lock` 

### Frontend-backend integration

We use a hybrid approach such as described in https://www.saaspegasus.com/guides/modern-javascript-for-django-developers/integrating-javascript-pipeline/:

- npm is used to manage JS dependencies (**npm install** should be run)
- Run `npm-check -u` frequently to update frontend dependencies  
- **During development**, run `npm run webpack-dev` so Webpack constantly watches our source frontend (in `./assets`) and create bundles (in `./static`)
- **When deploying**, use `npm run webpack prod` instead (smaller bundle size + one single copy - rather than watching files)

### Code formatting

We use `black` (for Python code) and `prettier` (for JS/TS/Vue) to automatically and consistently format the source code.
Contributors: please configure your favorite editor/IDE to format on save. 

### Data import mechanism

The data shown in the webapp can be automatically updated by running the `import_occurrences` management command. 
This one will trigger a GBIF Download for our search of interest (target country + species in the database) and 
load the corresponding occurrences into the database. At the end of the process, occurrences from previous data 
imports are deleted.

The data import history is recorded with the DataImport model, and shown to the user on the "about" page.

=> For a given occurrence, Django-managed IDs are therefore not stable, but the GBIF ids fortunately are.

### Users

The web application handle three categories of users:

- Anonymous users can access the website and visualize the occurrence data via the dashboard. For Django, they are 
  unauthenticated.
- Registered "normal" users can do all what can anonymous users can do + create and configure their alerts. Those users can 
  sign up directly thanks to a specific form (an e-mail address is required because it is needed for e-mail 
  notifications). For Django, they are regular users without any specific group or permission (**not** 
  staff, **not** superuser)
- Admins can do all that registered users can do + access the admin interface to configure the web application. For 
  Django they have the **staff** and **superuser** flags set. Admins can be created by different means, for example 
  being upgraded to this status by an existing Admin after registering as a normal user, or via Django's 
  `createsuperuser` management command.
  