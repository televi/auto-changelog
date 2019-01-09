"""
The basic data structures used in the project.
"""

import datetime
import re
from collections import defaultdict


class Tag:
    def __init__(self, name, date, commit):
        self.name = 'Version ' + name if not name.lower().startswith('v') else name
        self._commit = commit
        self.date = datetime.datetime.fromtimestamp(date)
        self.commits = []
        self.groups = defaultdict(list)
        
    def add_commit(self, commit):
        self.commits.append(commit)
        commit.tag = self
        self.groups[commit.category].append(commit)
        
    def __repr__(self):
        return '<{}: {!r}>'.format(
                self.__class__.__name__,
                self.name)
    

class Unreleased:
    def __init__(self, commits):
        self.name = 'Unreleased'
        self.groups = defaultdict(list)
        self.commits = commits
        
        for commit in commits:
            self.add_commit(commit)
            
    def add_commit(self, commit):
        self.groups[commit.category].append(commit)

    def __repr__(self):
        return '<{}: {!r}>'.format(
                self.__class__.__name__,
                self.name)
        

class Commit:
    def __init__(self, commit):
        self._commit = commit
        self.date = datetime.datetime.fromtimestamp(commit.committed_date)
        self.commit_hash = commit.hexsha
        self.message = commit.message

        self.whole_message = self.message.splitlines()
        self.whole_message_length = len(self.whole_message)
        self.first_line = self.whole_message[0].strip()  # the subject
        self.body = ""
        self.footer = ""

        # If we have > 1 line, then we have either a body, body and footer, or footer.
        # The first line after the subject is blank so skip it.
        # The next line up until the next blank or end of the message is the body.
        # If there's anything after that, it becomes footer.
        # If we have 2 blank lines, then we have no boddy but do have a footer.
        #
        if len(self.whole_message) > 1:
            line = 2
            while line < self.whole_message_length and len(self.whole_message[line]) > 0:
                self.body += self.whole_message[line].strip()
                line += 1
            if line + 1 < self.whole_message_length:
                self.footer += self.whole_message[line + 1]
        self.tag = None
        
        self.category, self.specific, self.description = self.categorize()
        
    def categorize(self):
        match = re.match(r'(\w+)(\(\w+\))?:\s*(.*)', self.first_line)
        
        if match:
            category, specific, description = match.groups()
            specific = specific[1:-1] if specific else None  # Remove surrounding brackets
            return category, specific, description
        else:
            return None, None, None

    def __repr__(self):
        return '<{}: {} "{}">'.format(
                self.__class__.__name__,
                self.commit_hash[:7],
                self.date.strftime('%x %X'))
