# LoadTesting

This script will run through a number of queries specified by the --count argument with a delaying a number of seconds specified by --delay between them.

It will then open a browser (firefox by default) with the ARAX results for each of these queries.  The intention is to test the ARS' ability to handle load both from query submissions and the auto-refresh of the ARAX interface.  Current defaults are 10 queries with 0 seconds of delay.
