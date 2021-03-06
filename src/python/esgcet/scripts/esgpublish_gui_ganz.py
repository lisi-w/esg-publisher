#!/usr/bin/env python
#
# The ESG-CET Publisher Graphical User Interface  - esgpublish_gui module
#
###############################################################################
#                                                                             #
# Module:       tk_publisher module                                           #
#                                                                             #
# Copyright:    "See file Legal.htm for copyright information."               #
#                                                                             #
# Authors:      PCMDI Software Team                                           #
#               Lawrence Livermore National Laboratory:                       #
#                                                                             #
# Description:  The ESG-CET data provider can publish data through a command  #
#               line interface, an application-programming interface, or      #
#               through a client graphical user interface (GUI). This GUI     #
#               interface will guide the user through the publication process #
#               necessary to publish data into the ESG-CET repository. Once   #
#               the publication process is complete, the data will be         #
#               immediately visible to users via the ESG-CET Gateway.         #
#                                                                             #
#               This is the main Python/Tkinter file to create the ESG-CET    #
#               publisher GUI.                                                #
#                                                                             #
#                                                                             #
###############################################################################
#

import Tkinter, Pmw, tkFont
import sys, os
import gui_support
import logging
from esgcet.ui import pub_menu, pub_buttonexpansion, pub_editorviewer, pub_editoroutput, pub_controls, extraction_controls, statusbar
from esgcet.messaging import debug, info, warning, error, critical, exception
import datetime
from esgcet.config import splitRecord
from pkg_resources import resource_filename

# Get the previously saved state of the GUI
try:
   fn = '%s/.esgcet' % os.environ['HOME']
   sys.path.append(fn)
   import esgpublish_gui_settings
except:
   pass

esg_banner = resource_filename('esgcet.ui', 'esg_banner.gif')
esg_bg = resource_filename('esgcet.ui', 'esg_bg.gif')
esg_ini = resource_filename('esgcet.config.etc', 'esg.ini')


Version = "1.0 beta"


#----------------------------------------------------------------------------
# Create the Show Progress Status Widget at the bottom of the GUI
#----------------------------------------------------------------------------
class show_progress:
    """
    Show the graphical progress of a collection of datasets being scanned.
    """
    def __init__(self, root):
       parent = root.pane2.pane( 'EditPaneStatus' )

       root.statusbar = statusbar.Statusbar(parent, value=0, bg = 'aliceblue', color = 'red', margins = (2,5,1.5,1.5), xcounter=50, ycounter = 50)
       root.statusbar.pack( side = 'top', fill = "both", expand = 1)

