import faker
from django.db import migrations
from django.utils import timezone


def make_test_data(apps, schema_editor):
    fake = faker.Faker()

    Question = apps.get_model("polls", "Question")
    Choice = apps.get_model("polls", "Choice")

    for __ in range(fake.pyint()):
        pub_date = timezone.make_aware(fake.date_time_this_year())
        question = Question.objects.create(question_text=fake.catch_phrase(), pub_date=pub_date)

        for ___ in range(fake.random_digit()):
            choice = Choice.objects.create(question=question, choice_text=fake.bs(), votes=fake.pyint())


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(make_test_data)
    ]
