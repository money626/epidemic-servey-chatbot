import os
import firebase_admin
import matplotlib.pyplot as plt
from errors import (
    NoSuchUserError,
    UserNotBindedError,
)
from constants import (
    BIND_LIST,
    DATABASE_URL,
    USER_LIST,
    ADMIN_LIST,
    OVERLAP,
    NAME,
)
from typing import Union
from firebase_admin import (
    credentials,
    db,
)

cred = credentials.Certificate(
    os.path.join(os.path.dirname(__file__), "Credentials.json")
)
firebase_admin.initialize_app(cred, {
    'databaseURL': DATABASE_URL,
})


class CloudFirebase(object):
    def __init__(self):
        self.root = db.reference('/')

    def init_db(self) -> None:
        self.root.set({})

    def set_admin_list(self, admin_id_list: list) -> None:
        admin_list = self.root.child(ADMIN_LIST)
        # adminList.set({})
        for admin in admin_id_list:
            admin_list.push(admin)

    def get_admin_list(self) -> dict:
        return self.root.child(ADMIN_LIST).get() or {}

    def add_admin(self, uuid: str) -> None:
        if self.find_admin(uuid) is not None:
            return
        self.root.child(ADMIN_LIST).push(uuid)

    def find_admin(self, uuid: str) -> Union[str, None]:
        for k, v in self.get_admin_list().items():
            if v == uuid:
                return k
        return None

    def is_admin(self, uuid: str) -> bool:
        return self.find_admin(uuid) is not None

    def get_user_dict(self) -> dict:
        return self.root.child(USER_LIST).get() or {}

    def get_user_name_list(self) -> list:
        return list(map(
            lambda x: x[NAME],
            self.get_user_dict().values()
        ))

    def add_user(self, name: str) -> None:
        if self.find_user(name) is not None:
            return
        self.root.child(USER_LIST).push({
            NAME: name,
        })

    def remove_user(self, name: str) -> None:
        user_key = self.find_user(name)
        if user_key is None:
            raise NoSuchUserError(f"Can't find user {name} in database")
        else:
            bind_list = self.root.child(BIND_LIST).get() or {}
            for k, v in bind_list.items():
                if v == user_key:
                    self.root.child(BIND_LIST).child(k).delete()
            self.root.child(USER_LIST).child(user_key).delete()

    def get_bound_key(self, uuid: str) -> str:
        user_key = self.root.child(BIND_LIST).child(uuid).get() or ""
        if user_key is None:
            raise UserNotBindedError
        return user_key

    def is_bound(self, uuid: str) -> bool:
        return self.root.child(BIND_LIST).child(uuid).get() is not None

    def bind_user(self, uuid: str, name: str) -> None:
        user_key = self.find_user(name)
        if user_key is None:
            raise NoSuchUserError(f"Can't find user {name} in database")
        self.root.child(BIND_LIST).child(uuid).set(user_key)

    def get_name_by_key(self, key: str) -> str:
        data = self.root.child(USER_LIST).child(key).get() or {}
        if data is None:
            raise NoSuchUserError(
                f"Can't find user with key: {key} in database"
            )
        return data.get(NAME)

    def add_reply(self, name: str, has_overlap: bool) -> None:
        user_key = self.find_user(name)
        if user_key is None:
            raise NoSuchUserError(f"Can't find user {name} in database")
        self.root \
            .child(USER_LIST) \
            .child(user_key) \
            .child(OVERLAP) \
            .set(has_overlap)

    def add_reply_by_key(self, key: str, has_overlap: bool) -> None:
        if self.root.child(USER_LIST).child(key).get() is None:
            raise NoSuchUserError(
                f"Can't find user with key: {key} in database"
            )
        self.root \
            .child(USER_LIST) \
            .child(key) \
            .child(OVERLAP) \
            .set(has_overlap)

    def clear_reply(self, name: str) -> None:
        pass

    def clear_replies(self) -> None:
        user_keys = self.get_user_dict().keys()
        for userKey in user_keys:
            self.root.child(USER_LIST).child(userKey).child(OVERLAP).delete()

    def find_user(self, name: str) -> Union[str, None]:
        for k, v in self.get_user_dict().items():
            if v[NAME] == name:
                return k
        return None

    def generate_pie_chart(self):
        data = self.get_user_dict().values()
        for i in data:
            print(i.get(OVERLAP))
        overlap_count = len([1 for i in data if i.get(OVERLAP) is True])
        no_overlap_count = len([1 for i in data if i.get(OVERLAP) is False])
        not_replied = len([i[NAME] for i in data if i.get(OVERLAP) is None])
        labels = ['overlap', 'noOverlap', 'notReplied']
        values = [overlap_count, no_overlap_count, not_replied]
        print(values)
        plt.pie(values, labels=labels, autopct="%1.1f%%")
        plt.savefig(
            os.path.join(os.path.dirname(__file__), 'static/statistic.png')
        )


if __name__ == '__main__':
    firebase_db = CloudFirebase()
    print(firebase_db.get_admin_list())
    firebase_db.set_admin_list(['Ue8a7d06ff58042bb80291c135e94ccdf'])
    print(firebase_db.get_admin_list())
