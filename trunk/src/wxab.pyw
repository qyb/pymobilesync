#----------------------------------------------------------------------
# A very simple wxPython example.  Just a wx.Frame, wx.Panel,
# wx.StaticText, wx.Button, and a wx.BoxSizer, but it shows the basic
# structure of any wxPython application.
#----------------------------------------------------------------------

import wx

import util

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
        util.init()
        pb = util.sqlite_init('local')
        self.addrlist = pb.fetchall()
        pb.close()
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

        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnItemRightClick)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnModifyOne)
        self.Bind(wx.EVT_MENU, self.OnRemoveOne, id=301)
        self.Bind(wx.EVT_MENU, self.OnModifyOne, id=302)
        return

    def OnItemSelected(self, event):
        self.currentItem = event.m_itemIndex
        return
    
    def OnItemRightClick(self, event):
        self.currentItem = event.m_itemIndex
        menu = wx.Menu()
        menu.Append(301, "remove")
        menu.Append(302, "modify")
        self.PopupMenu(menu)
        menu.Destroy()
        return

    def OnModifyOne(self, event):
        dlg = ContactDialog(self, -1, "Modify", size=(350, 200), style = wx.DEFAULT_DIALOG_STYLE)
        dlg.setDict(self.addrlist[self.currentItem])
        dlg.showDlg()
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            #print dlg.GetValue()
            if dlg.VerifyInput() == True:
                self.updateAddr(dlg.GetValue())
            else:
                msgDlg = wx.MessageDialog(self, 'Need Name', 'Error',
                                          wx.OK | wx.ICON_INFORMATION #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                                          )
                msgDlg.ShowModal()
                msgDlg.Destroy()

        dlg.Destroy()
        return

    def OnRemoveOne(self, event):
        addr_entry = self.addrlist[self.currentItem]
        Msg = "Do you want remove the address entry of '%s %s' ?" % \
              (addr_entry[3], addr_entry[2])
        msgDlg = wx.MessageDialog(self, Msg, 'Confirm', wx.OK | wx.ICON_INFORMATION | wx.CANCEL)
        val = msgDlg.ShowModal()
        if val == wx.ID_OK:
            pb = util.sqlite_init('local')
            pb.delete(addr_entry[0])
            self.addrlist = pb.fetchall()
            pb.close()
            self.SetItemCount(len(self.addrlist))
            #print 1, self.addrlist[self.currentItem][0]

        msgDlg.Destroy()
        return

    def updateAddr(self, data):
        addr_entry = self.addrlist[self.currentItem]
        update_string = ''
        pb = util.sqlite_init('local')
        if data["First Name:"] != addr_entry[3]:
            update_string = pb.updateSQL(update_string, 'firstname', data["First Name:"])
        if data["Last Name:"] != addr_entry[2]:
            update_string = pb.updateSQL(update_string, 'surname', data["Last Name:"])
        if data["Home Phone:"] != addr_entry[6]:
            update_string = pb.updateSQL(update_string, 'home', data["Home Phone:"])
        if data["Work Phone:"] != addr_entry[7]:
            update_string = pb.updateSQL(update_string, 'work', data["Work Phone:"])
        if data["Mobile Phone:"] != addr_entry[5]:
            update_string = pb.updateSQL(update_string, 'mobile', data["Mobile Phone:"])
        if data["Email Addr:"] != addr_entry[4]:
            update_string = pb.updateSQL(update_string, 'email', data["Email Addr:"])
        if data["Title:"] != addr_entry[9]:
            update_string = pb.updateSQL(update_string, 'title', data["Title:"])
        if data["Organization:"] != addr_entry[10]:
            update_string = pb.updateSQL(update_string, 'org', data["Organization:"])
        if update_string != '':
            pb.update(addr_entry[0], update_string)
            self.addrlist = pb.fetchall()
        pb.close()
        self.RefreshItem(self.currentItem)
        return
    
    def insertAddr(self, data):
        pb = util.sqlite_init('local')
        pb.insert([data["Last Name:"], \
                        data["First Name:"], \
                        data["Email Addr:"], \
                        data["Mobile Phone:"], \
                        data["Home Phone:"], \
                        data["Work Phone:"], \
                        "", \
                        data["Organization:"], \
                        data["Title:"], \
                        "", \
                        ""])
        self.addrlist = pb.fetchall()
        pb.close()
        self.SetItemCount(len(self.addrlist))
        return

class ContactDialog(wx.Dialog):
    args_list = ["First Name:",
                 "Last Name:",
                 "Home Phone:",
                 "Work Phone:",
                 "Mobile Phone:",
                 "Email Addr:",
                 "Title:",
                 "Organization:"]


    def __init__(self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE
                 ):
        self.args_dict = {"First Name:":"",
                          "Last Name:":"",
                          "Home Phone:":"",
                          "Work Phone:":"",
                          "Mobile Phone:":"",
                          "Email Addr:":"",
                          "Title:":"",
                          "Organization:":""}
        self.textClist = []
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)

    def setDict(self, data):
        self.args_dict["First Name:"] = data[3]
        self.args_dict["Last Name:"] = data[2]
        self.args_dict["Home Phone:"] = data[6]
        self.args_dict["Work Phone:"] = data[7]
        self.args_dict["Mobile Phone:"] = data[5]
        self.args_dict["Email Addr:"] = data[4]
        self.args_dict["Title:"] = data[10]
        self.args_dict["Organization:"] = data[9]
        print data
        
    def showDlg(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        for arg in self.args_list:
            box = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self, -1, arg)
            box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            textCtrl = wx.TextCtrl(self, -1, self.args_dict[arg], size=(80,-1))
            self.textClist.append(textCtrl)
            box.Add(textCtrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
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
        for arg in self.args_list:
            ret[arg] = self.textClist[i].GetValue()
            i+=1
        return ret
    
    def VerifyInput(self):
        if self.textClist[0].GetValue() == '' and self.textClist[1].GetValue() == '':
            return False
        else:
            return True
        
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
        self.abTable = MyListCtrl(panel)
        sizer.Add(self.abTable, 0, wx.ALL, 0)
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
        dlg = ContactDialog(self, -1, "New Contact", size=(350, 200), style = wx.DEFAULT_DIALOG_STYLE)
        dlg.showDlg()
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            #print dlg.GetValue()
            if dlg.VerifyInput() == True:
                self.abTable.insertAddr(dlg.GetValue())
            else:
                msgDlg = wx.MessageDialog(self, 'Need Name', 'Error',
                                          wx.OK | wx.ICON_INFORMATION #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                                          )
                msgDlg.ShowModal()
                msgDlg.Destroy()

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

