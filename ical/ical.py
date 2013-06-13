#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 28.06.2011

@author: denex
'''

from __future__ import with_statement
from datetime import datetime, timedelta
from urllib2 import urlopen

GMT_OFFSET_HOURS = +7  # Asia/Novosibirsk


class iCalParseError(Exception):
    pass


class iEvent():

    def __init__(self):
        self._summary = None
        self.dtstart = None
        self.dtend = None

    def has_closed(self):
        return (self._summary is not None
                and self.dtstart is not None
                and self.dtend is not None)

    def __repr__(self):
        return "%s-%s: %s" % (self.dtstart, self.dtend, self._summary)

    def __str__(self):
        result = '%s;"%s";%s;%s;%s' % (self.dtstart.strftime('%d.%m.%Y'),
                                       self._summary,
                                       self.dtstart.strftime('%H:%M'),
                                       self.dtend.strftime('%H:%M'),
                                       self.getDurationStr())
        return result

    def as_row(self):
        return (self.dtstart.strftime('%d.%m.%Y'),
                self._summary,
                self.dtstart.strftime('%H:%M'),
                self.dtend.strftime('%H:%M'),
                self.getDurationStr())

    def setSummary(self, rawSummary):
        """
        Set summary for events
        """
        result = ''
        prevChar = ''
        for char in rawSummary:
            if char == '\\':
                if prevChar == '\\':
                    result += char
            else:
                result += char
            prevChar = char
        self._summary = result

    def getDateTimeFromStr(self, dateString):
        """
        @return: DateTime
        """
        timeOffset = 0
        formatStr = '%Y%m%dT%H%M%S'
        if dateString.startswith(';VALUE=DATE:'):
            formatStr = '%Y%m%d'
        datetimes = dateString.partition(':')[-1]
        if datetimes.endswith('Z'):
            datetimes = datetimes[:-2]
            timeOffset = GMT_OFFSET_HOURS
        date = datetime.strptime(datetimes, formatStr)
        if timeOffset != 0:
            date += timedelta(hours=timeOffset)
        return date

    def duration(self):
        """
        @return: Event duration as timedelta
        """
        return self.dtend - self.dtstart

    def getDurationStr(self):
        """
        @return: String value of time delta
        """
        seconds = getTotalSeconds(self.duration())
        hours = seconds // 3600
        mins = (seconds - hours * 3600) // 60
        return '%d:%02d' % (hours, mins)
# End of class iEvent


def getRawEventsFromUrl(url):
    return get_events_from_stream(urlopen(url, timeout=3))


def get_events_from_stream(string_stream):
    event = None
    eventList = []
    eventContext = []
    for raw_line in string_stream:
        line = raw_line
        line = line.replace('\r', '').replace('\n', '')
        eventContext.append(line)
        if line.startswith('BEGIN:VEVENT'):
            event = iEvent()
            eventContext = []
        elif line.startswith('SUMMARY:'):
            summary = line.partition('SUMMARY:')[-1]
            event.setSummary(summary)
        elif line.startswith('DTSTART'):
            if event is not None:
                event.dtstart = event.getDateTimeFromStr(
                    line.partition('DTSTART')[-1])
        elif line.startswith('DTEND'):
            event.dtend = event.getDateTimeFromStr(
                line.partition('DTEND')[-1])
        elif line.startswith('END:VEVENT'):
            if not event.has_closed():
                raise iCalParseError("Previous event has not closed")
            eventList.append(event)
    # sort list by dtstart
    return sorted(eventList, key=lambda ev: ev.dtstart)


def getTotalSeconds(timedelta):
    """
    Converts timedelta to seconds
    @param timedelta: timedelta
    @return: seconds
    """
    return float((timedelta.microseconds +
                (timedelta.seconds + timedelta.days * 24 * 3600)
        * 10 ** 6)) // 10 ** 6

if __name__ == '__main__':
    # TODO: Add tests here
    pass
