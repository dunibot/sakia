'''
Created on 2 févr. 2014

@author: inso
'''

import logging
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QMessageBox, QAction, QMenu, QInputDialog, QLineEdit
from ..models.members import MembersListModel
from ..gen_resources.community_tab_uic import Ui_CommunityTabWidget
from .add_contact import AddContactDialog
from .wot_tab import WotTabWidget
from .transfer import TransferMoneyDialog
from .certification import CertificationDialog
from ..tools.exceptions import PersonNotFoundError, NoPeerAvailable


class CommunityTabWidget(QWidget, Ui_CommunityTabWidget):

    '''
    classdocs
    '''

    def __init__(self, account, community, password_asker):
        '''
        Constructor
        '''
        super().__init__()
        self.setupUi(self)
        self.community = community
        self.account = account
        self.password_asker = password_asker
        self.list_community_members.setModel(MembersListModel(community))
        self.button_membership.disconnect()

        if self.account.member_of(self.community):
            self.button_membership.setText("Send leaving demand")
            self.button_membership.clicked.connect(self.send_membership_leaving)
        else:
            self.button_membership.setText("Send membership demand")
            self.button_membership.clicked.connect(self.send_membership_demand)

        self.tabs_information.addTab(WotTabWidget(account, community,
                                                  password_asker),
                                     QIcon(':/icons/wot_icon'),
                                     "Wot")

    def member_context_menu(self, point):
        index = self.list_community_members.indexAt(point)
        model = self.list_community_members.model()
        if index.row() < model.rowCount(None):
            member = model.members[index.row()]
            logging.debug(member)
            menu = QMenu(model.data(index, Qt.DisplayRole), self)

            add_contact = QAction("Add as contact", self)
            add_contact.triggered.connect(self.add_member_as_contact)
            add_contact.setData(member)

            send_money = QAction("Send money", self)
            send_money.triggered.connect(self.send_money_to_member)
            send_money.setData(member)

            certify = QAction("Certify identity", self)
            certify.triggered.connect(self.certify_member)
            certify.setData(member)

            menu.addAction(add_contact)
            menu.addAction(send_money)
            menu.addAction(certify)
            # Show the context menu.
            menu.exec_(self.list_community_members.mapToGlobal(point))

    def add_member_as_contact(self):
        dialog = AddContactDialog(self.account, self.window())
        person = self.sender().data()
        dialog.edit_name.setText(person.name)
        dialog.edit_pubkey.setText(person.pubkey)
        dialog.exec_()

    def send_money_to_member(self):
        dialog = TransferMoneyDialog(self.account, self.password_asker)
        person = self.sender().data()
        dialog.edit_pubkey.setText(person.pubkey)
        dialog.combo_community.setCurrentText(self.community.name())
        dialog.radio_pubkey.setChecked(True)
        dialog.exec_()

    def certify_member(self):
        dialog = CertificationDialog(self.account, self.password_asker)
        person = self.sender().data()
        dialog.edit_pubkey.setText(person.pubkey)
        dialog.radio_pubkey.setChecked(True)
        dialog.exec_()

    def send_membership_demand(self):
        password = self.password_asker.ask()
        if password == "":
            return

        try:
            self.account.send_membership(password, self.community, 'IN')
            QMessageBox.information(self, "Membership",
                                 "Success sending membership demand")
        except ValueError as e:
            QMessageBox.critical(self, "Join demand error",
                              str(e))
        except PersonNotFoundError as e:
            QMessageBox.critical(self, "Key not sent to community",
                              "Your key wasn't sent in the community. \
                              You can't request a membership.")
        except NoPeerAvailable as e:
            QMessageBox.critical(self, "Network error",
                                 "Couldn't connect to network : {0}".format(e),
                                 QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 "{0}".format(e),
                                 QMessageBox.Ok)

    def send_membership_leaving(self):
        password = self.password_asker.ask()
        if password == "":
            return

        try:
            self.account.send_membership(password, self.community, 'OUT')
            QMessageBox.information(self, "Membership",
                                 "Success sending leaving demand")
        except ValueError as e:
            QMessageBox.critical(self, "Leaving demand error",
                              e.message)
        except NoPeerAvailable as e:
            QMessageBox.critical(self, "Network error",
                                 "Couldn't connect to network : {0}".format(e),
                                 QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 "{0}".format(e),
                                 QMessageBox.Ok)

