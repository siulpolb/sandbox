import logging

import faker
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from polls.models import Question, Choice
from tests import BaseTestCase, HttpMethod

fake = faker.Faker()

logger = logging.getLogger(__name__)


class QuestionTests(BaseTestCase):
    """
    Given the following failing tests, do what is required externally to this module to make them pass.

    i.e. There should be no changes to this file.  Instead, find the areas in the application to augment
    and fix the failing tests.
    """
    __test__ = True

    def create_question(self):
        pub_date = timezone.make_aware(fake.date_time_this_year())
        question = Question.objects.create(question_text=fake.catch_phrase(), pub_date=pub_date)
        for __ in range(fake.random_digit()):
            Choice.objects.create(question=question, choice_text=fake.bs(), votes=fake.pyint())
        return question

    def test_multi_update(self):
        """
        Augment the endpoint to handle updating multiple objects within a single request.
        """
        # Create some test objects
        expected_count = 10
        self.assertFalse(Question.objects.exists())

        for __ in range(expected_count):
            self.create_question()

        self.assertEqual(Question.objects.count(), expected_count)

        url = reverse("question-list")
        self.authenticate()

        # Build a payload for the request.  In this case we're sending a non-standard payload
        # that includes multiple objects to update.
        payload = []
        for obj in Question.objects.all():
            payload.append(dict(url=reverse("question-detail", kwargs=dict(pk=obj.pk)),
                                question_text=fake.bs()))

        # Send the request - we're doing a partial update in this case (i.e. PATCH vs a PUT)
        response, data = self.request(HttpMethod.PATCH, url, data=payload, authenticated=True)
        self.assertResponseStatus(response, status_code=status.HTTP_200_OK)
        self.assertEqual(len(data["results"]), expected_count)

    def test_has_date_created(self):
        """
        Augment the model to have a `date_created` field.

        This field should be automatically be set with a datetime value representing the point in time
        that the instance was created.  Make sure to create a migration file as well.  (python manage.py makemigrations)

        Furthermore, augment the serializer to include the new field.
        """
        obj = self.create_question()
        url = reverse("question-detail", kwargs=dict(pk=obj.pk))
        response, data = self.request(HttpMethod.GET, url, authenticated=True)
        self.assertResponseStatus(response, status_code=status.HTTP_200_OK)
        self.assertIn("pub_date", data)
        self.assertIn("url", data)
        self.assertIn("question_text", data)
        self.assertIn("choices", data)
        self.assertIn("date_created", data, msg="date_created isn't in the serialized data yet")
        self.assertIsNotNone(data["date_created"])

    def test_query_count_is_off(self):
        """
        Something is causing a higher than expected number of queries executed during a list request.

        Find and fix the area of the application that would be responsible for this.
        """
        # Create a bunch of test objects
        for __ in range(fake.pyint()):
            self.create_question()

        url = reverse("question-list")
        self.authenticate()

        # We only expect 11 queries to execute in total if this request was optimized
        with self.assertNumQueries(11):
            response, data = self.request(HttpMethod.GET, url, authenticated=True)
            self.assertResponseStatus(response, status_code=status.HTTP_200_OK)
            self.assertGreaterEqual(len(data["results"]), 1)
            obj = data["results"][0]
            self.assertIn("pub_date", obj)
            self.assertIn("url", obj)
            self.assertIn("question_text", obj)
            self.assertIn("choices", obj)
