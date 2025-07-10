from datetime import date, timedelta

from django.test import TestCase

from vehicles.models import Vehicle

from .models import ACTION_DONE, ACTION_INLOT, History
from .services import check_in, check_out


class CheckInOutServiceTests(TestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            user_name="Alice",
            unit="A1",
            model="Honda",
            license_plate="30A12345",
            phone_number="0900000000",
            issued_date=date.today() - timedelta(days=10),
            expired_date=date.today() + timedelta(days=365),
        )

    def test_check_in_creates_inlot_linked_to_vehicle(self):
        history = check_in("30A12345", "registered")
        self.assertEqual(history.action_type, ACTION_INLOT)
        self.assertIsNotNone(history.entry_time)
        self.assertIsNone(history.exit_time)
        self.assertEqual(history.vehicle, self.vehicle)

    def test_check_out_closes_open_inlot(self):
        check_in("30A12345", "registered")
        closed = check_out("30A12345")
        self.assertIsNotNone(closed)
        self.assertEqual(closed.action_type, ACTION_DONE)
        self.assertIsNotNone(closed.exit_time)

    def test_check_out_without_open_record_returns_none(self):
        self.assertIsNone(check_out("99Z99999"))

    def test_check_in_unknown_plate_has_no_vehicle(self):
        history = check_in("99Z99999", "unregistered")
        self.assertIsNone(history.vehicle)
        self.assertEqual(History.objects.count(), 1)
