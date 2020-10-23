class SecurityError(Exception):

    def __init__(self, permission, principal):
        self.permission = permission
        self.principal = principal
