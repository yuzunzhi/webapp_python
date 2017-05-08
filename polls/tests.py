# Create your tests here.
from django.test import TestCase
import datetime
from django.utils import timezone
from .models import Question, Choice
from django.core.urlresolvers import reverse


class QuestionMethodTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=1)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), True)


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question, choice_text):
    return Choice.objects.create(question=question, choice_text=choice_text)


class QuestionViewTests(TestCase):
    def test_index_view_with_no_question(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_past_question(self):
        q_past = create_question(question_text="Past question", days=-30)
        create_choice(question=q_past, choice_text="Past question's choice")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ["<Question: Past question>"])

    def test_index_view_with_future_question(self):
        q_future = create_question(question_text="Future question", days=30)
        create_choice(question=q_future, choice_text="Future question's choice")
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.", status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_past_question_and_future_question(self):
        q_past = create_question(question_text="Past question", days=-30)
        q_future = create_question(question_text="Future question", days=30)
        create_choice(question=q_past, choice_text="Past question's choice")
        create_choice(question=q_future, choice_text="Future question's choice")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ["<Question: Past question>"])

    def test_index_view_with_two_past_question(self):
        q_past = create_question(question_text="Past question.1", days=-30)
        q_future = create_question(question_text="Past question.2", days=-5)
        create_choice(question=q_past, choice_text="Past question's choice")
        create_choice(question=q_future, choice_text="Future question's choice")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ["<Question: Past question.1>", "<Question: Past question.2>"]
        )

    def test_index_view_with_choice_is_null(self):
        create_question(question_text="question.1", days =-1)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.", status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_choice_is_not_null(self):
        q = create_question(question_text="question.1", days=-1)
        create_choice(question=q,choice_text="choice.1")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ["<Question: question.1>"])

class DetailViewTest(TestCase):
    def test_detail_view_with_past_question(self):
        past_question = create_question(question_text="Past question.", days=-30)
        create_choice(question=past_question, choice_text="Past question's choice")
        response = self.client.get(reverse('polls:detail', args=(past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code=200)

    def test_detail_view_with_future_question(self):
        future_question = create_question(question_text="Past question.", days=5)
        create_choice(question=future_question, choice_text="Future question's choice")
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)
