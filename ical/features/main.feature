Feature: Test convert iCal to CSV

    Scenario: Convert iCal file to CSV
        Given I access the url "/ical/"
        When I upload CSV file
        Then I see table with events
