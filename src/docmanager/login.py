import collections
import wtforms.form
import wtforms.fields
import wtforms.validators
from pathlib import Path
from chameleon import PageTemplateLoader

import horseman.response
import roughrider.auth.meta
from horseman.prototyping import Environ
from horseman.meta import APIView, SentryNode
from horseman.parsing import parse

from docmanager.request import Request
from docmanager.layout import template_endpoint
from docmanager.app import ROUTER


TEMPLATES = PageTemplateLoader(
    str((Path(__file__).parent / 'templates').resolve()), ".pt")


class LoginForm(wtforms.form.Form):

    username = wtforms.fields.StringField(
        'Username',
        validators=(wtforms.validators.InputRequired(),)
    )

    password = wtforms.fields.PasswordField(
        'Password',
        validators=(wtforms.validators.InputRequired(),)
    )


@ROUTER.register('/login')
class LoginView(APIView):

    @template_endpoint(TEMPLATES['login.pt'], raw=False)
    def GET(self, request: Request):
        form = LoginForm()
        return {'form': form, 'error': None, 'path': request.route.path}

    @template_endpoint(TEMPLATES['login.pt'], raw=False)
    def POST(self, request: Request):
        form = LoginForm(request.data['form'])
        if not form.validate():
            return {'form': form, 'error': 'form'}
        if (user := request.app['auth'].from_credentials(
                request.environ, request.data['form'].to_dict())) is not None:
            request.app['auth'].remember(request.environ, user)
            print('The login was successful')
            return horseman.response.Response.create(
                302, headers={'Location': '/'})
        return {'form': form, 'error': 'auth', 'path': request.route.path}


@ROUTER.register('/logout')
def LogoutView(request, environ):
    request.session.store.clear(request.session.sid)
    return horseman.response.Response.create(
            302, headers={'Location': '/'})
