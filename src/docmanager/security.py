class SecurityError(Exception):

    def __init__(self, principal, *permissions):
        self.permissions = permissions
        self.principal = principal
