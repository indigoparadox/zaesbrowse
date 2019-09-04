#!/usr/bin/env python

# IFDY:USE:any

import argparse
import os
import re
import datetime
import logging
import sys
import codecs
import ifdyutil.archive

PIDGIN_LOG_DIR = os.path.join( os.path.expanduser( '~' ), '.purple', 'logs' )
ERROR_NO_ARCHIVE = 1

def list_logs(
   protocols_accounts, date_start=None, date_end=None, log_dir=PIDGIN_LOG_DIR
):

   ''' Build and return a list of all logs between the specified dates. 
   protocols_accounts should be in the format of {'protocol': ['account']}. '''

   logger = logging.getLogger( 'archive.pidginlogs.list' )

   list_out = []

   # Fill in missing parameters.
   if not date_start:
      date_start = datetime.date.min
   if not date_end:
      date_end = datetime.date.today()

   # A regex to match the date format presented in the log filenames.
   re_logdate = re.compile(
      r'(?P<year>[0-9]+?)\-(?P<month>[0-9]+?)\-(?P<day>[0-9]+?)\.' +
         r'(?P<hour>[0-9].)(?P<minute>[0-9].)(?P<second>[0-9].)' +
         r'(?P<timezone>\-.+)?.txt'
   )

   if protocols_accounts:
      # TODO: A list of protocols/accounts has been specified, so walk them
      #       specifically.
      for account_list in protocols_accounts.iteritems:
         for root, dirnames, filenames in os.walk( log_dir ):
            print root
   else:
      # Walk all protocols and accounts.
      for root, dirnames, filenames in os.walk( log_dir ):
         for filename in filenames:
            fn_match = re_logdate.match( filename )
            if fn_match:
               date_log = datetime.date(
                  int( fn_match.group( 'year' ) ),
                  int( fn_match.group( 'month' ) ),
                  int( fn_match.group( 'day' ) )
               )
               if date_log >= date_start and date_log <= date_end:
                  # The log is within range, so add it to the list.
                  log_path = os.path.join( root, filename )
                  try:
                     with codecs.open(
                        log_path, encoding='utf-8', mode='r'
                     ) as log_file:
                        list_out.append( {
                           'path_abs': log_path,
                           'path_rel': log_path[len( log_dir ):],
                           'contents':  log_file.read()
                        } )
                  except Exception, e:
                     logger.warning(
                        'Unable to open "{}" as utf-8, attempting latin1...'
                           .format(
                              log_path
                           )
                     )
                     with codecs.open(
                        log_path, encoding='latin1', mode='r'
                     ) as log_file:
                        list_out.append( {
                           'path_abs': log_path,
                           'path_rel': log_path[len( log_dir ):],
                           'contents':  log_file.read()
                        } )

   return list_out

def _parse_date_arg( date_string ):
   date_match = re.match(
      # The final missing ? isn't a mistake.
      r'(?P<year>[0-9]+?)\-(?P<month>[0-9]+?)\-(?P<day>[0-9]+)',
      date_string
   )
   if None != date_match:
      return datetime.date(
         int( date_match.group( 'year' ) ),
         int( date_match.group( 'month' ) ),
         int( date_match.group( 'day' ) )
      )
   else:
      return None

def main():

   parser = argparse.ArgumentParser()

   parser.add_argument(
      '-p', '--log-path', action='store', dest='log_dir', type=str,
      default=PIDGIN_LOG_DIR,
      help='The directory in which logs are contained. Defaults to {}.'.format(
         PIDGIN_LOG_DIR
      )
   )
   parser.add_argument(
      '-d', '--delete', action='store_true', dest='delete',
      help='Delete logs that are added to the archive.'
   )
   parser.add_argument(
      '-s', '--start-date', action='store', dest='start_date', default='',
      help='The date to start the archive from, in the format YYYY-MM-DD.'
   )
   parser.add_argument(
      '-e', '--end-date', action='store', dest='end_date', default='',
      help='The date to stop the archive at, in the format YYYY-MM-DD.'
   )
   parser.add_argument(
      'archive_path', action='store',
      help='The archive file to create.'
   )

   args = parser.parse_args()

   logging.basicConfig( level=logging.INFO )
   logger = logging.getLogger( 'archive.pidginlogs' )

   # Get the key from stdin.
   logger.info( 'Enter archive encryption key:' )
   key = sys.stdin.readline().strip()

   log_list = list_logs(
      {},
      _parse_date_arg( args.start_date ),
      _parse_date_arg( args.end_date ),
      args.log_dir
   )
   ifdyutil.archive.create(
      args.archive_path,
      key,
      item_list=log_list
   )
   # Perform deletions last to make sure everything else was successful
   # first.
   if args.delete:
      for item in log_list:
         # Remove file if requested.
         os.unlink( item['path_abs'] )

         # Remove parent directories if empty.
         try:
            parent_path = os.path.dirname( item['path_abs'] )
            os.rmdir( parent_path )
            logger.info(
               'Removed empty directory {}.'.format( parent_path )
            )
         except:
            logger.debug(
               'Not removing non-empty directory {}.'.format( parent_path )
            )

if '__main__' == __name__:
   main()