#----------------------------------------------------------------------------
# Create the Widgets in the GUI
#----------------------------------------------------------------------------
class GUI_frame:
    """
    Generate the main GUI frame along with all the widgets.
    """
    def __init__(self, root):

       #---------------------------------------------------------------------
       # GUI initializations
       #---------------------------------------------------------------------
       root.Version=Version
       root.title( "ESG Data Node: Publisher's Graphical User Interface" )
       root.data_info_type = 0
       root.dir_str = ""
       root.extension = []
       root.password_flg = False
       root.validateStandardName = True
       root.aggregateDimension = "time"
       root.init_file = esg_ini
       n=datetime.datetime.now().timetuple()
       timestamp=str(n[1])+"-"+str(n[2])+"-"+str(n[0])+"_"+str(n[3])+":"+str(n[4])+":"+str(n[5])

       #---------------------------------------------------------------------
       # Set the size and position of the GUI window
       #---------------------------------------------------------------------
       try:
          geom_str = str(esgpublish_gui_settings.get.gui_width)+"x"+str(esgpublish_gui_settings.get.gui_height)+"+"+str(esgpublish_gui_settings.get.gui_x_position)+"+"+str(esgpublish_gui_settings.get.gui_y_position)
       except:
          max_w = root.winfo_screenwidth()
          max_h = root.winfo_screenheight()
          if max_w > 1700:
             h_width  = hull_width=int(max_w*0.80)
             h_height = int(max_h*0.80)
          else:
             h_width  = hull_width=int(max_w*0.75)
             h_height = int(max_h*0.70)
          geom_str = str(h_width)+"x"+str(h_height)+"+0+0"
       root.geometry(geom_str)

       #---------------------------------------------------------------------
       # Create a Paned Widget and set the three panes inside - left pane,
       # top_right pane, bottom_right pane
       #---------------------------------------------------------------------
       root.pane = Pmw.PanedWidget( root, 
		                 hull_borderwidth = 1,
		                 hull_relief = 'raised',
                                 orient = 'horizontal' )

       try:
          root.pane1_size = pane1_size = esgpublish_gui_settings.get.ControlPane_size
       except:
          root.pane1_size = pane1_size = 340
       root.pane.add( 'ControlPane', size=pane1_size)
       root.pane.pack(side='top', expand = 1, fill = 'x')

       root.pane.add( 'EditPane' )
       root.pane.pack(expand = 1, fill = 'both')

       root.pane2 = Pmw.PanedWidget( root.pane.pane( 'EditPane' ), 
		                 hull_borderwidth = 1,
		                 hull_relief = 'raised',
                                 orient = 'vertical' )

       try:
          root.pane2_size = pane2_size = esgpublish_gui_settings.get.EditPaneTop_size
       except:
          root.pane2_size = pane2_size = 550
       pane2_size_min = 300
       status_pane_min_max = 55

       root.pane2.add( 'EditPaneTop', size=pane2_size, min=pane2_size_min)
       root.pane2.pack(side='top')

       root.pane2.add( 'EditPaneBottom', size=pane2_size, min=pane2_size_min)
       root.pane2.pack(side='top', expand=1, fill='both' )

       root.pane2.add( 'EditPaneStatus', min=status_pane_min_max, max=status_pane_min_max )
       root.pane2.pack(side='top', expand=1, fill='both' )

       #---------------------------------------------------------------------
       # Create a Menu-Bar widget at top_left of of the window in left pane
       #---------------------------------------------------------------------
       root.menu = pub_menu.create_publisher_menu( root.pane.pane( 'ControlPane' ), root )
       root.menu.main_menu.pack(side='top', fill='x')

       #---------------------------------------------------------------------
       # Initialize GUI widget to track Collections, Datasets, and Queries
       #---------------------------------------------------------------------
       self.top_notebook = root.top_notebook = None
       self.row_frame_labels = root.row_frame_labels = {}
       self.version_label = root.version_label = {} # ganz
       #self.version_label1 = root.version_label = {} # ganz TODO test only
       self.row_frame_label2 = root.row_frame = {}
       self.add_row_frame = root.add_row_frame = {}
       self.top_tab_id = root.top_tab_id = {}
       self.top_page_id = root.top_page_id = {}
       self.top_page_id2 = root.top_page_id2 = {}
       #self.top_page_id2v = root.top_page_id2v = {}
       self.status_label = root.status_label = {}
       self.ok_err = root.ok_err = {}
       self.projectName = root.projectName = {}
       self.refreshButton = root.refreshButton = {}
       self.offline_file_directory = root.offline_file_directory = {}
       self.hold_offline = root.hold_offline = {}
       self.dmap = root.dmap = {}
       self.extraFields = root.extraFields = {}
       self.datasetMapfile = root.datasetMapfile = {}
       self.dirp_firstfile = root.dirp_firstfile = {}
       self.handlerDictionary = root.handlerDictionary = {}
       self.defaultGlobalValues = root.defaultGlobalValues = {}
       self.directoryMap = root.directoryMap = {}
       self.top_ct = root.top_ct = 1
       self.selected_top_page = root.selected_top_page = None
       
 

       #----------------------------------------------------------------------------
       # Create the Button Expansions in the ControlPane Widget located in the 
       # left pane
       #----------------------------------------------------------------------------
       root.pub_buttonexpansion = pub_buttonexpansion.create_publisher_button_expansion( root )

       #------------------------------------------------------------------------------
       # Show the ESG-CET banner across the top of the screen
       #------------------------------------------------------------------------------
       img = Tkinter.PhotoImage( file = esg_banner )
       root.frame_canvas = Tkinter.Label( root.pane2.pane( 'EditPaneTop' ),
                       image = img,
                       width = img.width()/1.26,
                       height = img.height()/2,
                       background = "black"
                       )
       root.frame_canvas.image = img
       root.frame_canvas.pack(side='top', fill='x')

       #----------------------------------------------------------------------------
       # Initialize the Publisher variables needed for scanning and publishing data
       #----------------------------------------------------------------------------
       root.file_counter = 0
       root.file_line = []
       root.config = None
       root.Session = None
       root.datasetName = None
       root.handler = None
       root.did_start = False
       root.thd = None

       #----------------------------------------------------------------------------
       # Create the top note book to display collections, offlines, queries, and dataset
       # information -- located in the top_right pane
       #----------------------------------------------------------------------------
       self.top_notebook = root.top_notebook = Pmw.NoteBook( 
            root.pane2.pane( 'EditPaneTop' ), 
            raisecommand = pub_controls.Command( self.evt_select_top_tab, root )
       )
       from esgcet.ui import pub_expand_query_gui
       root.parent = root

       #----------------------------------------------------------------------------
       # Make an instance of the top note book to that will display the collection,
       # offlines, queries, and dataset information
       #----------------------------------------------------------------------------
       root.create_publisher_editor_viewer = pub_editorviewer.create_publisher_editor_viewer

       #----------------------------------------------------------------------------
       # Make an instance of the bottom note book that will display processing 
       # and error messages
       #----------------------------------------------------------------------------
       root.pub_editoroutput = pub_editoroutput.create_publisher_editor_output( root )

       #----------------------------------------------------------------------------
       # Create the Status widget at the very bottom_right of the GUI
       #----------------------------------------------------------------------------
       show_progress( root )

    #----------------------------------------------------------------------------
    # Event to set the selected top page
    #----------------------------------------------------------------------------
    def evt_select_top_tab( self,  root, tab_name ):
       try:
          self.selected_top_page = self.top_tab_id[tab_name]
          # Enable or disable the "Data Publication" button
          if tab_name[:5] == "Query":
             root.pub_buttonexpansion.ControlButton3.configure( state = 'normal' )
          elif not root.refreshButton:
                  root.pub_buttonexpansion.ControlButton3.configure( state = 'normal' )
          elif root.refreshButton[ self.selected_top_page ].cget('relief') == 'flat':
                root.pub_buttonexpansion.control_frame3.pack_forget( )
                root.pub_buttonexpansion.control_toggle3 = 0
                root.pub_buttonexpansion.ControlButton3.configure( image = root.pub_buttonexpansion.right, state = 'disabled' )
          else:
                root.pub_buttonexpansion.ControlButton3.configure( state = 'normal' )
       except:
          root.pub_buttonexpansion.control_frame3.pack_forget( )
          root.pub_buttonexpansion.control_toggle3 = 0
          root.pub_buttonexpansion.ControlButton3.configure( image = root.pub_buttonexpansion.right, state = 'disabled' )

          #elif (tab_name[:7] in ["Offline", "Collect"]):
    #----------------------------------------------------------------------------
    # Event to remove note book tabs and its children widgets from the top_right
    # note book
    #----------------------------------------------------------------------------
    def evt_remove_top_tab( self,  tab_name, tab_type ):
      if tab_type in ["Collection", "Offline"]:
         try:
            del self.top_page_id[self.top_tab_id[tab_name]]
            del self.top_page_id2[self.top_tab_id[tab_name]]
            #del self.top_page_id2v[self.top_tab_id[tab_name]]
         except:
            del self.top_page_id[ tab_name ]
            del self.top_page_id2[ tab_name ]
            #del self.top_page_id2v[ tab_name ]
         del self.top_tab_id[ tab_name ]

      self.top_notebook.delete( tab_name )

