
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

import gtk

class UnlockDialog( gtk.MessageDialog ):

    def __init__( self, *args, **kwargs ):

        # Set the initial properties.
        kwargs = {
            'flags': gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            'type': gtk.MESSAGE_QUESTION,
            'buttons': gtk.BUTTONS_OK_CANCEL,
        }
        super( UnlockDialog, self ).__init__( *args, **kwargs )
        self.set_markup( 'Please enter the archive encryption key:' )

        # Create the text entry field.
        self.entry = gtk.Entry()
        self.entry.show()
        self.entry.set_visibility( False )
        
        self.vbox.pack_end( self.entry )
        self.entry.connect(
            'activate', lambda _: self.response( gtk.RESPONSE_OK )
        )
        self.set_default_response( gtk.RESPONSE_OK )

    def run( self ):
        # Process the response.
        response = super( UnlockDialog, self ).run()
        text = self.entry.get_text()
        self.destroy()
        if gtk.RESPONSE_OK == response:
            return text
        else:
            return None

class SearchDialog( gtk.MessageDialog ):

    def __init__( self, *args, **kwargs ):

        # Set the initial properties.
        kwargs = {
            'flags': gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            'type': gtk.MESSAGE_QUESTION,
            'buttons': gtk.BUTTONS_OK_CANCEL,
        }
        super( SearchDialog, self ).__init__( *args, **kwargs )
        self.set_markup( 'Please enter the phrase to search for:' )

        # Create the text entry field.
        self.entry = gtk.Entry()
        self.entry.show()
        
        self.vbox.pack_end( self.entry )
        self.entry.connect(
            'activate', lambda _: self.response( gtk.RESPONSE_OK )
        )
        self.set_default_response( gtk.RESPONSE_OK )

    def run( self ):
        # Process the response.
        response = super( SearchDialog, self ).run()
        text = self.entry.get_text()
        self.destroy()
        if gtk.RESPONSE_OK == response:
            return text
        else:
            return None

