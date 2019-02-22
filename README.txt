--------------------
Catalog Application.
--------------------
The files in this project run an application for logged-in users to add items
to a small martial arts supply catalog. Non logged-in users can view all
items but cannot change them. Logged-in users can only change items they
added themself but can view all items the same as non-logged in users.

---------------
Files Required.
---------------
This application was created on a Ubuntu VM using Vagrant and Oracle VM
VirtualBox. The VM was downloaded from Udacity for the Full Stack Web
Development program from Udacity.

The following files were created in addition to the VM described above.
The files should be in folder under the vagrant folder in the VM. This folder
can be named anything but the name catalog is suggested and was used during
development. In this folder there should be two sub-folders named static
and templates.

The catalog folder contains the following files:
catalog_datamodel.py      This file contains the classes needed to access and
                          manipulate the catalog.db. Do NOT RUN THIS
                          APPLICATION DIRECTLY in the Python interpreter. It
                          was used to create the initial catalog.db. It is still
                          needed now because it has the classes to manipulate
                          the catalog.db.

catalog.db                This file contains the catalog database. It comes
                          pre-seeded with six martial arts categories, each
                          category containing two items. A logged-in user can
                          add, edit, or delete items in the catalog.

catalog.py                This is the file that creates and runs the web server
                          for mainpulating the catalog. This is the main engine
                          for the application.

client_secrets.json       This file contains the JSON data needed to login and
                          out of the Google apis.

README.txt                The file you are reading now.

static/styles.css         This file contains the CSS styles used in the html
                          files in the templates folder.

templates/catalog.html    This file contains the html for the home page for
                          the application.

templates/category.html   This file contains the html for the category page
                          for the application. This page is displayed when the
                          user clicks a Category Name on the home page.

templates/deleteItem.html This file contains the html for deleting an item
                          in the database.

templates/editItem.html   This file contains the html for editing an item
                          in the database.

templates/header.html     This file contains the html for displaying the banner
                          at the top of each page.

templates/login.html      This file contains the html for logging in to the
                          Google API needed to login into this application.

templates/main.html       This file contains the html head and body framework
                          and tokens for Flask block content.

templates/newItem.html    This file contains the html adding a new item to the
                          database.

templates/showItem.html   This file contains the html for showing the details
                          of a specific item in the database.

--------
Credits.
--------
Much of the code was copied from the lessons in Module 3 of the Udacity
Full Stack Web Development course.

------------------------
RUNNING THE APPLICATION.
------------------------
To run this application login to the Vagrant VM and change to the
vagrant/catalog folder.

Run from the command prompt: python catalog.py

This will start a web server running on port 8000 on the local machine.

To access the application open a browser and navigate to:
http://localhost:8000/catalog or http://localhost:8000/

It is not necessary to login to the application to browse the catalog by
clicking on the various displayed links.

To add items, delete items, or edit items in the catalog you must login.
To login, click the Login link in the banner on any page. You must have
a Google account to login.

Once logged in, you can add items to the catalog by clicking the Add Item
link on the home page or the categories page.

You can only edit or delete items that you have added. You cannot delete
items added by other users.

To logout of the application click the Logout link in the banner on each page.
It is not necessary to logout of the application. You can simply close your
browser instead.

-- JSON ENDPOINTS --
There are four JSON endpoints in the application as follows:

To return every item in the entire catalog:
http://localhost:8000/catalog/JSON

To return a list of all categories:
http://localhost:8000/category/JSON

To return a list of items in a specific category (change the /4/ to the desired
category id (the example below returns items in category id 4 - Practice
Weapons):
http://localhost:8000/category/4/JSON

To return information on a specific item change the /6/ to the desired item id
(the example below returns information for item id 6 - Leg Guard):
http://localhost:8000/item/6/JSON

To end the web server press Ctrl+C in the command prompt running the python
application.
