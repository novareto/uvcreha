class SecurityError(Exception):

    def __init__(self, user, *permissions):
        self.permissions = permissions
        self.user = user
