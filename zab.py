#!/usr/bin/env python

'''
This file is part of ZAESBrowse.

ZAESBrowse is free software: you can redistribute it and/or modify it under 
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

ZAESBrowse is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more 
details.

You should have received a copy of the GNU Lesser General Public License along
with ZAESBrowse.  If not, see <http://www.gnu.org/licenses/>.
'''

import gtk
import re
import yaml
import logging
import zaesbrowse.browser

def main():

   logging.basicConfig( level=logging.INFO )

   zaesbrowse.browser.Browser()

   '''
   parser = argparse.ArgumentParser()
   subparsers = parser.add_subparsers( dest='command' )

   parser_search = subparsers.add_parser( 'search' )
   #parser_search.add_argument(
   #   '-c', '--context', action='store', dest='context', type=int, default=3,
   #   help='The number of lines of context (in each direction) to display ' +
   #      'for each result.'
   #)
   parser_search.add_argument(
      'archive_path', action='store',
      help='The archive file to search within.'
   )
   parser_search.add_argument(
      'search_phrase', action='store',
      help='The phrase to search for within the archive.'
   )

   args = parser.parse_args()

   elif 'search' == args.command:
      result_list = ifdyutil.archive.search(
         args.archive_path, key, PIDGIN_LOG_KEY_SALT, args.search_phrase
      )
      try:
         import arcbrowse
         zaesbrowse.browser.Browser( result_list, args.search_phrase )
      except Exception, e:
         # Fall back to the command line.
         # TODO: Implement CLI search result viewer.
         logger.error(
            'Unable to start graphical log viewer: {}'.format( e.message )
         )
   '''

if '__main__' == __name__:
   main()

