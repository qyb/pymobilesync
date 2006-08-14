#----------------------------------------------------------------------
# A very simple wxPython example.  Just a wx.Frame, wx.Panel,
# wx.StaticText, wx.Button, and a wx.BoxSizer, but it shows the basic
# structure of any wxPython application.
#----------------------------------------------------------------------

import wx

from sqlitepb import *
pbfile = '004601012106440-449117B5.sqlite'

class MyListCtrl(wx.ListCtrl):
    def OnGetItemText(self, item, col):
        if col == 0:
            return self.addrlist[item][2] + self.addrlist[item][3]
        elif col == 1:
            return self.addrlist[item][5]
        elif col == 2:
            return self.addrlist[item][4]
        elif col == 3:
            return self.addrlist[item][6]
        elif col == 4:
            return self.addrlist[item][7]
        else:
            return 'NA'
        
    def __init__(self, parent):
        self.sortlist = [ ['1','2','3','4','5'],['6','7','8','9','10'] ]
        self.pb = sqlitepb(pbfile)
        self.addrlist = self.pb.fetchall()
        self.pb.close()
        wx.ListCtrl.__init__(self, parent, -1, size=(700,480),
                             style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES)
        self.InsertColumn(0, "Name")
        self.InsertColumn(1, "Mobile Phone")
        self.InsertColumn(2, "Email")
        self.InsertColumn(3, "Home Phone")
        self.InsertColumn(4, "Work Phone")
        self.SetColumnWidth(0, 80)
        self.SetColumnWidth(1, 160)
        self.SetColumnWidth(2, 200)
        self.SetColumnWidth(3, 120)
        self.SetColumnWidth(4, 120)
        self.SetItemCount(len(self.addrlist))
        return

    
class MyFrame(wx.Frame):
    """
    This is MyFrame.  It just shows a few controls on a wxPanel,
    and has a simple menu.
    """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title,
                          pos=(150, 150), size=(705, 540))

        # Create the menubar
        menuBar = wx.MenuBar()

        # and a menu 
        menu = wx.Menu()

        # add an item to the menu, using \tKeyName automatically
        # creates an accelerator, the third param is some help text
        # that will show up in the statusbar
        menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit this simple sample")

        # bind the menu event to an event handler
        self.Bind(wx.EVT_MENU, self.OnTimeToClose, id=wx.ID_EXIT)

        # and put the menu on the menubar
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)

        self.CreateStatusBar()
        

        # Now create the Panel to put the other controls on.
        panel = wx.Panel(self)

        '''
        # and a few controls
        text = wx.StaticText(panel, -1, "Hello World!")
        text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        text.SetSize(text.GetBestSize())
        btn = wx.Button(panel, -1, "Close")
        funbtn = wx.Button(panel, -1, "Just for fun...")

        # bind the button events to handlers
        self.Bind(wx.EVT_BUTTON, self.OnTimeToClose, btn)
        self.Bind(wx.EVT_BUTTON, self.OnFunButton, funbtn)
        '''

        # create ListCtrl
        # Use a sizer to layout the controls, stacked vertically and with
        # a 10 pixel border around each
        sizer = wx.BoxSizer(wx.VERTICAL)
        abTable = MyListCtrl(panel)
        sizer.Add(abTable, 0, wx.ALL, 0)
        '''
        sizer.Add(text, 0, wx.ALL, 10)
        sizer.Add(btn, 0, wx.ALL, 10)
        sizer.Add(funbtn, 0, wx.ALL, 10)
        '''
        panel.SetSizer(sizer)
        panel.Layout()


    def OnTimeToClose(self, evt):
        """Event handler for the button click."""
        print "See ya later!"
        self.Close()

    def OnFunButton(self, evt):
        """Event handler for the button click."""
        print "Having fun yet?"


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "Simple wxPython App")
        self.SetTopWindow(frame)

        print "Print statements go to this stdout window by default."

        frame.Show(True)
        return True
        
app = MyApp(redirect=True)
app.MainLoop()

