#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 28.06.2011

@author: denex
'''

from __future__ import with_statement
import os
import sys
from datetime import datetime, timedelta, time
from urllib2 import urlopen

magic_k = 8 / 7.75
GMT_OFFSET_HOURS = +7  # Asia/Novosibirsk

stdout = sys.stdout
stderr = sys.stderr


class iEvent():

    def __init__(self):
        self._summary = None
        self.dtstart = None
        self.dtend = None

    def close(self):
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
        if self._summary.upper().startswith('VIERA'):
            result += ';Viera'
        elif self._summary.upper().startswith('NATEXPO'):
            result += ';NATEXPO'
        elif self._summary.upper().startswith('LMD'):
            result += ';LMD'
        elif self._summary.lower().startswith('mail.ru'):
            result += ';Mail.ru'
        elif self._summary.lower().startswith('vk2'):
            result += ';Vkontakte2'
        elif self._summary.lower().startswith('eplaza'):
            result += ';eplaza'
        return result

    def as_row(self):
        return [self.dtstart.strftime('%d.%m.%Y'),
                self._summary,
                self.dtstart.strftime('%H:%M'),
                self.dtend.strftime('%H:%M'),
                self.getDurationStr()]

    """
    Set summary for events
    """
    def setSummary(self, rawSummary):
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

    """
    @return: DateTime
    """
    def getDateTimeFromStr(self, dateString):
        timeOffset = 0
        formatStr = '%Y%m%dT%H%M%S'
        if dateString.startswith(';VALUE=DATE:'):
            formatStr = '%Y%m%d'
        datetimes = dateString.partition(':')[-1]
        if datetimes.endswith('Z'):
            datetimes = datetimes[:-2]
            timeOffset = GMT_OFFSET_HOURS
        try:
            date = datetime.strptime(datetimes, formatStr)
        except ValueError:
            print>>stderr, "DateStr:", dateString
            raise
        else:
            if timeOffset != 0:
                date += timedelta(hours=timeOffset)
            return date

    """
    @return: Event duration as timedelta
    """
    def duration(self):
        return self.dtend - self.dtstart

    """
    @return: String value of time delta
    """
    def getDurationStr(self):
        seconds = getTotalSeconds(self.duration())
        hours = seconds // 3600
        mins = (seconds - hours * 3600) // 60
        return '%d:%02d' % (hours, mins)
# End of class iEvent


def getRawEventsFromFile(fileName):
    """
    @return: a list of events
    """
    with open(fileName) as efile:
        return get_events_from_stream(efile)


def getRawEventsFromUrl(url):
    return get_events_from_stream(urlopen(url, timeout=3))


def get_events_from_stream(string_stream):
    event = None
    eventList = []
    eventContext = []
    for raw_line in string_stream:
        line = raw_line
        try:
            line = line.replace('\r', '').replace('\n', '')
        except:
            raise
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
            if event.close():
                eventList.append(event)
            else:
                print>>stderr, "Broken event:", eventContext
                print>>stderr, repr(event)
        else:
            # print>>stderr, line
            pass
    # sort list by dtstart
    return sorted(eventList, key=lambda ev: ev.dtstart)


def getNextMondayDate(currentDate):
    monDate = currentDate + timedelta(days=-currentDate.weekday(), weeks=1)
    return datetime.combine(monDate, time())


def getLastMondayDate(currentDate):
    monDate = currentDate + timedelta(days=-currentDate.weekday())
    return datetime.combine(monDate, time())


def getTotalSeconds(timedelta):
    """
    Converts timedelta to seconds
    @param timedelta: timedelta
    @return: seconds
    """
    return float((timedelta.microseconds +
                (timedelta.seconds + timedelta.days * 24 * 3600)
        * 10 ** 6)) // 10 ** 6


def printWorkHoursPerWeek(workHoursPerWeek):
    """
    @param workHoursPerWeek: timedelta
    """
    seconds = getTotalSeconds(workHoursPerWeek)
    if seconds > 0:
        printWorkHoursFromSeconds(seconds)
        # Multiply
        seconds = seconds * magic_k
        # Round to 15 mins
        seconds = seconds - seconds % (15 * 60)
        printWorkHoursFromSeconds(seconds, 7)
        print>>stderr, seconds // 3600,
    return


def printWorkHoursFromSeconds(seconds, position=6):
    """
    Prints
    @param seconds: seconds
    @param position: Number of column
    """
    if seconds > 0:
        print>>stdout, ('%s%.2f' % (
            ';' * position, seconds // 3600)).replace('.', ',')


def main():

    if len(sys.argv) > 1:
        ical_source = sys.argv[1]
    else:
        # HomeDir
        default_filename = os.path.expanduser(os.path.join(
            "~", "Dropbox", "Efforts", "Рабочий.ics"))
        if os.path.isfile(default_filename):
            ical_source = default_filename
        else:
            ical_source = "test.ics"
    if ical_source.startswith('http'):
        rawEvents = getRawEventsFromUrl(ical_source)
    else:
        rawEvents = getRawEventsFromFile(ical_source)

    events = rawEvents

    print>>stdout, ur'"Дата";"Описание";"Начало";"Окончание";"Длительность";"Проект";"Сумма часов за неделю";"Скорректированная cумма часов за неделю"'
    nextMondayDate = None
    lastMondayDate = None
    lastlastMondayDate = None
    lastDay = None
    workHoursPerDay = timedelta()
    workHoursPerWeek = timedelta()

    for event in events:
        if None == nextMondayDate or event.dtstart >= nextMondayDate:
            lastlastMondayDate = lastMondayDate if lastMondayDate is not None else getLastMondayDate(
                event.dtstart.date())
            lastMondayDate = nextMondayDate if nextMondayDate is not None else getLastMondayDate(
                event.dtstart.date())
            nextMondayDate = getNextMondayDate(event.dtstart.date())
            if getTotalSeconds(workHoursPerWeek) > 0:
                print>>stderr, "from", lastlastMondayDate.strftime(
                    '%d.%m.%Y'), "to", lastMondayDate.strftime('%d.%m.%Y'), "worked",
                printWorkHoursPerWeek(workHoursPerWeek)
                print>>stderr, "hours"
                # Zero work time for new week
                workHoursPerWeek = timedelta()
        if lastDay != event.dtstart.date():
            if lastDay is not None:
                print>>stderr, lastDay.strftime(
                    '%d.%m.%Y'), workHoursPerDay
            workHoursPerDay = timedelta()
            lastDay = event.dtstart.date()
        # Sum work time per day
        workHoursPerDay += event.duration()
        # Sum work time for week
        workHoursPerWeek += event.duration()
        # Prints line with event
        print>>stdout, event

    if workHoursPerDay != timedelta():
        print>>stderr, lastDay, workHoursPerDay
    print>>stderr, "from", lastMondayDate.strftime(
        '%d.%m.%Y'), "to", nextMondayDate.strftime('%d.%m.%Y'), "worked",
    printWorkHoursPerWeek(workHoursPerWeek)
    print>>sys.stderr, "hours"

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    main()
