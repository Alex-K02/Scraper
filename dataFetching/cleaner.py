# -*- coding: utf-8 -*-
# used from news_please python library https://pypi.org/project/news-please/
import re
import sys

from lxml import html

# to improve performance, regex statements are compiled only once per module
re_newline_spc = re.compile(r'(?<=\n)( )+') # Deletes whitespaces after a newline
re_starting_whitespc = re.compile(r'^[ \t\n\r\f]*') # Deletes every whitespace, tabulator, newline at the beginning of the string
re_multi_spc_tab = re.compile(r'[ \t]+(?=([ \t]))') # Deletes whitespace or tabulator if followed by whitespace or tabulator
re_double_newline = re.compile(r'[ \n]+(?=(\n))') # Deletes newline if it is followed by an other one
re_ending_spc_newline = re.compile(r'[ \n]*$')  # Deletes newlines and whitespaces at the end of the string
# cleaning extension
re_curly_brck = re.compile(r'\{\}') # Remove curly braces {}
re_sqr_brcl = re.compile(r'\[\]') # Remove square braces []
re_rnd_brcl = re.compile(r'\(\)') # Remove curly braces ()
re_bck_slash = re.compile(r'\\') # Remove backslashes \
re_fwrd_slash = re.compile(r'\/') # Remove forward slashes /
re_quot_mark = re.compile(r'\"') # Remove forward slashes /
re_sngl_quot_mark = re.compile(r'\'') # Remove forward slashes /
re_comma = re.compile(r'\,') # Remove comma
re_equals = re.compile(r'\=') # Remove equals

regex_statments = [re_newline_spc, re_starting_whitespc, re_multi_spc_tab, re_double_newline, re_ending_spc_newline, re_curly_brck, re_sqr_brcl, re_rnd_brcl, re_bck_slash, re_fwrd_slash, re_quot_mark, re_sngl_quot_mark, re_comma, re_equals]


class Cleaner:
    """The Cleaner-Class tries to get the raw extracted text of the extractors
    in a comparable format. For this it deletes unnecessary whitespaces
    or in case of readability html-tags which are still in the extracted
    text.
    """

    def delete_tags(self, arg):
        """Removes html-tags from extracted data.

        :param arg: A string, the string which shall be cleaned
        :return: A string, the cleaned string
        """

        if len(arg) > 0:
            try:
                raw = html.fromstring(arg)
            except ValueError:
                raw = html.fromstring(arg.encode("utf-8"))
            return raw.text_content().strip()

        return arg

    def delete_whitespaces(self, arg):
        """Removes newlines, tabs and whitespaces at the beginning, the end and if there is more than one.

        :param arg: A string, the string which shell be cleaned
        :return: A string, the cleaned string
        """
        for regex_statment in regex_statments:
            arg = regex_statment.sub('', arg)
        return arg

    def do_cleaning(self, arg):
        """Does the actual cleaning by using the delete methods above.

        :param arg: A string, the string which shell be cleaned. Or a list, in which case each of the strings within the
        list is cleaned.
        :return: A string, the cleaned string. Or a list with cleaned string entries.
        """
        if arg is not None:
            if isinstance(arg, list):
                newlist = []
                for entry in arg:
                    newlist.append(self.do_cleaning(entry))
                return newlist
            else:
                if sys.version_info[0] < 3:
                    arg = unicode(arg)
                else:
                    arg = str(arg)
                arg = self.delete_tags(arg)
                arg = self.delete_whitespaces(arg)
                return arg
        else:
            return None

    def clean(self, list_article_source_codes):
        """Iterates over each article_candidate and cleans every extracted data.

        :param list_article_source_codes: A list, the list of websites source codes which have been extracted
        :return: A list, the list with the cleaned artilce source codes
        """
        # Save cleaned article_candidates in results.
        results = []

        for article_candidate in list_article_source_codes:
            article_candidate = self.do_cleaning(article_candidate)
            results.append(article_candidate)

        return results