from requests import Session


class TorqueSession(Session):
    def __init__(self):
        """Creates new Torque Session"""
        super(TorqueSession, self).__init__()

        self.headers.update({"Accept": "application/json", "Accept-Charset": "utf-8"})

    def init_bearer_auth(self, token: str) -> None:
        """

        :rtype: object
        """
        self.headers.update({"Authorization": "Bearer {}".format(token)})
