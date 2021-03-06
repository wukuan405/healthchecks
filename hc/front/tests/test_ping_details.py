from hc.api.models import Check, Ping
from hc.test import BaseTestCase


class LastPingTestCase(BaseTestCase):

    def test_it_works(self):
        check = Check(user=self.alice)
        check.save()

        Ping.objects.create(owner=check, body="this is body")

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/checks/%s/last_ping/" % check.code)
        self.assertContains(r, "this is body", status_code=200)

    def test_it_shows_fail(self):
        check = Check(user=self.alice)
        check.save()

        Ping.objects.create(owner=check, fail=True)

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/checks/%s/last_ping/" % check.code)
        self.assertContains(r, "/fail", status_code=200)

    def test_it_shows_start(self):
        check = Check(user=self.alice)
        check.save()

        Ping.objects.create(owner=check, start=True)

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/checks/%s/last_ping/" % check.code)
        self.assertContains(r, "/start", status_code=200)

    def test_it_requires_user(self):
        check = Check.objects.create()
        r = self.client.get("/checks/%s/last_ping/" % check.code)
        self.assertEqual(r.status_code, 404)

    def test_it_accepts_n(self):
        check = Check(user=self.alice)
        check.save()

        # remote_addr, scheme, method, ua, body:
        check.ping("1.2.3.4", "http", "post", "tester", "foo-123", "success")
        check.ping("1.2.3.4", "http", "post", "tester", "bar-456", "success")

        self.client.login(username="alice@example.org", password="password")

        r = self.client.get("/checks/%s/pings/1/" % check.code)
        self.assertContains(r, "foo-123", status_code=200)

        r = self.client.get("/checks/%s/pings/2/" % check.code)
        self.assertContains(r, "bar-456", status_code=200)

    def test_it_allows_cross_team_access(self):
        self.bobs_profile.current_team = None
        self.bobs_profile.save()

        check = Check(user=self.alice)
        check.save()

        Ping.objects.create(owner=check, body="this is body")

        self.client.login(username="bob@example.org", password="password")
        r = self.client.get("/checks/%s/last_ping/" % check.code)
        self.assertEqual(r.status_code, 200)
