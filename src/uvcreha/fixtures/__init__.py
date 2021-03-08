import omegaconf


CONFIG = omegaconf.OmegaConf.create('''
app:

  factories:
    user: ${class:uvcreha.models.User}
    request: ${class:uvcreha.request.Request}

  env:
    session: uvcreha.test.session
    user: test.principal

  session:
    cookie_name: uvcreha.cookie
    cookie_secret: secret

  logger:
    name: uvcreha.test.logger

  assets:
    compile: True
    recompute_hashes: True
    bottom: True
''')
