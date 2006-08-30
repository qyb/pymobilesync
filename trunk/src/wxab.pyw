#----------------------------------------------------------------------
# A very simple wxPython example.  Just a wx.Frame, wx.Panel,
# wx.StaticText, wx.Button, and a wx.BoxSizer, but it shows the basic
# structure of any wxPython application.
#----------------------------------------------------------------------

import wx

import os.path

def testfile(filepath):
    if os.path.exists(filepath) == True:
        return True
    path = os.path.split(filepath)
    try:
        os.makedirs(path[0])
    except:
        pass
    return False
    
        
from sqlitepb import *
default_pbfile = 'sqlite/local.sqlite'

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
        testfile(default_pbfile) #create directory if not exist
        self.pb = sqlitepb(default_pbfile)
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

class ContactDialog(wx.Dialog):
    args = ["First Name:",
        "Last Name:",
        "Home Phone:",
        "Work Phone:",
        "Mobile Phone:",
        "Email Addr:",
        "Title: ",
        "Organization: "]
    text = []

    def __init__(self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE
                 ):
        
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)
        sizer = wx.BoxSizer(wx.VERTICAL)

        for arg in self.args:
            box = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self, -1, arg)
            box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            text = wx.TextCtrl(self, -1, "", size=(80,-1))
            self.text.append(text)
            box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
            sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btn = wx.Button(self, wx.ID_CANCEL)
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btnsizer.Realize()
        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def GetValue(self):
        ret = {}
        i = 0
        for arg in self.args:
            ret[arg] = self.text[i].GetValue()
            i+=1
        return ret
        
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

        addr_menu = wx.Menu()
        addr_menu.Append(101, "New Contact")
        self.Bind(wx.EVT_MENU, self.newContact, id=101)
        menuBar.Append(addr_menu, "&Contact")

        sync_menu = wx.Menu()
        sync_menu.Append(201, "Sync with IR(Ericsson/Siemens)")
        self.Bind(wx.EVT_MENU, self.syncIRMC, id=201)
        #sync_menu.Append(202, "Sync with IR(Nokia)")
        menuBar.Append(sync_menu, "&Sync")
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

    def newContact(self, event):
        dlg = ContactDialog(self, -1, "ttt", size=(350, 200), style = wx.DEFAULT_DIALOG_STYLE)
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            print dlg.GetValue()

        dlg.Destroy()
        return

    def syncIRMC(self, event):
        return


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "Simple wxPython App")
        self.SetTopWindow(frame)

        print "Print statements go to this stdout window by default."

        frame.Show(True)
        return True
        
app = MyApp(redirect=True)
app.MainLoop()

