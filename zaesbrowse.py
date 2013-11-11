#!/usr/bin/env python

# IFDY:USE:desktop

import gtk
import re
import yaml

class ArchiveBrowser( object ):

   window = None
   editor = None
   results = []
   phrase = ''

   def __init__( self, result_list, search_phrase='' ):

      self.results = result_list
      self.phrase = search_phrase

      self.window = gtk.Window()
      self.window.set_title( 'PyNoteWiki Viewer' )
      self.window.connect( 'destroy', gtk.main_quit )

      mb = gtk.MenuBar()

      # Create the file menu.
      filemenu = gtk.Menu()
      filem = gtk.MenuItem( 'File' )
      filem.set_submenu( filemenu )

      exitm = gtk.MenuItem( 'Exit' )
      exitm.connect( 'activate', gtk.main_quit )
      filemenu.append( exitm )

      mb.append( filem )

      # Create the log list.
      self.listbox = gtk.List()
      self.listbox.connect( 'selection_changed', self.on_selection )
      # TODO: Get the scrolling/sizing stuff sorted.
      listbox_scroller = gtk.ScrolledWindow()
      listbox_scroller.set_size_request( 200, 200 )
      listbox_scroller.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
      listbox_scroller.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
      listbox_scroller.add_with_viewport( self.listbox )

      for log in result_list:
         label = gtk.Label( log.get( 'filename' ) )
         list_item = gtk.ListItem()
         list_item.add( label )
         list_item.set_data( 'contents', log.get( 'contents' ) )
         self.listbox.add( list_item )

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

   def on_selection( self, widget ):
      selection = widget.get_selection()
      
      if not selection:
         return

      # Load the selection text into the editor.
      for item in selection:
         contents = item.get_data( 'contents' )

         # Set the buffer text.
         buf = self.editor.get_buffer()
         buf.remove_all_tags( buf.get_start_iter(), buf.get_end_iter() )
         buf.set_text( contents )

         # Find all lines with the search phrase in them.
         phrase_words = self.phrase.split( ' ' )
         for word in phrase_words:
            # Clean out non-alphanumeric symbols.
            word = re.sub( r'\W+', '', word )

            # Perform the highlight.
            phrase_spans = re.finditer( re.escape( word ), contents )
            for span in phrase_spans:
               span = span.span()
               buf.apply_tag_by_name(
                  'highlighted',
                  buf.get_iter_at_offset( span[0] ),
                  buf.get_iter_at_offset( span[1] )
               )


class InputDialog( gtk.MessageDialog ):

   def __init__( self, *args, **kwargs ):

      # Parse special arguments.
      if 'password' in kwargs:
         password = kwargs['password']
         del kwargs['password']
      else:
         password = False
      
      if 'label_text' in kwargs:
         label_text = kwargs['label_text']
         del kwargs['label_text']
      else:
         label_text = ''

      super( InputDialog, self ).__init__( *args, **kwargs )

      self.set_title( label_text )
      self.add_buttons( 
         gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
         gtk.STOCK_OK, gtk.RESPONSE_OK
      )

      # Create the label.
      label = gtk.Label( label_text )

      # Create the text entry.
      entry = gtk.Entry()        
      entry.connect(
         "activate", 
         lambda ent, dlg, resp: dlg.response( resp ),
         self, gtk.RESPONSE_OK
      )
      self.entry = entry
      if password:
         self.entry.set_visibility( False )

      # Pack and show.
      self.vbox.pack_start( label, False, 5, 5 )
      self.vbox.pack_end( entry, True, True, 0 )
      self.vbox.show_all()

   def run( self ):
      result = super( InputDialog, self ).run()
      if gtk.RESPONSE_OK == result:
         return self.entry.get_text()
      else:
         return None

class OpenDialog( gtk.FileChooserDialog ):

   caller_id = 'ifdyscripts'

   def __init__( self, *args, **kwargs ):

      if 'caller_id' in kwargs:
         caller_id = kwargs['caller_id']
         del kwargs['caller_id']

      super( OpenDialog, self ).__init__( *args, **kwargs )

      self.set_title( 'Open archive file...' )
      self.add_buttons( 
         gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
         gtk.STOCK_OPEN, gtk.RESPONSE_OK
      )

      # TODO: Set the starting directory to the saved directory for the 
      #       caller_id.

   def run( self ):
      result = super( OpenDialog, self ).run()
      if gtk.RESPONSE_OK == result:
         # TODO: Save the chosen filename directory for later.
         return self.get_filename()
      else:
         return None

#if '__main__' == __name__:

