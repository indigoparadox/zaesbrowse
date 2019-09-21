
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
import logging
import re
import dialogs
import sys
import ifdyutil.archive

class Browser( object ):

    window = None
    editor = None
    results = []
    phrase = ''
    logger = None
    arcz = None

    def __init__( self ):

        self.logger = logging.getLogger( 'zaesbrowse.browser' )

        self.window = gtk.Window()
        self.window.set_title( 'ZAES Archive Viewer' )
        self.window.connect( 'destroy', gtk.main_quit )

        mb = gtk.MenuBar()

        # Create the file menu.
        filemenu = gtk.Menu()
        filem = gtk.MenuItem( 'File' )
        filem.set_submenu( filemenu )

        openm = gtk.MenuItem( 'Open...' )
        openm.connect( 'activate', self.on_open )
        filemenu.append( openm )

        exitm = gtk.MenuItem( 'Exit' )
        exitm.connect( 'activate', gtk.main_quit )
        filemenu.append( exitm )

        mb.append( filem )

        # Create a tools menu.
        toolsmenu = gtk.Menu()
        toolsm = gtk.MenuItem( 'Tools' )
        toolsm.set_submenu( toolsmenu )

        searchm = gtk.MenuItem( 'Search...' )
        searchm.connect( 'activate', self.on_search )
        toolsmenu.append( searchm )

        upgradem = gtk.MenuItem( 'Upgrade...' )
        upgradem.connect( 'activate', self.on_upgrade )
        toolsmenu.append( upgradem )

        mb.append( toolsm )

        # Create the log list.
        self.listbox = gtk.List()
        self.listbox.connect( 'selection_changed', self.on_selection )
        listbox_scroller = gtk.ScrolledWindow()
        listbox_scroller.set_size_request( 200, 200 )
        listbox_scroller.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        listbox_scroller.add_with_viewport( self.listbox )

        # Create the log viewer.
        self.editor = gtk.TextView()
        self.editor.set_editable( False )
        editor_scroller = gtk.ScrolledWindow()
        editor_scroller.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        editor_scroller.add( self.editor )
      
        buf = self.editor.get_buffer()
        buf.create_tag( 'highlighted', background='red' )

        # Pack the widgets and show the window.
        hbox = gtk.HBox( False, 2 )
        hbox.pack_start( listbox_scroller, False, False, 0 )
        hbox.pack_start( editor_scroller, True, True, 0 )

        vbox = gtk.VBox( False, 2 )
        vbox.pack_start( mb, False, False, 0 )
        vbox.pack_start( hbox, True, True, 0 )
        self.window.add( vbox )
        self.window.show_all()

        gtk.main()

    def show_search( self, phrase=None, arcz=None ):

        # Update the search results.
        #self.results = result_list
        if None != phrase:
            self.phrase = phrase

        if arcz:
            self.arcz = arcz

        # Clear the buffer.
        buf = self.editor.get_buffer()
        buf.remove_all_tags( buf.get_start_iter(), buf.get_end_iter() )

        # Find all lines with the search phrase in them.
        phrase_words = self.phrase.split( ' ' )
        for word in phrase_words:
            # Clean out non-alphanumeric symbols.
            word = re.sub( r'\W+', '', word )

            # Perform the highlight.
            phrase_spans = re.finditer(
                re.escape( word ),
                buf.get_text( buf.get_start_iter(), buf.get_end_iter() )
            )
            for span in phrase_spans:
                span = span.span()
                buf.apply_tag_by_name(
                    'highlighted',
                    buf.get_iter_at_offset( span[0] ),
                    buf.get_iter_at_offset( span[1] )
                )

        # Refresh the file list.
        if None != phrase:
            # Clear the list box.
            for child in self.listbox.get_children():
                child.destroy()

            # Get the new results and post them.
            result_list = ifdyutil.archive.search( self.arcz, self.phrase )
            if not result_list:
                # Looks like we need to improvise.
                result_list = []
                for item in self.arcz.namelist():
                    item_file = self.arcz.open( item )
                    result_list.append( {
                        'filename': item,
                        'contents': item_file.read()
                    } )
                    item_file.close()
                    
            for item in result_list:
                # Skip index directories.
                if item.get( 'filename' ).startswith( '/index' ):
                    continue

                # Create and add the listbox item.
                label = gtk.Label( item.get( 'filename' ) )
                label.set_alignment( 0, 0.5 )
                label.show()
                list_item = gtk.ListItem()
                list_item.add( label )
                list_item.set_data( 'contents', item.get( 'contents' ) )
                list_item.show()
                self.listbox.add( list_item )

    def on_search( self, widget ):
        phrase = dialogs.SearchDialog( self.window ).run()
        self.show_search( phrase )

    def on_upgrade( self, widget ):

        if not self.arcz:
            self.logger.error( 'No open archive available to upgrade.' )
            return

        # Display a file open dialog.
        dialog =  gtk.FileChooserDialog(
            'Save Archive...',
            None,
            gtk.FILE_CHOOSER_ACTION_SAVE,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_SAVE, gtk.RESPONSE_OK)
        )
        dialog.set_default_response( gtk.RESPONSE_OK )
        response = dialog.run()
        file_name = dialog.get_filename()
        dialog.destroy()

        if gtk.RESPONSE_OK == response:
            new_key = dialogs.UnlockDialog( self.window ).run()
            item_list = []
            for name in self.arcz.namelist():
                item_list.append( {
                    'path_rel': name,
                    'contents': self.arcz.read( name )
                } )
            ifdyutil.archive.create(
                file_name,
                new_key,
                item_list=item_list,
                index=False
            )

    def on_open( self, widget ):

        # Display a file open dialog.
        dialog =  gtk.FileChooserDialog(
            'Open Archive...',
            None,
            gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK)
        )
        dialog.set_default_response( gtk.RESPONSE_OK )
        #if None != self.config.get_value( 'LastDir' ):
        #    dialog.set_current_folder( self.config.get_value( 'LastDir' ) )

        zaesfilter = gtk.FileFilter()
        zaesfilter.set_name( 'ZAES Archives' )
        zaesfilter.add_pattern( '*.zaes' )
        dialog.add_filter( zaesfilter )

        allfilter = gtk.FileFilter()
        allfilter.set_name( 'All Files' )
        allfilter.add_pattern( '*' )
        dialog.add_filter( allfilter )

        response = dialog.run()
        file_name = dialog.get_filename()
        dialog.destroy()
        if gtk.RESPONSE_OK == response:
            # Store the last used path for later.
            #self.config.set_value(
            #    'LastDir', os.path.dirname( dialog.get_filename() )
            #)

            key = dialogs.UnlockDialog( self.window ).run()
            if None == key:
                return

            arcz = ifdyutil.archive.handle( file_name, key )
            # 'dCJVFT%fv345gyW'
            if self.arcz:
                self.arcz.close()
            self.arcz = arcz
            if self.arcz:
                self.show_search( phrase='', arcz=arcz )

    def on_selection( self, widget ):
        selection = widget.get_selection()
        
        if not selection:
            return

        # Load the selection text into the editor.
        for item in selection:
            contents = item.get_data( 'contents' )

            # Set the buffer text.
            buf = self.editor.get_buffer()
            buf.set_text( contents )

            self.show_search()

