import unittest
from unittest import skip

from django.db import connection
from django.test.testcases import TransactionTestCase
from django.test.utils import override_settings

from wagtail.search.query import Not, PlainText
from wagtail.search.tests.test_backends import BackendTests
from wagtail.test.search import models


@unittest.skipUnless(connection.vendor == "mysql", "The current database is not MySQL")
@override_settings(
    WAGTAILSEARCH_BACKENDS={
        "default": {
            "BACKEND": "wagtail.search.backends.database.mysql.mysql",
        }
    }
)
class TestMySQLSearchBackend(BackendTests, TransactionTestCase):
    backend_path = "wagtail.search.backends.database.mysql.mysql"

    # Overrides parent method, because there's a slight difference in what the MySQL backend supports/accepts as search queries.
    def test_not(self):
        all_other_titles = {
            "A Clash of Kings",
            "A Game of Thrones",
            "A Storm of Swords",
            "Foundation",
            "Learning Python",
            "The Hobbit",
            "The Two Towers",
            "The Fellowship of the Ring",
            "The Return of the King",
            "The Rust Programming Language",
            "Two Scoops of Django 1.11",
            "Programming Rust",
        }

        results = self.backend.search(
            Not(PlainText("javascript")), models.Book.objects.all()
        )
        self.assertSetEqual({r.title for r in results}, all_other_titles)

        results = self.backend.search(
            ~PlainText("javascript"), models.Book.objects.all()
        )
        self.assertSetEqual({r.title for r in results}, all_other_titles)

        # Tests multiple words
        results = self.backend.search(
            ~PlainText("javascript the"), models.Book.objects.all()
        )
        # NOTE: The difference with the parent method is here. As we're querying NOT 'javascript the', all entries containing both words should be excluded, but MySQL doesn't index stopwords in FULLTEXT indexes by default, so the JavaScript books won't match the query, since the 'the' word is excluded from the index. Therefore, both books will get returned.
        self.assertSetEqual(
            {r.title for r in results},
            all_other_titles
            | {"JavaScript: The Definitive Guide", "JavaScript: The good parts"},
        )

        # Tests multiple words too, but this time the second word is not a stopword
        results = self.backend.search(
            ~PlainText("javascript parts"), models.Book.objects.all()
        )
        self.assertSetEqual(
            {r.title for r in results},
            all_other_titles | {"JavaScript: The Definitive Guide"},
        )

    def test_empty_search(self):
        results = self.backend.search("", models.Book.objects.all())
        self.assertSetEqual(
            {r.title for r in results},
            set(),
        )

        results = self.backend.search(" ", models.Book.objects.all())
        self.assertSetEqual(
            {r.title for r in results},
            set(),
        )

        results = self.backend.search("*", models.Book.objects.all())
        self.assertSetEqual(
            {r.title for r in results},
            set(),
        )

    def test_empty_autocomplete(self):
        results = self.backend.autocomplete("", models.Book.objects.all())
        self.assertSetEqual(
            {r.title for r in results},
            set(),
        )

        results = self.backend.autocomplete(" ", models.Book.objects.all())
        self.assertSetEqual(
            {r.title for r in results},
            set(),
        )

        results = self.backend.autocomplete("*", models.Book.objects.all())
        self.assertSetEqual(
            {r.title for r in results},
            set(),
        )

    def test_symbols_in_search_term(self):
        # symbols as their own tokens should be ignored
        results = self.backend.search("javascript @ parts", models.Book.objects.all())
        self.assertSetEqual(
            {r.title for r in results},
            {"JavaScript: The good parts"},
        )

        results = self.backend.search("javascript parts @", models.Book.objects.all())
        self.assertSetEqual(
            {r.title for r in results},
            {"JavaScript: The good parts"},
        )

        results = self.backend.search("@ javascript parts", models.Book.objects.all())
        self.assertSetEqual(
            {r.title for r in results},
            {"JavaScript: The good parts"},
        )

        # tokens containing both symbols and alphanumerics should not be discarded
        # or treated as equivalent to the same token without symbols
        results = self.backend.search("java@script parts", models.Book.objects.all())
        self.assertSetEqual(
            {r.title for r in results},
            set(),
        )

    def test_autocomplete_with_symbols(self):
        # the * is not part of the autocomplete mechanism, but if someone includes it
        # we want it to be gracefully ignored
        results = self.backend.autocomplete("parts javasc*", models.Book.objects.all())
        self.assertSetEqual(
            {r.title for r in results},
            {"JavaScript: The good parts"},
        )

    def test_lexeme_validation(self):
        from wagtail.search.backends.database.mysql.query import Lexeme

        with self.assertRaisesMessage(ValueError, "Lexeme value cannot be empty."):
            Lexeme("")

        Lexeme("hello")  # no error

        with self.assertRaisesMessage(
            ValueError,
            "Lexeme value 'hello world' must consist of alphanumeric characters "
            "and '_' only.",
        ):
            Lexeme("hello world")

        with self.assertRaisesMessage(
            ValueError,
            "Lexeme value 'rimsky@korsakov' must consist of alphanumeric characters "
            "and '_' only.",
        ):
            Lexeme("rimsky@korsakov")

    @skip(
        "The MySQL backend doesn't support choosing individual fields for the search, only (body, title) or (autocomplete) fields may be searched."
    )
    def test_search_on_individual_field(self):
        return super().test_search_on_individual_field()

    @skip("The MySQL backend doesn't support boosting.")
    def test_search_boosting_on_related_fields(self):
        return super().test_search_boosting_on_related_fields()

    @skip("The MySQL backend doesn't support boosting.")
    def test_boost(self):
        return super().test_boost()

    @skip("The MySQL backend doesn't score annotations.")
    def test_annotate_score(self):
        return super().test_annotate_score()

    @skip("The MySQL backend doesn't score annotations.")
    def test_annotate_score_with_slice(self):
        return super().test_annotate_score_with_slice()

    @skip("The MySQL backend doesn't guarantee correct ranking of results.")
    def test_ranking(self):
        return super().test_ranking()
