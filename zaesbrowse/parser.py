
'''
This file is part of ZAESBrowse.

ZAESBrowse is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

ZAESBrowse is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more 
details.

You should have received a copy of the GNU General Public License along
with ZAESBrowse.  If not, see <http://www.gnu.org/licenses/>.
'''

import re

class Parser( object ):

   contents = ''
   highlighted_words = []

   def __init__( self, contents, highlighted_words=[] ):
      
      self.contents = contents
      
   def parse( self ):

      # TODO: Iterate through the body and wrap highlighted_words in spans.

      # TODO: Maybe move parsers to a plugin system or something.

      re_pidgin = re.compile( '^Conversation with .*' )
      