def main():
   #------------------------------------------------------------------------------
   # We are using the same gui_support as VCDAT for possible future integration 
   #------------------------------------------------------------------------------
   root = gui_support.root()
   Pmw.initialise( root )

   #----------------------------------------------------------------------------
   # One time only call to setup the database session 
   #----------------------------------------------------------------------------
   root.echoSql = False
   extraction_controls.call_sessionmaker( root )

   #----------------------------------------------------------------------------
   # Initialize the GUI widgets
   #----------------------------------------------------------------------------
   root.main_frame = GUI_frame( root )

   #------------------------------------------------------------------------------
   # Display the ESG-CET world image in the background and the copyright
   #------------------------------------------------------------------------------
   root.canvas = Tkinter.Frame(root.pane2.pane( 'EditPaneTop' ))
   root.canvas.pack(side='top', fill='both', expand=1)

   txtFont = tkFont.Font(root, family = pub_controls.tab_font_type, size=pub_controls.tab_font_size)
   copywrite_text = "\nPublisher software version %s @ copyright LLNL/PCMDI\nEarth System Grid Center for Enabling Technologies, funded by the U.S. Department of Energy" % root.Version
   root.text = Tkinter.Label(root.canvas, text=copywrite_text, font=txtFont, bg = "white")
   root.text.pack(side='top', fill='both', expand=1)

   img = Tkinter.PhotoImage( file = esg_bg )
   root.canvas_img = Tkinter.Label( root.canvas, image = img, background = "white")
   root.canvas_img.image = img
   root.canvas_img.pack(side='top', fill='both', expand=1)

   #------------------------------------------------------------------------------
   # Redirect stderr and stdout to the output windows located in the bottom_right
   # pane (i.e., "Output" and "Error")
   # 
   # INFO messages are sent to the "Output" window -- that is, stdout
   #
   # WARNING, ERROR, DEBUG, CRITICAL, and Exception messages are sent to
   # the "Error" window -- that is, stderr
   #
   # Note: we distinguish between what is standard out and standard error,
   #       then display the appropriate window to view the text       
   #------------------------------------------------------------------------------
   sys.stdout = pub_controls.standard_out( root )
   sys.stderr = pub_controls.standard_err( root )

   #----------------------------------------------------------------------------
   # Log INFO messages to stdout and display the output to the "Output" window
   #----------------------------------------------------------------------------
   inf=logging.StreamHandler(sys.stdout)
   inf.setLevel(logging.INFO)
   logging.getLogger('Info').addHandler(inf)

   #----------------------------------------------------------------------------
   # Log WARNING messages to stderr and display the output to the "Error" window
   #----------------------------------------------------------------------------
   wrn=logging.StreamHandler(sys.stderr)
   wrn.setLevel(logging.WARNING)
   logging.getLogger('Warning').addHandler(wrn)

   #----------------------------------------------------------------------------
   # Log ERROR messages to stderr and display the output to the "Error" window
   #----------------------------------------------------------------------------
   err=logging.StreamHandler(sys.stderr)
   err.setLevel(logging.ERROR)
   logging.getLogger('Error').addHandler(err)

   #----------------------------------------------------------------------------
   # Log DEBUG messages to stderr and display the output to the "Error" window
   #----------------------------------------------------------------------------
   dbg=logging.StreamHandler(sys.stderr)
   dbg.setLevel(logging.DEBUG)
   logging.getLogger('Debug').addHandler(dbg)

   #----------------------------------------------------------------------------
   # Log CRITICAL messages to stderr and display the output to the "Error" window
   #----------------------------------------------------------------------------
   crt=logging.StreamHandler(sys.stderr)
   crt.setLevel(logging.CRITICAL)
   logging.getLogger('Critical').addHandler(crt)

   #----------------------------------------------------------------------------
   # Log Exception messages to stderr and display the output to the "Error" window
   #----------------------------------------------------------------------------
   exc=logging.StreamHandler(sys.stderr)
   exc.setLevel(logging.ERROR)
   logging.getLogger('Exception').addHandler(exc)

   #----------------------------------------------------------------------------
   # Test the message print commands from logging --- the below lines are
   # showing examples of how to use Python logging for message sending
   #----------------------------------------------------------------------------
   #debug("%d: This is the Debug Test" % logging.DEBUG)
   #info("%d: This is the Info Test" % logging.INFO)
   #warning("%d: This is Warning Test" % logging.WARNING)
   #error("%d: This is the Error Test" % logging.ERROR)
   #critical("%d: This is the Critical Test" % logging.CRITICAL)
   #exception("%d: This is the Exception (NotSet) Test" % logging.NOTSET)

   #---------------------------------------------------------------------
   # View the GUI on the screen.
   #---------------------------------------------------------------------
   root.deiconify()
   root.update()
   root.lift()

   #---------------------------------------------------------------------
   # Enter the Tkinter main event loop
   #---------------------------------------------------------------------
   root.mainloop()

#---------------------------------------------------------------------
# Call the main routine to execute the program
#---------------------------------------------------------------------
if __name__ == "__main__":
    main()

#---------------------------------------------------------------------
# End of File
#---------------------------------------------------------------------
